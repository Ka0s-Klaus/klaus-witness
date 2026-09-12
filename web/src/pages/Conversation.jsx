import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../store/auth'
import { Send } from 'lucide-react'
import axios from 'axios'

export default function Conversation() {
  const { token } = useAuthStore()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
      const response = await axios.post(`${API_URL}/conversation/chat`, {
        content: input
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        citations: response.data.citations
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      console.error('Error sending message:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex flex-col">
      <div className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <h1 className="text-2xl font-bold text-white">Conversación conmigo</h1>
        <p className="text-slate-400 text-sm">Habla con tu yo basado en tu historia</p>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center text-slate-400">
              <p className="mb-4">Comienza a conversar contigo mismo</p>
              <p className="text-sm">Usa tu memoria personal como guía</p>
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-amber-500 text-black'
                  : 'bg-slate-700 text-slate-100'
              }`}
            >
              <p>{msg.content}</p>
              {msg.citations && (
                <p className="text-xs mt-2 opacity-60">
                  Basado en {msg.citations.retrieved_count} memorias
                </p>
              )}
            </div>
          </motion.div>
        ))}

        {loading && (
          <motion.div animate={{ opacity: [0.5, 1] }} className="flex justify-start">
            <div className="bg-slate-700 px-4 py-3 rounded-lg">
              <p className="text-slate-300">Pensando...</p>
            </div>
          </motion.div>
        )}

        <div ref={endRef} />
      </div>

      <div className="bg-slate-800 border-t border-slate-700 px-6 py-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Pregunta sobre ti..."
            className="flex-1 bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:border-amber-400 outline-none"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="bg-amber-500 hover:bg-amber-600 text-black p-2 rounded transition disabled:opacity-50"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  )
}
