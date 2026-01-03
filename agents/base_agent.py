from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def can_handle(self, query: str) -> bool:
        """Check if this agent can handle the query"""
        pass
    
    @abstractmethod
    async def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process the query and return response"""
        pass
    
    def get_info(self) -> Dict[str, str]:
        """Get agent information"""
        return {
            "name": self.name,
            "description": self.description
        }