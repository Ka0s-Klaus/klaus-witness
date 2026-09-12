import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../store/auth'
import { Sparkles } from 'lucide-react'
import axios from 'axios'
import Markdown from 'react-markdown'

export default function FutureSelf() {
  const { token } = useAuthStore()
  const [scenario, setScenario] = useState('tendencial')
  const [yearsAhead, setYearsAhead] = useState(5)
  const [monologue, setMonologue] = useState('')
  const [loading, setLoading] = useState(false)

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
      const response = await axios.post(`${API_URL}/persona/future-self`, {
        scenario_type: scenario,
        years_ahead: yearsAhead
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })

      setMonologue(response.data.monologue)
    } catch (err) {
      console.error('Error generating scenario:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">Mi Yo Futuro</h1>
        <p className="text-slate-400 mb-8">Explora quién podrías ser en diferentes escenarios</p>

        {/* Controls */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-8">
          <div className="grid sm:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-semibold mb-2">Años en el futuro</label>
              <input
                type="range"
                min="1"
                max="20"
                value={yearsAhead}
                onChange={(e) => setYearsAhead(parseInt(e.target.value))}
                className="w-full"
              />
              <p className="text-amber-400 font-bold text-lg mt-2">{yearsAhead} años</p>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Tipo de escenario</label>
              <select
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
                className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-amber-400 outline-none"
              >
                <option value="tendencial">Tendencial (tu camino natural)</option>
                <option value="optimista">Optimista (mejor versión)</option>
                <option value="arrepentimiento">Arrepentimiento (reflexión)</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading}
            className="w-full bg-gradient-to-r from-amber-400 to-amber-500 text-black font-bold py-3 rounded transition disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Sparkles size={20} />
            {loading ? 'Generando escenario...' : 'Generar escenario'}
          </button>
        </motion.div>

        {/* Monologue */}
        {monologue && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-slate-800 border border-slate-700 rounded-lg p-8">
            <div className="prose prose-invert max-w-none">
              <Markdown>{monologue}</Markdown>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
