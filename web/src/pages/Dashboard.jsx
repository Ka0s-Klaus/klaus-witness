import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import { Heart, Brain, LogOut, BookOpen, Users, Download, Sparkles } from 'lucide-react'
import axios from 'axios'

export default function Dashboard() {
  const navigate = useNavigate()
  const { logout, token, user } = useAuthStore()
  const [stats, setStats] = useState({ events: 0, memories: 0, personas: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [token])

  const fetchStats = async () => {
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
      const response = await axios.get(`${API_URL}/export/summary`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setStats({
        events: response.data.total_events,
        memories: response.data.total_memories,
        personas: response.data.total_personas
      })
    } catch (err) {
      console.error('Error fetching stats:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const menuItems = [
    { title: 'Mis Eventos', desc: 'Registra tu vida', icon: <Heart />, to: '/events' },
    { title: 'Conversación', desc: 'Habla contigo mismo', icon: <Brain />, to: '/conversation' },
    { title: 'Mi Yo Futuro', desc: 'Explora escenarios', icon: <Sparkles />, to: '/future-self' },
    { title: 'Exportar Datos', desc: 'Descarga tu historia', icon: <Download />, to: '/export' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-amber-400">TESTIGO</h1>
        <button onClick={handleLogout} className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded transition">
          <LogOut size={18} />
          Salir
        </button>
      </header>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Welcome */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h2 className="text-4xl font-bold mb-2">Bienvenido de vuelta</h2>
          <p className="text-slate-400 mb-12">Tu memoria personal te espera</p>
        </motion.div>

        {/* Stats */}
        {!loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="grid sm:grid-cols-3 gap-4 mb-12">
            {[
              { label: 'Eventos', value: stats.events },
              { label: 'Creencias', value: stats.memories },
              { label: 'Personas', value: stats.personas }
            ].map((stat, i) => (
              <motion.div key={i} whileHover={{ y: -4 }} className="bg-slate-800 border border-slate-700 rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-amber-400 mb-2">{stat.value}</div>
                <div className="text-slate-400">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* Menu */}
        <div className="grid sm:grid-cols-2 gap-6">
          {menuItems.map((item, i) => (
            <motion.button
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              whileHover={{ y: -8 }}
              onClick={() => navigate(item.to)}
              className="bg-slate-800 border border-slate-700 rounded-lg p-8 text-left hover:border-amber-400 hover:bg-slate-700/50 transition group"
            >
              <div className="text-amber-400 mb-4 group-hover:scale-110 transition">{item.icon}</div>
              <h3 className="text-xl font-bold mb-2">{item.title}</h3>
              <p className="text-slate-400">{item.desc}</p>
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  )
}
