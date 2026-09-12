# TESTIGO — Guía de desarrollo completa para agentes de IA

> **Propósito de este documento:** permitir que cualquier modelo de lenguaje (o agente de
> código: Claude Code, Cursor, Codex, etc.) desarrolle este proyecto de principio a fin y
> entregue una versión productiva y usable. Sigue las instrucciones en orden. Donde algo
> sea una decisión de producto y no de ingeniería, está marcado como [DECISIÓN].

---

## 0. Cómo usar este documento

1. Lee las secciones 1–3 completas antes de escribir una sola línea de código.
2. Las secciones 4–10 son la especificación técnica: implementa tal cual salvo mejor
   argumento explícito (documenta cualquier desviación en `DECISIONES.md`).
3. La sección 11 es el plan por fases con criterios de aceptación verificables. No avances
   de fase sin cumplir los criterios de la anterior.
4. La sección 14 enumera errores que NO debes cometer. Están probados en el diseño.

---

## 1. Visión

**TESTIGO** (nombre de trabajo) es una aplicación de memoria longitudinal: acompaña a una
persona durante años, registra su vida con consentimiento granular, aprende de ella y, con
el tiempo, puede conversar como "el yo futuro" de esa persona. Es la fusión de dos ideas:

- **App auto-extensible:** propone y construye nuevas funcionalidades según la etapa vital.
- **Simulador del yo mayor:** un interlocutor construido sobre décadas de datos reales.

La promesa de producto: *la única app que se vuelve más valiosa cuanto más vieja es.*

**El valor no es la IA, es la memoria.** Nadie puede replicar 10 años de la vida de un
usuario. Todo el diseño defiende ese activo.

---

## 2. Principios rectores (no negociables)

Estos principios prevalecen sobre cualquier comodidad de implementación:

1. **La memoria sobrevive al modelo.** El modelo de IA es un componente intercambiable
   (se opera cada 2–4 años). La memoria vive 20+. Nada en el almacenamiento permanente
   depende de un proveedor, un modelo o un formato propietario.
2. **Texto legible = fuente de verdad.** Todo hecho se guarda como texto en formato
   abierto. Embeddings y representaciones vectoriales son **derivados regenerables**,
   nunca primarios. Test: *"¿puedo leer esto en un editor de texto en 2045?"*
3. **Nunca borrar, solo superponer.** La gente cambia. "En 2026 valoraba X" y "en 2031
   valora Y" coexisten con fecha y confianza. El conflicto es historia, no error.
4. **Consentimiento viaja con el dato.** Cada evento lleva su propio nivel de permiso
   (personal / familiar / legado) y es revocable de forma independiente.
5. **Exportable siempre.** El usuario puede exportar íntegramente sus datos en JSON legible
   en cualquier momento, sin coste y sin fricción. Es un derecho, no un feature.
6. **La IA propone, el humano dispone.** Ninguna funcionalidad auto-generada se activa sin
   aprobación explícita del usuario. Ninguna conclusión sobre la persona se presenta como
   hecho sin confianza y fecha.
7. **La empresa puede morir, la memoria no.** El esquema de datos y el export deben
   permitir reconstruir el archivo sin la infraestructura original.

---

## 3. Arquitectura general

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENTE (web/móvil)                      │
│        Entrada de eventos · Aprobaciones · Conversación      │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS (TLS 1.3)
┌──────────────────────────▼──────────────────────────────────┐
│                      API (FastAPI)                           │
│   Auth · Ingesta de eventos · Recuperación · Consentimiento  │
└──────┬──────────────────┬───────────────────┬───────────────┘
       │                  │                   │
┌──────▼───────┐  ┌───────▼────────┐  ┌───────▼─────────┐
│ EVENT STORE  │  │  MEMORIA       │  │  MODELO PERSONA │
│ (inmutable)  │  │  SEMÁNTICA     │  │  (versionado)   │
│ PostgreSQL   │  │  (regenerable) │  │  (bifurcable)   │
└──────┬───────┘  └───────┬────────┘  └───────┬─────────┘
       │                  │                   │
       │           ┌──────▼───────────────────▼───┐
       │           │   EMBEDDINGS (cache,          │
       │           │   regenerable por migración)  │
       │           └───────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────┐
