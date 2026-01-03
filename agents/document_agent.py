from typing import Dict, Any, Optional
import os
import tempfile
from pathlib import Path
from agents.base_agent import BaseAgent
from tools.document_tool import DocumentTool
import logging
import re

logger = logging.getLogger(__name__)

class DocumentAgent(BaseAgent):
    """Agent 2: Document Understanding + Web Intelligence Agent"""
    
    def __init__(self, openai_api_key: Optional[str] = None, upload_dir: str = "static/uploads"):
        super().__init__(name="DocumentAgent", description="Handles document Q&A with web search fallback")
        self.document_tool = DocumentTool(openai_api_key)
        self.upload_dir = upload_dir
        self.current_document = None
        self.current_filename = None
        
        # Create upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
    
    def can_handle(self, query: str) -> bool:
        """Determine if this agent can handle the query"""
        query_lower = query.lower()
        document_keywords = [
            'document', 'pdf', 'file', 'upload', 'resume', 'cv',
            'policy', 'report', 'what does the document say',
            'based on the document', 'according to the file'
        ]
        
        # Also handle if user is asking about uploaded content
        if self.current_document:
            # If we have a document loaded, we can handle more queries
            general_question_keywords = ['what', 'how', 'when', 'where', 'who', 'why']
            if any(keyword in query_lower for keyword in general_question_keywords):
                return True
        
        return any(keyword in query_lower for keyword in document_keywords)
    
    async def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process document-related queries"""
        try:
            query_lower = query.lower()
            
            # Check if user wants to upload a document
            if 'upload' in query_lower or ('document' in query_lower and 'read' in query_lower):
                file_content = kwargs.get('file_content')
                filename = kwargs.get('filename')
                
                if file_content and filename:
                    return await self._handle_document_upload(file_content, filename, query)
                else:
                    return {
                        "success": False,
                        "error": "Please upload a document file",
                        "agent": self.name,
                        "instructions": "Use the /api/document/upload endpoint to upload a document first"
                    }
            
            # Check if we have a document loaded
            if not self.current_document:
                return {
                    "success": False,
                    "error": "No document loaded. Please upload a document first.",
                    "agent": self.name,
                    "suggestion": "Ask something like: 'Upload and read my resume' or use the upload endpoint"
                }
            
            # Process query against document
            return await self._handle_document_query(query)
            
        except Exception as e:
            logger.error(f"Error in DocumentAgent: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to process document query: {str(e)}",
                "agent": self.name
            }
    
    async def _handle_document_upload(self, file_content: bytes, filename: str, query: str) -> Dict[str, Any]:
        """Handle document upload and processing"""
        try:
            # Save file temporarily
            file_extension = Path(filename).suffix
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
            temp_file.write(file_content)
            temp_file.close()
            
            # Extract text from file
            text = self.document_tool.process_uploaded_file(temp_file.name, file_extension)
            
            # Create vector store
            success = self.document_tool.create_vector_store(text, filename)
            
            if success:
                self.current_document = text
                self.current_filename = filename
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                # Analyze document for common questions
                summary = self._analyze_document(text)
                
                response = (
                    f"✅ Document '{filename}' uploaded and processed successfully!\n\n"
                    f"**Document Summary:**\n{summary}\n\n"
                    f"You can now ask questions about this document. Examples:\n"
                    f"- What is the main content of this document?\n"
                    f"- What are the key points?\n"
                    f"- Specific questions based on the document content"
                )
                
                return {
                    "success": True,
                    "response": response,
                    "agent": self.name,
                    "document": filename,
                    "summary": summary,
                    "characters": len(text),
                    "pages": len(text.split('\n\n')) // 2  # Rough estimate
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to process document",
                    "agent": self.name
                }
                
        except Exception as e:
            logger.error(f"Error handling document upload: {str(e)}")
            return {
                "success": False,
                "error": f"Document processing error: {str(e)}",
                "agent": self.name
            }
    
    async def _handle_document_query(self, query: str) -> Dict[str, Any]:
        """Handle query against the loaded document"""
        try:
            # First, try to answer from document
            document_result = self.document_tool.query_document(query)
            
            if document_result["success"] and document_result["from_document"]:
                # Answer found in document
                response = (
                    f"**Based on the document '{self.current_filename}':**\n\n"
                    f"{document_result['answer']}\n\n"
                    f"*Source: {document_result['source']}*"
                )
                
                return {
                    "success": True,
                    "response": response,
                    "agent": self.name,
                    "from_document": True,
                    "confidence": document_result["confidence"],
                    "data": {
                        "answer": document_result["answer"],
                        "source": document_result["source"]
                    }
                }
            else:
                # Not found in document, fall back to web search
                logger.info(f"Question not answered from document, falling back to web search: {query}")
                return await self._handle_web_search(query)
                
        except Exception as e:
            logger.error(f"Error handling document query: {str(e)}")
            return {
                "success": False,
                "error": f"Query processing error: {str(e)}",
                "agent": self.name
            }
    
    async def _handle_web_search(self, query: str) -> Dict[str, Any]:
        """Handle web search fallback"""
        try:
            # Perform web search
            search_results = self.document_tool.web_search(query, num_results=3)
            
            if not search_results:
                response = (
                    f"I couldn't find an answer in the document and web search didn't return results.\n\n"
                    f"**Question:** {query}\n\n"
                    f"Please try:\n"
                    f"1. Rephrasing your question\n"
                    f"2. Asking about something in the uploaded document\n"
                    f"3. Uploading a different document"
                )
                
                return {
                    "success": False,
                    "response": response,
                    "agent": self.name,
                    "from_document": False,
                    "web_search_fallback": True,
                    "data": {"search_results": []}
                }
            
            # Format web search results
            response = (
                f"**I couldn't find this information in the document, but here's what I found online:**\n\n"
                f"**Question:** {query}\n\n"
            )
            
            for i, result in enumerate(search_results, 1):
                response += f"{i}. **{result['title']}**\n"
                response += f"   {result['snippet']}\n"
                response += f"   [Read more]({result['url']})\n\n"
            
            response += "*Note: This information is from web search, not from your uploaded document.*"
            
            return {
                "success": True,
                "response": response,
                "agent": self.name,
                "from_document": False,
                "web_search_fallback": True,
                "confidence": 0.7,
                "data": {
                    "search_results": search_results,
                    "answer_source": "web_search"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in web search: {str(e)}")
            response = f"Error performing web search: {str(e)}"
            
            return {
                "success": False,
                "response": response,
                "agent": self.name,
                "from_document": False,
                "web_search_fallback": False
            }
    
    def _analyze_document(self, text: str) -> str:
        """Analyze document content and generate summary"""
        # Simple analysis - can be enhanced
        lines = text.split('\n')
        words = text.split()
        
        # Count sections (based on common patterns)
        sections = []
        common_section_keywords = ['education', 'experience', 'skills', 'summary', 'objective', 
                                  'policy', 'procedure', 'guideline', 'introduction', 'conclusion']
        
        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in common_section_keywords) and len(line) < 100:
                sections.append(line.strip())
        
        # Generate summary
        summary = f"Document contains approximately {len(words)} words.\n"
        
        if sections:
            summary += f"Detected sections: {', '.join(sections[:5])}"
            if len(sections) > 5:
                summary += f" and {len(sections) - 5} more."
        
        # Extract first few lines as preview
        preview_lines = [line.strip() for line in lines[:10] if line.strip()]
        if preview_lines:
            summary += f"\n\n**Preview:**\n" + "\n".join(preview_lines[:5]) + "..."
        
        return summary
    
    def clear_document(self):
        """Clear currently loaded document"""
        self.current_document = None
        self.current_filename = None
        self.document_tool.vector_store = None
        self.document_tool.documents = []
        logger.info("Cleared current document")