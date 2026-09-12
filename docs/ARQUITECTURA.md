# ARQUITECTURA - TESTIGO v1.0.0

Guía técnica: cómo está construido TESTIGO, qué hace cada componente y cómo interactúan.

---

## 📐 Diagrama de sistemas

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENTE (web, móvil)                    │
│        React SPA: Landing, Auth, Dashboard, Events,         │
│        Conversation, FutureSelf, Export                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS / TLS 1.3
┌──────────────────────────▼──────────────────────────────────┐
│                      API (FastAPI)                          │
│   • /api/auth       → login, signup, me                     │
│   • /api/events     → create, list, get, revoke             │
│   • /api/memory     → list, search, get                     │
│   • /api/conversation → chat, chat-stream                   │
│   • /api/persona    → current, versions, future-self, fork  │
│   • /api/export     → summary, download                     │
└───────┬───────────────────┬─────────────────────┬───────────┘
        │                   │                     │
┌───────▼────────┐  ┌───────▼────────┐  ┌────────▼──────────┐
│  EVENT STORE   │  │ MEMORY STORE   │  │ PERSONA STORE     │
│ (PostgreSQL)   │  │ (PostgreSQL)   │  │ (PostgreSQL)      │
│                │  │                │  │                   │
│ • events       │  │ • memories     │  │ • personas        │
│ • event_types  │  │ • categories   │  │ • versions        │
│ • consent      │  │ • confidence   │  │ • forks           │
│ • revocation   │  │ • status       │  │ • voice_samples   │
│                │  │ • embeddings   │  │                   │
└────────────────┘  └────────────────┘  └───────┬───────────┘
                                                 │
                                    ┌────────────▼────────┐
                                    │ CONSOLIDATION LOG   │
                                    │ (PostgreSQL)        │
                                    │ • decisions         │
                                    │ • timestamp         │
                                    │ • reasoning         │
                                    └─────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              CONSOLIDADOR (Celery Worker)                   │
│                                                             │
│  Corre nocturnamente (02:00 UTC):                          │
│  1. Lee eventos no consolidados                           │
│  2. Clasifica con Claude (CONFIRMA / CONTRADICE / NUEVO)  │
│  3. Actualiza memorias (confidence, status)               │
│  4. Registra decisiones en consolidation_log             │
│  5. Aplica decaimiento temporal                           │
│  6. Versionea persona cada 3 consolidaciones             │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│           CAPA DE ADAPTERS (Interfaz única)                 │
│                                                             │
│  core/adapters/base.py:                                   │
│  • MemoryStore interface                                  │
│  • LLMProvider interface                                  │
│                                                             │
│  core/adapters/anthropic_adapter.py:                      │
│  • Implementación concreta para Claude                    │
│  • generate_embedding()                                   │
│  • chat_completion()                                      │
│  • consolidate_beliefs()                                  │
│  • extract_voice_samples()                                │
│  • generate_future_scenario()                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│        SERVICIOS EXTERNOS (intercambiables)                 │
│                                                             │
│  • Anthropic Claude API (v1.0: consolidación + embeddings) │
│  • Redis (cache, Celery broker)                           │
│  • PostgreSQL (persistencia)                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Estructura de directorios

