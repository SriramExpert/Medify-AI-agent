import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! I am Medify, your Agentic AI assistant. How can I help you today?' }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [agents, setAgents] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const fileInputRef = useRef(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    try {
      const response = await fetch('/api/agents')
      const data = await response.json()
      setAgents(data || [])
    } catch (error) {
      console.error('Error fetching agents:', error)
    }
  }

  const handleSend = async () => {
    if (!input.trim()) return

    const userMsg = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input })
      })

      const data = await response.json()

      // Use the response field if present; otherwise show the full JSON payload for debugging
      const aiResponse = data.response ?? JSON.stringify(data, null, 2) ?? "I processed your request but didn't get a specific text response."
      setMessages(prev => [...prev, { role: 'ai', content: aiResponse, agent: data.agent }])
    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', content: 'Sorry, I encountered an error while processing your request.' }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    setIsUploading(true)
    setUploadStatus('Uploading...')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/document/upload', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()

      if (data.success) {
        setMessages(prev => [...prev, {
          role: 'ai',
          content: `✅ Document '${file.name}' uploaded successfully!\n\n${data.summary || ''}`,
          agent: 'DocumentAgent'
        }])
        setUploadStatus('Success!')
      } else {
        setUploadStatus('Upload failed')
        setMessages(prev => [...prev, { role: 'ai', content: `❌ Upload failed: ${data.detail || data.error || 'Unknown error'}` }])
      }
    } catch (error) {
      console.error('Error uploading document:', error)
      setUploadStatus('Error')
      setMessages(prev => [...prev, { role: 'ai', content: '❌ Error uploading document. Is the backend running?' }])
    } finally {
      setIsUploading(false)
      // Reset file input
      if (fileInputRef.current) fileInputRef.current.value = ''
      setTimeout(() => setUploadStatus(null), 3000)
    }
  }

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="sidebar-header">Medify AI</div>
        <div className="agent-status-list">
          <h3>Active Agents</h3>
          {agents.length > 0 ? (
            agents.map((agent, i) => (
              <div key={i} className="agent-item">
                <div className="status-indicator"></div>
                <span>{agent.name}</span>
              </div>
            ))
          ) : (
            <>
              <div className="agent-item"><div className="status-indicator"></div><span>Weather Agent</span></div>
              <div className="agent-item"><div className="status-indicator"></div><span>DB Agent</span></div>
              <div className="agent-item"><div className="status-indicator"></div><span>Meeting Agent</span></div>
            </>
          )}
        </div>
      </aside>

      <main className="chat-area">
        <div className="messages-container">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              {msg.agent && <div style={{ fontSize: '0.7rem', opacity: 0.7, marginBottom: '4px' }}>[{msg.agent}]</div>}
              {msg.content}
            </div>
          ))}
          {isLoading && (
            <div className="message ai">
              <div className="loading-dots">
                <span>.</span><span>.</span><span>.</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <div className="input-box">
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              onChange={handleFileUpload}
              accept=".pdf,.txt,.docx"
            />
            <button
              className="upload-button"
              onClick={() => fileInputRef.current.click()}
              disabled={isUploading || isLoading}
              title="Upload Document"
            >
              {isUploading ? '...' : '📎'}
            </button>
            <input
              type="text"
              placeholder="Ask anything (e.g., weather, documents)..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button className="send-button" onClick={handleSend} disabled={isLoading || isUploading}>
              Send
            </button>
          </div>
          {uploadStatus && <div className="upload-indicator">{uploadStatus}</div>}
        </div>
      </main>
    </div>
  )
}

export default App
