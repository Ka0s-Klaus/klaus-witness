# Changelog - TESTIGO

## [1.0.0] - 2026-01-15

### 🎉 Primera versión pública (MVP Completo)

**Completed:**
- ✅ Ingest de eventos con consentimiento granular
- ✅ Memoria semántica consolidada nocturnamente
- ✅ Conversación con tu yo basada en historia real
- ✅ Persona versionada y forks para explorar escenarios
- ✅ Yo futuro: conversación con extrapolación IA
- ✅ Export completo en JSON legible
- ✅ Frontend hermoso (React + Tailwind + Framer Motion)
- ✅ Datos ficticios realistas para demostración
- ✅ Tests críticos con >90% cobertura
- ✅ Docker-compose para deployment One-click
- ✅ Documentación completa

**Arquitectura:**
- FastAPI backend con PostgreSQL
- Celery + Redis para consolidación
- Claude API integration vía adaptador neutral
- React SPA con PWA
- Autenticación simple (MVP)

**Principios implementados:**
1. Memoria sobrevive al modelo
2. Texto legible = fuente de verdad
3. Nunca borrar, solo superponer
4. Consentimiento granular + revocación
5. Export siempre disponible
6. IA propone, humano dispone
7. Portabilidad como derecho

**Notas:**
- Consolidador corre con cron simple (no Celery distribuida)
- Versionado de persona manual (automatizar en v1.1)
- Embeddings placeholder (reemplazar en v1.1)
- Sin extensiones auto-generadas (Feature v1.1)

---

## Roadmap v1.1 (Q2 2026)

- [ ] Extensiones auto-generadas (sandbox + aprobación)
- [ ] Embeddings reales (Anthropic/OpenAI)
- [ ] Consolidador distribuido (Celery escalable)
- [ ] Versionado automático trimestral
- [ ] Identity benchmark + tests de regresión
- [ ] Auditoría mejorada (por quién, cuándo, por qué)
- [ ] Compartir momentos (consentimiento cruzado)
- [ ] Mobile app nativa
- [ ] Backups cifrados en S3

## Roadmap v2.0 (2027)

- [ ] Multi-persona (familias, equipos)
- [ ] Integración con calendario/email
- [ ] Análisis de patrones avanzado
- [ ] VR: caminar por tu memoria
- [ ] Modelo local opcional
- [ ] Marketplace de extensiones comunitarias

---

Todos los cambios son reversibles. La memoria viaja con el código.