│           CONSOLIDADOR (jobs por lotes)                  │
│   Episódica + semántica actual → nueva semántica         │
│   Persona → nueva versión / forks                        │
│   Corre sobre LLM vía adaptador intercambiable           │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│           CAPA DE MODELO (interfaz única)                │
│   MemoryStore / LLMProvider: ningún código toca         │
│   APIs de terceros directamente                          │
└──────────────────────────────────────────────────────────┘
```

**Regla de dependencias:** el flujo de dependencias va hacia abajo. La capa de modelo no
conoce el event store; el cliente no conoce el consolidador.

---

## 4. Stack tecnológico

[DECISIÓN: stack pragmático, reemplazable; no elegir tecnología exótica]

| Componente | Elección por defecto | Justificación |
|---|---|---|
| API | Python 3.12 + FastAPI | Ecosistema LLM maduro, tipado, async |
| Base de datos | PostgreSQL 16+ | JSONB para esquema flexible, ACID, vida útil ilimitada |
| Storage frío | Parquet en disco/S3-compatible | Formatos abiertos para archivo de décadas |
| Jobs/consolidación | Celery + Redis (o cron simple al inicio) | Desacoplado, reintentable |
| Embeddings | Tabla aparte, cualquier proveedor | Derivados, regenerables |
| Frontend | Web app (React/Svelte) + PWA | Un código, todos los dispositivos |
| Auth | OAuth2 + cifrado de datos personales con clave del usuario | Ver sección 10 |
| Contenedores | Docker + docker-compose (prod: Kubernetes opcional) | Reproducibilidad |
| LLM | Cualquiera vía adaptador | OpenAI/Anthropic/local — el código no elige |

Restricción dura: **ninguna dependencia de proveedor de LLM aparece fuera del módulo
`adapters/`**.

---

## 5. Modelo de datos

### 5.1 Evento (átomo de memoria, esquema CONGELADO)

```json
{
  "id": "evt_<uuid>",
  "timestamp": "ISO-8601 con timezone",
  "tipo": "decision | emocion | hecho | reflexion | conversacion | hito_vital",
  "contenido": "texto legible, en el idioma y voz de la persona",
  "contexto": {
    "lugar": "string opcional",
    "etapa_vital": "string libre (ej: 'primer empleo')",
    "personas": ["nombres o alias"],
    "fuente": "app | import | conversacion"
  },
  "peso_emocional": 0.0,
  "consentimiento": {
    "nivel": "personal | familiar | legado",
    "otorgado_en": "timestamp",
    "revocable": true
  },
  "derivados": ["mem_<id>", ...]
}
```

- `tipo` es un enum cerrado y **jamás se modifica retroactivamente**. Nuevos tipos se
  añaden solo con migración versionada.
- `contenido` siempre texto. Prohibido guardar embeddings como contenido.

### 5.2 Memoria semántica (conocimiento consolidado)

```json
{
  "id": "mem_<uuid>",
  "creencia": "texto: 'valora la estabilidad económica'",
  "categoria": "valor | patron | relacion | objetivo | temor | habito",
  "first_seen": "timestamp",
  "last_confirmed": "timestamp",
  "confidence": 0.0,
  "estado": "activa | decaida | refutada",
  "origen": ["evt_<id>", ...],
  "version_memoria": 3
}
```

- `refutada` conserva la creencia vieja con sus fechas. Ver principio 3.

### 5.3 Modelo de persona (versionado y bifurcable)

```json
{
  "persona_id": "per_<uuid>",
  "version": 4,
  "rango_temporal": ["2026-01-01", "2029-06-30"],
  "resumen": "quién era esta persona en este periodo",
  "valores": ["..."], "patrones": ["..."], "contradicciones": ["..."],
  "muestras_voz": ["fragmentos reales de texto del usuario"],
  "padre": "per_<uuid>|null",
  "tipo": "principal | fork",
  "fork_descripcion": "null | 'si hubiera aceptado el trabajo de 2028'"
}
```

### 5.4 Funcionalidades auto-generadas (idea 20)

```json
{
  "extension_id": "ext_<uuid>",
  "propuesta_en": "timestamp",
  "motivacion": "qué patrón de uso la originó (en lenguaje natural)",
  "codigo": "ruta al módulo generado (sandboxed)",
  "estado": "propuesta | aprobada | activa | retirada",
  "aprobada_por": "usuario",
  "tests": "ruta a tests generados",
  "auditoria": {"estatica": "ok", "fecha": "..."}
}
```

---

## 6. Componentes y responsabilidades

| Módulo | Responsabilidad | Prohibido |
|---|---|---|
| `ingest` | Validar y escribir eventos; validar consentimiento | Modificar eventos existentes |
| `memory` | CRUD de memoria semántica; recuperación (híbrida texto+vectorial) | Inyectar toda la memoria en contexto (selección obligatoria, top-N por relevancia + diversidad temporal) |
| `consolidator` | Jobs nocturnos: confirmar/refutar/nueva creencia; decaimiento; versionar persona | Borrar origen episódico; decidir sin registrar decisión |
| `persona` | Versionado, forks, extracción de voz | Sobrescribir una versión congelada |
| `extensions` | Propuesta, generación en sandbox, aprobación, poda | Activar sin aprobación humana |
| `adapters/` | Única puerta a LLMs/embeddings externos | Que otro módulo importe SDKs de terceros |
| `export` | Export JSON legible completo, on-demand | Requerir suscripción o condiciones |

---

## 7. Pipeline de consolidación (el "sueño" del sistema)

Job nocturno, idempotente, reintentable:

```
ENTRADA: eventos desde última consolidación + memoria semántica activa

