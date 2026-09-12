import React from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Sparkles, Heart, Brain, Archive } from 'lucide-react'

export default function Landing() {
  const navigate = useNavigate()

  const features = [
    {
      icon: <Heart className="w-8 h-8" />,
      title: "Tu Memoria Importa",
      desc: "Registra los momentos que definen tu vida. Cada decisión, cada emoción cuenta."
    },
    {
      icon: <Brain className="w-8 h-8" />,
      title: "Aprende de Ti Mismo",
      desc: "La IA consolida tus experiencias en patrones y creencias. Descubre quién eres realmente."
    },
    {
      icon: <Sparkles className="w-8 h-8" />,
      title: "Conversa con Tu Yo Futuro",
      desc: "Explora escenarios posibles. Habla con la versión que podrías ser en 5 años."
    },
    {
      icon: <Archive className="w-8 h-8" />,
      title: "Tus Datos Son Tuyos",
      desc: "Exporta siempre, sin costo. Puedes llevarte tu historia completa cuando quieras."
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 opacity-20">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))]"></div>
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <header className="flex justify-between items-center px-6 sm:px-12 py-6">
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-amber-200 to-amber-400 bg-clip-text text-transparent"
          >
            TESTIGO
          </motion.h1>
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onClick={() => navigate('/auth')}
            className="px-6 py-2 bg-amber-500 hover:bg-amber-600 text-black rounded-lg font-semibold transition"
          >
            Comenzar
          </motion.button>
        </header>

        {/* Hero */}
        <section className="max-w-6xl mx-auto px-6 py-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12"
          >
            <h2 className="text-5xl sm:text-6xl font-bold mb-6 leading-tight">
              La única app que se vuelve más valiosa cuanto más vieja es
            </h2>
            <p className="text-xl text-slate-300 mb-8 max-w-3xl mx-auto">
              TESTIGO es tu archivo personal. Acompaña tu vida durante años, aprende quién eres y te permite conversar con tu yo futuro.
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/auth')}
              className="px-8 py-4 bg-gradient-to-r from-amber-400 to-amber-500 text-black rounded-lg font-bold text-lg hover:shadow-lg transition"
            >
              Crear cuenta gratis
            </motion.button>
          </motion.div>

          {/* Features Grid */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="grid sm:grid-cols-2 gap-6 my-20"
          >
            {features.map((feature, i) => (
              <motion.div
                key={i}
                whileHover={{ y: -8 }}
                className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6"
              >
                <div className="text-amber-400 mb-3">{feature.icon}</div>
                <h3 className="text-lg font-bold mb-2">{feature.title}</h3>
                <p className="text-slate-300">{feature.desc}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* Principles */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="bg-slate-800/30 backdrop-blur border border-slate-700 rounded-lg p-8 mt-16"
          >
            <h3 className="text-2xl font-bold mb-6">7 Principios que nos guían</h3>
            <div className="grid sm:grid-cols-2 gap-4 text-slate-300">
              <div><strong className="text-amber-400">✓</strong> La memoria sobrevive al modelo</div>
              <div><strong className="text-amber-400">✓</strong> Todo es texto legible (no formatos cerrados)</div>
              <div><strong className="text-amber-400">✓</strong> Nunca borramos, solo archivamos</div>
              <div><strong className="text-amber-400">✓</strong> Tu consentimiento viaja con el dato</div>
              <div><strong className="text-amber-400">✓</strong> Puedes exportar en cualquier momento</div>
              <div><strong className="text-amber-400">✓</strong> La IA propone, tú decides</div>
              <div className="sm:col-span-2"><strong className="text-amber-400">✓</strong> Aunque TESTIGO desaparezca, tu archivo sobrevive</div>
            </div>
          </motion.div>
        </section>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-700 mt-16 py-8 text-center text-slate-400">
        <p>TESTIGO v1.0.0 | Memoria que dura • Desarrollado con IA, 100% funcional</p>
      </footer>
    </div>
  )
}
