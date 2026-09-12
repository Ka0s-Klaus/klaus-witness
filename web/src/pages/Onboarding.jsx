import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { CheckCircle } from 'lucide-react'

export default function Onboarding() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)

  const steps = [
    { title: 'Bienvenido a TESTIGO', desc: 'Tu archivo personal para la vida' },
    { title: 'Consentimiento', desc: 'Controlas qué compartir y con quién' },
    { title: 'Privacidad', desc: 'Tus datos están cifrados y son tuyos' },
    { title: 'Comenzar', desc: 'Listo para registrar tu historia' }
  ]

  const handleNext = () => {
    if (step < steps.length) setStep(step + 1)
    else navigate('/dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4">
      <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="max-w-lg w-full">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-amber-400 mb-2">TESTIGO</h1>
            <h2 className="text-2xl font-bold text-white mb-4">{steps[step - 1].title}</h2>
            <p className="text-slate-400 text-lg">{steps[step - 1].desc}</p>
          </div>

          <div className="mb-8 space-y-4">
            {step === 1 && (
              <div className="space-y-3 text-slate-300">
                <p>TESTIGO es tu testigo personal: acompaña tu vida durante años, registra quién eres y aprende de ti.</p>
                <p>Con el tiempo, podrás conversar con tu "yo futuro" basado en tu historia real.</p>
              </div>
            )}
            {step === 2 && (
              <div className="space-y-3 text-slate-300">
                <p><strong className="text-amber-400">✓</strong> Tú controlas el acceso a cada evento</p>
                <p><strong className="text-amber-400">✓</strong> Puedes revocar el consentimiento en cualquier momento</p>
                <p><strong className="text-amber-400">✓</strong> La IA solo ve lo que apruebes</p>
              </div>
            )}
            {step === 3 && (
              <div className="space-y-3 text-slate-300">
                <p><strong className="text-amber-400">✓</strong> Cifrado AES-256 en reposo</p>
                <p><strong className="text-amber-400">✓</strong> TLS 1.3 en tránsito</p>
                <p><strong className="text-amber-400">✓</strong> Exportable siempre, sin costo</p>
              </div>
            )}
            {step === 4 && (
              <div className="space-y-3 text-slate-300">
                <p className="text-lg">Estás listo para comenzar a registrar tu historia.</p>
                <p>Ve a "Mis Eventos" para crear tu primer registro.</p>
              </div>
            )}
          </div>

          {/* Progress */}
          <div className="mb-8 flex gap-2">
            {steps.map((_, i) => (
              <div
                key={i}
                className={`h-2 flex-1 rounded transition ${
                  i < step ? 'bg-amber-400' : 'bg-slate-600'
                }`}
              />
            ))}
          </div>

          <button
            onClick={handleNext}
            className="w-full bg-amber-500 hover:bg-amber-600 text-black font-bold py-3 rounded transition"
          >
            {step < steps.length ? 'Siguiente' : 'Ir a Dashboard'}
          </button>
        </div>
      </motion.div>
    </div>
  )
}