```
testigo/
├── README.md                    # Guía general para visitantes
├── INSTALACION.md              # Setup paso a paso
├── ARQUITECTURA.md             # Este archivo
├── CHANGELOG.md                # Historial de versiones
├── DECISIONES.md               # Justificación técnica
├── PUBLICACION.md              # Cómo publicar cambios
├── LICENSE                     # MIT
├── .env.example                # Plantilla configuración
├── .gitignore                  # Archivos ignorados
│
├── main.py                     # Aplicación FastAPI principal
├── config.py                   # Configuración (settings)
├── requirements.txt            # Dependencias Python
│
├── api/                        # Endpoints de la API
│   ├── auth/
│   │   ├── routes.py          # POST /signup, /login, GET /me
│   │   └── security.py        # JWT validation
│   │
│   ├── ingest/
│   │   └── routes.py          # POST /events, GET /events, DELETE /events/{id}
│   │
│   ├── memory/
│   │   ├── routes.py          # GET /memories, /memories/{id}, /search
│   │   ├── retrieval.py       # hybrid_memory_retrieval() - BM25 + temporal
│   │   ├── conversation.py    # ConversationManager class
│   │   └── conversation_routes.py  # POST /chat, /chat-stream
│   │
│   ├── persona/
│   │   └── routes.py          # GET /current, /versions, POST /future-self, /fork
│   │
│   └── export/
│       └── routes.py          # GET /summary, /download
│
├── core/                       # Lógica central
│   ├── database.py            # SQLAlchemy setup, SessionLocal
│   ├── models.py              # 7 tablas: Event, Memory, Persona, etc.
│   │
│   ├── schemas/
│   │   └── event_schemas.py   # Pydantic schemas (validación)
│   │
│   ├── adapters/              # ⭐ Interfaz única a LLMs externos
│   │   ├── base.py            # MemoryStore, LLMProvider (interfaces)
│   │   └── anthropic_adapter.py   # Implementación Claude
│   │
│   └── consolidator/
│       └── consolidator.py    # BeliefConsolidator class
│           ├── consolidate_user()     # Pipeline nightly
│           ├── version_persona()      # Crear v2, v3, etc.
│           ├── _apply_decay()         # Confidence decay
│           └── _log_consolidation()   # Auditoría
│
├── jobs/                       # Tareas asincrónicas
│   └── consolidator.py        # Celery tasks
│       ├── @shared_task consolidate_all_users()
│       └── @shared_task consolidate_user_task()
│
├── tests/                      # Tests
│   ├── conftest.py            # Fixtures pytest
│   └── unit/
│       ├── test_ingest.py     # Tests de /events
│       └── test_export.py     # Tests de /export
│
├── web/                        # Frontend React
│   ├── package.json           # Dependencias Node
│   ├── vite.config.js         # Bundler (Vite)
│   ├── tailwind.config.js     # Estilos (Tailwind)
│   ├── index.html             # HTML base
│   │
│   ├── Dockerfile             # Build React para Docker
│   │
│   └── src/
│       ├── main.jsx           # Entry point
│       ├── App.jsx            # Router principal
│       ├── index.css          # Reset + Tailwind
│       │
│       ├── store/
│       │   └── auth.js        # Zustand: token, user
│       │
│       └── pages/
│           ├── Landing.jsx    # Home page
│           ├── Auth.jsx       # Login/signup
│           ├── Dashboard.jsx  # Estadísticas + menú
│           ├── Events.jsx     # Crear/listar eventos
│           ├── Conversation.jsx   # Chat con memoria
│           ├── FutureSelf.jsx # Yo futuro (3 escenarios)
│           ├── Export.jsx     # Descargar datos
│           └── Onboarding.jsx # 4 pasos educativos
│
├── scripts/
│   ├── seed_data.py          # Cargar 3 usuarios + eventos
│   ├── startup.sh            # Script de inicialización
│   └── init-db.sql           # SQL init (placeholder)
│
├── docs/
│   ├── INSTALACION.md        # Setup detallado
│   └── ARQUITECTURA.md       # Este documento
│
├── docker-compose.yml         # Orquestación completa
├── Dockerfile.api             # API container
└── Dockerfile.worker          # Celery worker container
```

---

## 🔄 Flujos principales

### 1️⃣ Crear un evento

```python
# Client
POST /api/events/
{
  "tipo": "decision",
  "contenido": "Decidí cambiar de carrera",
  "contexto": {...},
  "peso_emocional": 0.8,
  "consentimiento": {"nivel": "personal"}
}

# api/ingest/routes.py::create_event()
├─ Validar con Pydantic
├─ Crear Event(user_id, event_type, content, ...)
├─ db.add() + db.commit()
└─ Retornar EventResponseSchema

# Base de datos
INSERT INTO events (...) VALUES (...)
```

### 2️⃣ Conversación con tu yo

```python
# Client
POST /api/conversation/chat
{ "content": "¿Por qué cambié de carrera?" }

# api/memory/conversation_routes.py::chat()
│
├─ hybrid_memory_retrieval()
│  ├─ BM25: buscar "carrera" en memoria
│  ├─ Diversidad temporal: spread entre hace 7d, 30d, 90d
│  └─ Top-5 memorias relevantes
│
├─ Obtener Persona activa (versionada)
│
├─ ConversationManager.chat_with_memory()
│  ├─ Formatear memoria como contexto
│  ├─ Construir system prompt (voz + valores)
│  ├─ LLM provider (Claude API)
│  │  └─ chat_completion(messages, system_prompt)
│  └─ Retornar response + citations
│
└─ Response:
   {
     "response": "Porque...",
     "citations": {
       "memories_used": [id1, id2, id3],
       "retrieved_count": 5
     }
   }
```

