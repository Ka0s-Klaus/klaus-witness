import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import axios from 'axios'

export default function Auth() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [isSignup, setIsSignup] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    first_name: '',
    last_name: ''
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

      if (isSignup) {
        const response = await axios.post(`${API_URL}/auth/signup`, {
          email: formData.email,
          username: formData.username,
          first_name: formData.first_name,
          last_name: formData.last_name
        })

        setAuth(response.data.token, response.data.user_id, response.data)
      } else {
        const response = await axios.post(`${API_URL}/auth/login`, {
          email: formData.email,
          password: formData.password
        })

        setAuth(response.data.token, response.data.user_id, response.data)
      }

      navigate('/onboarding')
    } catch (err) {
      setError(err.response?.data?.detail || 'Error en autenticación')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8">
          <h1 className="text-3xl font-bold text-amber-400 mb-2 text-center">TESTIGO</h1>
          <p className="text-slate-400 text-center mb-8">Memoria que dura</p>

          <div className="flex gap-4 mb-8">
            <button
              onClick={() => setIsSignup(true)}
              className={`flex-1 py-2 rounded font-semibold transition ${
                isSignup
                  ? 'bg-amber-500 text-black'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Registrarse
            </button>
            <button
              onClick={() => setIsSignup(false)}
              className={`flex-1 py-2 rounded font-semibold transition ${
                !isSignup
                  ? 'bg-amber-500 text-black'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Ingresar
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {isSignup && (
              <>
                <input
                  type="text"
                  name="first_name"
                  placeholder="Nombre"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                  className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:border-amber-400 outline-none"
                />
                <input
                  type="text"
                  name="last_name"
                  placeholder="Apellido"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                  className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:border-amber-400 outline-none"
                />
                <input
                  type="text"
                  name="username"
                  placeholder="Usuario"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:border-amber-400 outline-none"
                />
              </>
            )}

            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:border-amber-400 outline-none"
            />

            <input
              type="password"
              name="password"
              placeholder="Contraseña"
              value={formData.password}
              onChange={handleChange}
              required
              className="w-full bg-slate-700 text-white px-4 py-2 rounded border border-slate-600 focus:border-amber-400 outline-none"
            />

            {error && (
              <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-2 rounded text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-amber-500 hover:bg-amber-600 text-black font-bold py-2 rounded transition disabled:opacity-50"
            >
              {loading ? 'Procesando...' : (isSignup ? 'Crear cuenta' : 'Ingresar')}
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  )
}