PARA CADA evento:
  1. Clasificar contra creencias existentes (via LLM, salida JSON estricta):
     - CONFIRMA(creencia_id)      → actualizar last_confirmed, subir confidence
     - CONTRADICE(creencia_id)    → marcar refutada la vieja, crear nueva con origen
     - NUEVO_PATRON               → crear creencia (confidence baja inicial)
     - ALTO_PESO_EMOCIONAL        → marcar evento como protegido contra decaimiento
  2. Registrar cada decisión del consolidador en `consolidation_log`
     (auditable: qué modelo decidió, cuándo, con qué prompt-version).

DECAIMIENTO (semanal):
  - confidence -= f(tiempo_sin_confirmar), sin bajar de piso si peso_emocional alto.

VERSIONADO DE PERSONA (trimestral o por hito vital):
  - Generar nueva versión consolidada; congelar la anterior.
```

Requisitos: el log de consolidación permite responder *"¿por qué el sistema cree esto de
mí?"* — y esa trazabilidad es feature de producto ("¿por qué mi testigo dice esto?").

---

## 8. Migración de modelos (test de regresión de identidad)

Cada vez que se cambia de proveedor/modelo:

1. Mantener `identity_bench.jsonl`: ~200 consultas canónicas con respuestas de referencia
   ("¿Qué valora esta persona?", "¿Cómo reaccionó ante X?", "¿Cuál es su tono?").
2. Ejecutar la batería con modelo viejo y nuevo sobre la misma memoria.
3. Divergencia >5% sustancial → ajustar system prompt / capa de memoria. **Nunca** el
   archivo original.
4. Registrar migración en `MODEL_MIGRATIONS.md` (fechas, modelos, divergencias).

---

## 9. Sistema de extensiones auto-generadas (idea 20)

Ciclo: **observar → hipotetizar → proponer → construir (sandbox) → validar → integrar → podar**

- Detección: heurísticas sobre eventos de uso (búsquedas fallidas, exportaciones manuales
  repetidas, tareas abandonadas) resumidas por LLM en "necesidades candidatas".
- Propuesta al usuario en lenguaje natural: *"Veo que haces X a mano. ¿Quieres que lo
  automatice?"*
- Generación: agente de código en sandbox (contenedor sin red por defecto, recursos
  limitados, sin acceso al event store global — solo a APIs definidas).
- Activación solo tras aprobación explícita y superar tests generados + auditoría estática.
- Poda trimestral: funcionalidades sin uso propuestas para retirar.

---

## 10. Seguridad y privacidad

1. **Cifrado:** en tránsito TLS 1.3; en reposo AES-256. Campo sensible: cifrado a nivel de
   campo con clave derivada del usuario (para que ni el operador lea sin consentimiento).
2. **Consentimiento:** granular por evento; revocación que propaga a memoria semántica
   (marca como revocada, no borra la fila de log — auditoría).
3. **Menor privilegio:** el consolidador lee, no escribe el event store; las extensiones
   no tocan datos ajenos a su alcance aprobado.
4. **Modo incógnito:** conversaciones que no persisten.
5. **Backups:** cifrados, verificados con restore periódico.
6. **Cumplimiento:** diseñar desde cero para GDPR/LOPDGDD (portabilidad = principio 5).

---

## 11. Plan de desarrollo por fases

### M1 — Fundación (semanas 1–3)
- Repo, CI, docker-compose con PostgreSQL.
- Esquema SQL de las 4 tablas (eventos, memoria, persona, extensiones) + migraciones.
- Módulo `ingest` + API de creación de eventos + auth básica.
- **Criterio de aceptación:** se puede crear, listar y exportar (JSON) un evento vía API.

### M2 — Recuperación y conversación (semanas 4–6)
- `adapters/` con proveedor LLM configurable por variable de entorno.
- Recuperación híbrida (BM25 + embeddings derivados) con selección top-N + diversidad temporal.
- Endpoint de conversación con el "yo" (persona actual) con inyección de memoria seleccionada.
- **Criterio:** conversación de 15 min que usa exclusivamente memoria del usuario, sin
  inventar datos no presentes (test con caja negra + logging de fuentes citadas).

### M3 — Consolidador (semanas 7–9)
- Job nocturno completo (sección 7) con `consolidation_log`.
- Decaimiento y protección por peso emocional.
- Vista de usuario: "¿Por qué el sistema cree esto de mí?" con trazabilidad.
- **Criterio:** tras 7 días de datos simulados, el sistema genera creencias acordes a los
  eventos; toda creencia tiene origen navegable.

### M4 — Persona versionada + yo futuro (semanas 10–12)
- Versionado trimestral, forks, extracción de muestras de voz.
- Feature "conversar con mi yo de dentro de N años" construido sobre una versión
  congelada + extrapolación de escenarios (tendencial/optimista/arrepentimiento).
- `identity_bench.jsonl` + script de regresión.
- **Criterio:** la batería de identidad pasa con divergencia <5% en dos migraciones de
  modelo simuladas (p.ej. cambiar el adaptador a otro proveedor).

### M5 — Extensiones + producción (semanas 13–16)
- Ciclo completo de extensiones (sección 9) con sandbox.
- Frontend usable: entrevista semanal (3 preguntas), aprobaciones, conversación, export.
- Hardening: rate limiting, auditoría, backups con restore probado, documentación.
- **Criterio final (versión productiva v1.0):**
  - Un usuario real puede completar: onboarding → 4 semanas de entrevistas → conversación
    con su yo futuro → export completo de sus datos.
  - Tests automatizados en CI verdes; cobertura crítica (ingest, consent, export) >90%.
  - `docker-compose up` levanta el sistema completo con datos de ejemplo.

---

## 12. Estructura de directorios

```
testigo/
├── LICENSE                  # MIT
├── README.md
├── DECISIONES.md
├── docker-compose.yml
├── api/                     # FastAPI
│   ├── ingest/  memory/  persona/  extensions/  export/
├── core/
│   ├── adapters/            # Única puerta a LLMs/embeddings
│   │   ├── base.py          # interfaces MemoryStore, LLMProvider
│   │   └── openai_*.py / anthropic_*.py / local_*.py
│   ├── consolidator/
│   ├── identity_bench.jsonl
│   └── schemas/             # JSON schemas congelados + validadores
├── jobs/                    # Celery/cron
├── web/                     # PWA
├── tests/
└── docs/
    ├── MODELO_DE_DATOS.md
    └── MODELO_MIGRATIONS.md