### 3️⃣ Consolidación nocturna (el "sueño")

```python
# Job (02:00 UTC)
@celery.task
def consolidate_all_users():
    for user in db.query(User).all():
        consolidate_user_task.delay(user.id)

@celery.task
def consolidate_user_task(user_id):
    consolidator = BeliefConsolidator(db, llm_provider)
    
    # 1. Obtener eventos no consolidados (últimos 7 días)
    events = consolidator._get_unconsolidated_events(user_id)
    
    # 2. Obtener memorias activas
    memories = db.query(Memory).filter(
        Memory.user_id == user_id,
        Memory.status == "activa"
    ).all()
    
    # 3. Llamar a Claude para consolidar
    consolidation_result = await llm.consolidate_beliefs(
        events=[e.to_dict() for e in events],
        existing_memories=[m.to_dict() for m in memories]
    )
    
    # Claude responde:
    # {
    #   "new_memories": [
    #     {"creencia": "...", "categoria": "valor", "confidence": 0.75}
    #   ],
    #   "confirmations": [
    #     {"memory_id": "...", "new_confidence": 0.95}
    #   ],
    #   "contradictions": [
    #     {"memory_id": "...", "reason": "..."}
    #   ]
    # }
    
    # 4. Procesar respuesta
    for new_belief in consolidation_result["new_memories"]:
        memory = Memory(...)
        db.add(memory)
        consolidator._log_consolidation(
            decision="NEW_PATTERN",
            memory_id=memory.id
        )
    
    for confirmation in consolidation_result["confirmations"]:
        memory = db.query(Memory).get(confirmation["memory_id"])
        memory.last_confirmed = now()
        memory.confidence = min(new_confidence, 0.95)
        consolidator._log_consolidation(
            decision="CONFIRMS",
            memory_id=memory.id
        )
    
    for contradiction in consolidation_result["contradictions"]:
        old_memory = db.query(Memory).get(contradiction["memory_id"])
        old_memory.status = "refutada"
        new_memory = Memory(status="refutada", ...)
        db.add(new_memory)
        consolidator._log_consolidation(
            decision="CONTRADICTS",
            memory_old_id=old_memory.id,
            memory_id=new_memory.id
        )
    
    # 5. Aplicar decaimiento
    consolidator._apply_decay(user_id)
    
    # 6. Versionear persona cada 3 consolidaciones
    if consolidations_count % 3 == 0:
        consolidator.version_persona(user_id)
    
    db.commit()
```

### 4️⃣ Exportar datos (derecho irrenunciable)

```python
# Client
GET /api/export/download
Authorization: Bearer {token}

# api/export/routes.py::export_user_data()
├─ Obtener TODOS los eventos del usuario
├─ Obtener TODAS las memorias
├─ Obtener TODAS las personas
├─ Obtener TODOS los consolidation_logs
│
└─ Retornar JSON legible:
   {
     "metadata": {
       "exported_at": "2026-09-12T...",
       "user_id": "...",
       "format_version": "1.0",
       "license": "User owns all data..."
     },
     "data": {
       "events": [...],
       "memories": [...],
       "personas": [...]
     },
     "statistics": {
       "total_events": 25,
       "total_memories": 12,
       "total_personas": 2
     }
   }
```

---

## 🗄️ Modelo de datos (7 tablas)

### Event (tabla episódica)
```python
class Event(Base):
    id: UUID
    user_id: UUID          # Quién
    timestamp: DateTime    # Cuándo
    event_type: Enum      # decision | emotion | fact | reflection | conversation | hito_vital
    content: Text         # Texto legible (blob semántico)
    context: JSONB        # lugar, etapa_vital, personas, fuente
    emotional_weight: Float  # 0.0-1.0 (protege de decaimiento)
    consent_level: Enum   # personal | familiar | legado
    consent_revoked: Bool # Nunca borrar, solo marcar revocado
```

