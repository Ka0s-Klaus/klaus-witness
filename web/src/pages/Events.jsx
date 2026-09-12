import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../store/auth'
import { Heart } from 'lucide-react'
import axios from 'axios'

export default function Events() {
  const { token } = useAuthStore()
  const [events, setEvents] = useState([])
  const [formData, setFormData] = useState({ tipo: 'hecho', contenido: '' })
  const [loading, setLoading] = useState(false)

  const eventTypes = [
    { value: 'decision', label: 'Decisión' },
    { value: 'emotion', label: 'Emoción' },
    { value: 'fact', label: 'Hecho' },
    { value: 'reflection', label: 'Reflexión' },
    { value: 'hito_vital', label: 'Hito Vital' }
  ]

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.contenido.trim()) return

    setLoading(true)
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
      await axios.post(`${API_URL}/events/`, {
        tipo: formData.tipo,
        contenido: formData.contenido,
        contexto: { lugar: '', etapa_vital: '' },
        peso_emocional: 0.5,
        consentimiento: { nivel: 'personal' }
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })

      setFormData({ tipo: 'hecho', contenido: '' })
      fetchEvents()
    } catch (err) {
      console.error('Error creating event:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchEvents = async () => {
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
      const response = await axios.get(`${API_URL}/events/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setEvents(response.data.events || [])
    } catch (err) {
      console.error('Error fetching events:', err)
    }
  }

  useEffect(() => {
    fetchEvents()
  }, [token])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Mis Eventos</h1>

        {/* Form */}
        <motion.form initial={{ opacity: 0 }} animate={{ opacity: 1 }} onSubmit={handleSubmit} className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-8">
          <div className="mb-4">
            <label className="block text-sm font-semibold mb-2">Tipo de evento</label>
            <select
              value={formData.tipo}
              onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
              className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-amber-400 outline-none"
            >
              {eventTypes.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-semibold mb-2">¿Qué pasó?</label>
            <textarea
              value={formData.contenido}
              onChange={(e) => setFormData({ ...formData, contenido: e.target.value })}
              placeholder="Cuéntame sobre este momento..."
              rows="4"
              className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-amber-400 outline-none resize-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-amber-500 hover:bg-amber-600 text-black font-bold py-2 rounded transition disabled:opacity-50"
          >
            {loading ? 'Guardando...' : 'Registrar evento'}
          </button>
        </motion.form>

        {/* List */}
        <div className="space-y-4">
          {events.map((event, i) => (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-slate-800 border border-slate-700 rounded-lg p-4"
            >
              <div className="flex items-start gap-3 mb-2">
                <Heart size={18} className="text-amber-400 mt-1" />
                <div>
                  <h3 className="font-semibold">{event.tipo}</h3>
                  <p className="text-xs text-slate-400">{new Date(event.timestamp).toLocaleDateString('es')}</p>
                </div>
              </div>
              <p className="text-slate-300">{event.contenido}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
