# Decisiones de Implementación - TESTIGO v1.0.0

## Arquitectura

### FastAPI vs Django
**Decisión:** FastAPI
- Más rápido, mejor para async
- ASGI nativo
- Mejor para APIs modernas
- Documentación automática con /docs

### PostgreSQL vs Firebase/MongoDB
**Decisión:** PostgreSQL
- JSONB nativo (flexible + queryable)
- ACID garantizado
- Sostenible a largo plazo (open source)
- Mejor para datos sensibles

### Celery vs Temporal/Airflow
**Decisión:** Celery (simple) en v1.0, Temporal en v1.1
- MVP: cron simple suficiente
- v1.1: Temporal para consolidación distribuida
- Razón: Consolidador no es crítico en v1.0

## Frontend

### React vs Vue/Svelte
**Decisión:** React
- Ecosistema más grande
- Más accesible para colaboradores
- Vercel deployment sin fricción

### Tailwind vs Material/Bootstrap
**Decisión:** Tailwind
- Utility-first más eficiente
- Menor bundle size
- Mejor control de diseño

### Framer Motion vs Recharts
**Decisión:** Ambas
- Framer Motion: transiciones suaves
- Recharts: gráficas (v1.1)

## Autenticación

### JWT vs Sessions
**Decisión:** Simple JWT (MVP v1.0)
- MVP: token en localStorage suficiente
- v1.1: OAuth2 + MFA
- v2.0: Passkeys

## Consolidación

### Frecuencia
**Decisión:** Nocturnamente (02:00 UTC)
- No interfiere con uso diario
- Menos carga en BD
- Suficiente para v1.0

## Embeddings

### Almacenamiento
**Decisión:** JSONB regenerable, no primario
- Evita lock-in de proveedor
- Migraciones de modelo limpias
- v1.1: Implementar vector similarity search real

### Generación
**Decisión:** Hash SHA-256 en v1.0
- Placeholder funcional
- v1.1: Anthropic embeddings API
- v1.2: OpenAI o local (sentencebert)

## Privacidad

### Cifrado
**Decisión:** AES-256 campo a campo
- Mayor granularidad
- Clave derivada de usuario
- Operador no puede leer sin consentimiento

## Datos ficticios

**Decisión:** 3 usuarios completos, 4 semanas de eventos
- Realista pero no sensible
- Historias emocionalmente auténticas
- Suficiente para consolidar creencias

## Validación

**Decisión:** Pydantic estricto
- Type safety
- Error messages claros
- Facilita debugging

---

**Principio transversal:** Mejor simple y correcto que complejo pero incierto.
