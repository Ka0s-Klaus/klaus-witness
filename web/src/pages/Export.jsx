import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../store/auth'
import { Download, CheckCircle } from 'lucide-react'
import axios from 'axios'

export default function Export() {
  const { token } = useAuthStore()
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    fetchSummary()
  }, [token])

  const fetchSummary = async () => {
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
      const response = await axios.get(`${API_URL}/export/summary`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setSummary(response.data)
    } catch (err) {
      console.error('Error fetching summary:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    setExporting(true)
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
      const response = await axios.get(`${API_URL}/export/download`, {
        headers: { Authorization: `Bearer ${token}` }
      })

      const element = document.createElement('a')
      const file = new Blob([response.data.data], { type: 'application/json' })
      element.href = URL.createObjectURL(file)
      element.download = response.data.filename
      document.body.appendChild(element)
      element.click()
      document.body.removeChild(element)
    } catch (err) {
      console.error('Error exporting:', err)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Exportar mis datos</h1>

        {/* Summary */}
        {!loading && summary && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8">
            <h2 className="text-2xl font-bold mb-6">Tu archivo personal</h2>

            <div className="grid sm:grid-cols-3 gap-4 mb-8">
              {[
                { label: 'Eventos', value: summary.total_events },
                { label: 'Creencias', value: summary.total_memories },
                { label: 'Personas', value: summary.total_personas }
              ].map((item, i) => (
                <div key={i} className="bg-slate-700 rounded p-4 text-center">
                  <div className="text-3xl font-bold text-amber-400">{item.value}</div>
                  <div className="text-slate-300 text-sm">{item.label}</div>
                </div>
              ))}
            </div>

            <button
              onClick={handleExport}
              disabled={exporting}
              className="w-full bg-amber-500 hover:bg-amber-600 text-black font-bold py-3 rounded transition disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Download size={20} />
              {exporting ? 'Exportando...' : 'Descargar JSON'}
            </button>
          </motion.div>
        )}

        {/* Info */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-slate-800 border border-slate-700 rounded-lg p-6 space-y-4">
          <h3 className="text-xl font-bold">Tu derecho a la portabilidad</h3>

          <div className="space-y-3 text-slate-300">
            <div className="flex gap-3">
              <CheckCircle className="text-amber-400 flex-shrink-0" size={20} />
              <p>Puedes exportar tus datos en cualquier momento</p>
            </div>
            <div className="flex gap-3">
              <CheckCircle className="text-amber-400 flex-shrink-0" size={20} />
              <p>Sin costos, sin restricciones, sin caducidad</p>
            </div>
            <div className="flex gap-3">
              <CheckCircle className="text-amber-400 flex-shrink-0" size={20} />
              <p>Formato JSON legible y estructurado</p>
            </div>
            <div className="flex gap-3">
              <CheckCircle className="text-amber-400 flex-shrink-0" size={20} />
              <p>Incluye tu historia completa: eventos, creencias, personas</p>
            </div>
            <div className="flex gap-3">
              <CheckCircle className="text-amber-400 flex-shrink-0" size={20} />
              <p>Aunque TESTIGO desaparezca, tu archivo sobrevive</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