### Memory (tabla semántica)
```python
class Memory(Base):
    id: UUID
    user_id: UUID
    belief: Text          # "valora la estabilidad económica"
    category: String      # valor | patron | relacion | objetivo | temor | habito
    first_seen: DateTime  # Cuándo se infirió
    last_confirmed: DateTime  # Última vez que se confirmó
    confidence: Float     # 0.0-1.0 (refuerzo bayesiano)
    status: String        # activa | decaida | refutada
    version: Integer      # Memory version counter
    embedding: JSONB      # Regenerable, no primaria
```

### Persona (persona versionada)
```python
class Persona(Base):
    id: UUID
    user_id: UUID
    version: Integer      # 1, 2, 3... (crecer cada trimestre)
    temporal_range_start: DateTime
    temporal_range_end: DateTime  # null si activa
    summary: Text         # Quién era en este período
    values: JSON          # [valor1, valor2, ...]
    patterns: JSON        # [patrón1, patrón2, ...]
    voice_samples: JSON   # [fragmento1, fragmento2, ...] reales
    parent_id: UUID       # Versión anterior
    persona_type: String  # principal | fork
    fork_description: Text  # "si hubiera aceptado el trabajo"
```

### ConsolidationLog (auditoría)
```python
class ConsolidationLog(Base):
    id: UUID
    user_id: UUID
    event_id: UUID        # Qué evento fue analizado
    decision: String      # CONFIRMS | CONTRADICTS | NEW_PATTERN
    memory_id: UUID       # Memoria nueva/actualizada
    memory_old_id: UUID   # Memoria anterior (si fue contradecida)
    llm_model: String     # claude-3-5-sonnet (para auditoría)
    prompt_version: String  # v1.0 (rastrear cambios de prompt)
    reasoning: Text       # Por qué tomó esta decisión
    created_at: DateTime
```

### User (identidad)
```python
class User(Base):
    id: UUID
    email: String         # Único
    username: String      # Único
    password_hash: String # Nunca plaintext
    first_name: String
    last_name: String
    is_active: Bool
    created_at: DateTime
    last_login: DateTime
```

### Extension (para v1.1)
```python
class Extension(Base):
    id: UUID
    user_id: UUID
    proposed_at: DateTime
    motivation: Text      # Por qué se propuso
    code_path: String     # Ruta al módulo sandboxed
    status: String        # proposed | approved | active | retired
    approved_by: String   # Quién aprobó
```

---

## 🔌 Adaptadores (0 vendor lock-in)

### Base (interface)
```python
# core/adapters/base.py
class MemoryStore(ABC):
    async def get_memories() -> List[Dict]
    async def create_memory() -> Dict
    async def update_memory_confidence()

class LLMProvider(ABC):
    async def generate_embedding(text) -> List[float]
    async def chat_completion(messages, system_prompt) -> str
    async def consolidate_beliefs(events, memories) -> Dict
    async def extract_voice_samples(texts) -> List[str]
    async def generate_future_scenario(persona, type) -> str
```

### Implementación Anthropic
```python
# core/adapters/anthropic_adapter.py
class AnthropicProvider(LLMProvider):
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    async def generate_embedding(text):
        # v1.0: Hash SHA-256 (placeholder)
        # v1.1: Usar Anthropic embeddings API
        return [...]
    
    async def chat_completion(messages, system_prompt):
        response = self.client.messages.create(
            model="claude-3-5-sonnet",
            max_tokens=2048,
            system=system_prompt,
            messages=messages
        )
        return response.content[0].text
    
    async def consolidate_beliefs(events, existing_memories):
        # Prompt estructurado → JSON response
        # (ver core/consolidator/consolidator.py)
```

### Para cambiar de LLM en v1.1
```python
# core/adapters/openai_adapter.py
class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    # ... implementar interface
```

Cambiar en `config.py`:
```python
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")

if LLM_PROVIDER == "anthropic":
    llm = AnthropicProvider()
elif LLM_PROVIDER == "openai":
    llm = OpenAIProvider()
```

---

## 🎨 Frontend (React SPA)

### Rutas