```

---

## 13. Licencia

Proyecto publicado bajo **licencia MIT**: uso, copia, modificación y distribución libres,
incluido uso comercial, con única condición de conservar el aviso de copyright. Archivo
`LICENSE` estándar MIT en la raíz. La memoria del usuario no es "código": el usuario
conserva la propiedad total de sus datos y el derecho de exportación es irrenunciable
(documentado en README y términos).

---

## 14. Qué NO hacer (errores probados)

1. ❌ Guardar embeddings como representación primaria. ✅ Texto primero, vectores como caché.
2. ❌ Sobrescribir el perfil de persona. ✅ Versionar y bifurcar.
3. ❌ Borrar creencias contradichas. ✅ Marcar refutadas con fechas.
4. ❌ Inyectar toda la memoria en el contexto. ✅ Selección por relevancia + diversidad temporal.
5. ❌ Activar extensiones sin aprobación humana. ✅ Siempre consentimiento explícito.
6. ❌ Acoplar código a un proveedor de LLM fuera de `adapters/`. ✅ Interfaz única.
7. ❌ Hacer la exportación difícil o condicionada. ✅ On-demand, gratis, JSON legible.
8. ❌ Presentar inferencias como hechos. ✅ Siempre con confidence, fecha y trazabilidad.
9. ❌ Diseñar el tono del "yo futuro" como oráculo. ✅ Espejo narrativo: admite su naturaleza.
10. ❌ Tratar la retención por dependencia como estrategia. ✅ El negocio es la experiencia,
    no el rehén.

---

*Documento de especificación v1.0 — diseñado para durar más que cualquier modelo.*
