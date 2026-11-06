---
tags: [proyecto/klaus-witness, tipo/guia, agente/desarrollo]
---

# 📚 Guía de Estilo de Documentación

Este documento define el estándar de formato para toda la documentación del proyecto **Klaus-witness (TESTIGO)** a partir de septiembre 2026.

## 🎯 Estructura de README.md

### Portada
```markdown
# 🧠 Nombre del Proyecto v1.0.0

> **Tagline en negrita.** Contexto adicional.

[![Badge1](url)](url) [![Badge2](url)](url)

---
```

### Sección: "¿Qué hago? ¿Cómo lo hago? ¿Y para qué lo hago?"
```markdown
## 🤔 ¿Qué hago? ¿Cómo lo hago? ¿Y para qué lo hago?

**¿Qué hago:** [Descripción del proyecto]
**¿Cómo lo hago:** [Técnica/Arquitectura]
**¿Para qué lo hago:** [Problema que resuelve]

---
```

### Características
```markdown
## ✨ Características v1.0.0

- 📝 **Feature 1:** Descripción breve
- 🧠 **Feature 2:** Descripción breve
- 💬 **Feature 3:** Descripción breve

---
```

### Instalación rápida
```markdown
## 🚀 Instalación rápida

### Requisitos
- Docker + Docker Compose
- (Opcional: Python 3.12, Node.js 20)
- API key de Anthropic

### Pasos

\`\`\`bash
git clone <repo>
cd project
cp .env.example .env
nano .env              # Editar ANTHROPIC_API_KEY
docker-compose up
\`\`\`

### URLs

| URL | Servicio |
|---|---|
| http://localhost:8000 | API REST |
| http://localhost:3000 | Frontend |
| http://localhost:8000/docs | Docs |

---
```

### Principios
```markdown
## 🔑 Principios (No Negociables)

1. **La memoria sobrevive al modelo.**
2. **Texto legible = fuente de verdad.**
3. **Nunca borrar, solo superponer.**
4. **Consentimiento viaja con el dato.**
5. **Exportable siempre.**

---
```

### Arquitectura
```markdown
## 🏗️ Arquitectura

\`\`\`mermaid
graph TD
    REACT["🎨 Frontend (React)"]
    API["📡 API (FastAPI)"]
    DB["🗄️ PostgreSQL"]
    QUEUE["⚡ Celery + Redis"]
    LLM["🧠 Claude"]
    
    REACT --> API
    API --> DB
    API --> QUEUE
    QUEUE --> LLM
\`\`\`

**Stack:**
- 🎨 Frontend: React 18 + Tailwind
- 📡 API: FastAPI + Python 3.12
- 🗄️ BD: PostgreSQL 16+
- ⚡ Jobs: Celery + Redis
- 🧠 LLM: Claude Anthropic

---
```

### Documentación
```markdown
## 📚 Documentación

| Doc | Contenido |
|---|---|
| [🚀 Instalación](docs/INSTALACION.md) | Setup detallado |
| [🏗️ Arquitectura](docs/ARQUITECTURA.md) | Diseño técnico |
| [📡 API](docs/API.md) | Endpoints y esquemas |
| [📝 Cambios](docs/CAMBIOS.md) | Historial de versiones |

---
```

### Desarrollo
```markdown
## 🛠️ Desarrollo

### Backend
\`\`\`bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
\`\`\`

### Frontend
\`\`\`bash
cd web
npm install
npm run dev
\`\`\`

### Tests
\`\`\`bash
pytest tests/ --cov=api,core
\`\`\`

---
```

### Seguridad
```markdown
## 🔐 Seguridad y Privacidad

✅ Cifrado AES-256 en reposo
✅ TLS 1.3 en tránsito
✅ Consentimiento granular por evento
✅ Revocación sin borrado (auditoría preservada)
✅ Menor privilegio en procesos
✅ GDPR-first: portabilidad como principio

---
```

### Status
```markdown
## 📊 Status v1.0.0

| Componente | Status | Nota |
|---|---|---|
| 📝 Ingest de eventos | ✅ v1.0 | Producción |
| 🧠 Memoria semántica | ✅ v1.0 | Producción |
| 🔄 Consolidador | ✅ v1.0 | Cron diaria |
| 💬 Conversación | ✅ v1.0 | Con inyección de memoria |
| 📤 Export | ✅ v1.0 | JSON legible |
| 🔌 Extensiones | 📋 v1.1 | Diseño completado |

---
```

### Contribuir
```markdown
## 🤝 Contribuciones

1. Fork
2. Rama: `git checkout -b feature/amazing`
3. Commit: `git commit -m "Add feature"`
4. Push y PR

---

## 📄 Licencia

[MIT](LICENSE) — Libre para uso comercial.

© 2026 TESTIGO Contributors
```

## 🎨 Emojis estándar

| Sección | Emoji |
|---|---|
| Título | 🧠 (específico) |
| ¿Qué? | 🤔 |
| Características | ✨ |
| Instalación | 🚀 |
| Principios | 🔑 |
| Arquitectura | 🏗️ |
| Documentación | 📚 |
| Desarrollo | 🛠️ |
| Seguridad | 🔐 |
| Status | 📊 |
| Contribuir | 🤝 |
| Licencia | 📄 |

## ✅ Checklist

- [ ] Portada con emoji + tagline + badges
- [ ] Sección "¿Qué? ¿Cómo? ¿Para qué?"
- [ ] Características con emojis
- [ ] Separadores `---`
- [ ] Instalación con requisitos
- [ ] URLs claras para acceso
- [ ] Principios o valores del proyecto
- [ ] Arquitectura con Flowchart Mermaid
- [ ] Documentación: tabla con links
- [ ] Desarrollo: comandos por componente
- [ ] Seguridad: checklist de features
- [ ] Status: tabla con versión actual
- [ ] Contribuir: pasos claros
- [ ] Licencia MIT
- [ ] Créditos (si aplica)

## 📝 Ver README.md como referencia aplicada.