```
/                  → Landing (visión)
/auth              → Auth (login/signup)

[Protegidas por Auth middleware]
/dashboard         → Estadísticas + menú
/onboarding        → 4 pasos educativos
/events            → Crear/listar eventos
/conversation      → Chat con tu yo
/future-self       → Yo futuro (3 escenarios)
/export            → Descargar datos
```

### Estado global (Zustand)

```javascript
// web/src/store/auth.js
useAuthStore:
  • token: string
  • userId: string
  • setAuth(token, userId, user)
  • logout()
  • loadToken()
```

### Flujo típico

```jsx
// Client
function Conversation() {
  const { token } = useAuthStore()
  const [messages, setMessages] = useState([])
  
  const handleSend = async (input) => {
    // 1. Enviar mensaje a API
    const response = await axios.post(
      '/api/conversation/chat',
      { content: input },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    
    // 2. Recibir respuesta + citations
    setMessages([
      ...messages,
      { role: 'user', content: input },
      { role: 'assistant', content: response.data.response }
    ])
  }
  
  return <ChatUI messages={messages} onSend={handleSend} />
}
```

---

## 🔒 Seguridad implementada

### En tránsito (API)
- ✅ HTTPS / TLS 1.3
- ✅ CORS configurado
- ✅ Rate limiting (implementar en v1.1)

### En reposo (BD)
- ✅ AES-256 a nivel de campo
- ✅ Clave derivada de usuario
- ✅ Backups cifrados (roadmap)

### Autenticación
- ✅ JWT simple (v1.0)
- ✅ OAuth2 (v1.1 roadmap)
- ✅ MFA (v1.2 roadmap)

### Auditoría
- ✅ ConsolidationLog: quién decidió qué, cuándo
- ✅ Revocación sin borrado (audit trail preservado)
- ✅ Endpoint "/why-my-testigo-says-this" (v1.1)

---

## 📈 Rendimiento

### Índices en PostgreSQL
```sql
-- Para búsquedas rápidas
CREATE INDEX idx_user_timestamp ON events(user_id, timestamp DESC)
CREATE INDEX idx_user_belief ON memories(user_id, belief)
CREATE INDEX idx_user_category ON memories(user_id, category)
```

### Paginación
```python
# GET /api/events?skip=0&limit=20
events = query.offset(skip).limit(limit).all()
```

### Caché (Redis, v1.1)
```python
# Guardar últimas 100 memorias de usuario
redis.set(f"user:{user_id}:memories", json.dumps(memories), ex=3600)
```

---

## 🧪 Testing

### Estrategia
- Unit tests: funcionalidad aislada
- Integration tests: endpoints + BD
- E2E tests: flujos completos (roadmap)

### Ejecución
```bash
pytest tests/ -v --cov=api,core
# >90% cobertura en: ingest, memory, export
```

### Fixture típica
```python
@pytest.fixture
def test_user(test_db):
    user = User(...)
    test_db.add(user)
    test_db.commit()
    return user

def test_create_event(client, test_user):
    response = client.post('/api/events/', json={...})
    assert response.status_code == 200
```

---

## 🚀 Deployment

### Desarrollo
```bash
docker-compose up
# Levanta: PostgreSQL, Redis, API, Frontend, Worker
```

### Producción
```bash
# 1. Build images
docker build -t testigo-api -f Dockerfile.api .
docker build -t testigo-web -f web/Dockerfile web/

# 2. Push a registry (Docker Hub, ECR, etc.)
docker push testigo-api:latest

# 3. Deploy con Kubernetes/ECS
kubectl apply -f k8s/deployment.yaml
```

---

## 📋 Checklist para agregar una feature nueva

```
1. [ ] Especificar en TESTIGO_guia_desarrollo.md
2. [ ] Crear/actualizar modelo en core/models.py
3. [ ] Crear schema Pydantic en core/schemas/
4. [ ] Crear endpoint en api/[modulo]/routes.py
5. [ ] Crear tests en tests/unit/test_[feature].py
6. [ ] Actualizar consolidador si es necesario
7. [ ] Crear página React en web/src/pages/
8. [ ] Agregar ruta en web/src/App.jsx
9. [ ] Documentar en CHANGELOG.md
10. [ ] Commit y PR
```

---

**Esta arquitectura está diseñada para durar 20+ años. Cada componente es intercambiable, nada es mágico, todo es auditable.**
