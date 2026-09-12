# Guía de Instalación - TESTIGO v1.0.0

## Requisitos previos

- **Docker** 20.10+ y **Docker Compose** 2.0+
- **Anthropic API Key** (gratis: https://www.anthropic.com)
- 4GB RAM disponible
- Puerto 3000 (frontend), 8000 (API), 5432 (DB) disponibles

## Instalación rápida (Docker)

### 1. Clonar y configurar

```bash
git clone https://github.com/yourusername/testigo.git
cd testigo

# Copiar configuración
cp .env.example .env
```

### 2. Añadir API Key

```bash
# Editar .env
nano .env

# Buscar ANTHROPIC_API_KEY y reemplazar:
ANTHROPIC_API_KEY=sk-ant-... # Tu clave real
```

### 3. Iniciar

```bash
docker-compose up
```

Espera 2-3 minutos para que:
- PostgreSQL se inicialice
- Schema se cree
- Datos ficticios se carguen
- API y frontend se levanten

### 4. Acceder

| Componente | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

## Usuarios de prueba

El sistema crea 3 usuarios automáticamente:

```
Sophia García      sophia@testigo.local   (token: {"user_id": "..."})
Marcus Chen        marcus@testigo.local
Elena Rodriguez    elena@testigo.local
```

Para iniciar sesión, usa cualquier email + contraseña cualquiera en el flujo de signup.

## Instalación local (sin Docker)

### 1. Backend

```bash
# Python 3.12
python -m venv venv
source venv/bin/activate  # o .\ venv\Scripts\activate en Windows

# Dependencias
pip install -r requirements.txt

# PostgreSQL local
# macOS: brew install postgresql
# Linux: sudo apt-get install postgresql
# Windows: https://www.postgresql.org/download/windows/

# Crear DB y usuario
psql -U postgres
CREATE USER testigo WITH PASSWORD 'testigo_pass';
CREATE DATABASE testigo_db OWNER testigo;
\q

# Actualizar .env
DATABASE_URL=postgresql://testigo:testigo_pass@localhost:5432/testigo_db

# Iniciar API
python main.py
```

API corre en http://localhost:8000

### 2. Frontend

```bash
cd web
npm install
npm run dev
```

Frontend corre en http://localhost:3000

### 3. Redis (para Celery)

```bash
# macOS
brew install redis
redis-server

# Linux
sudo apt-get install redis-server
redis-server

# Windows
https://redis.io/download
```

### 4. Consolidador (opcional)

```bash
# En otra terminal
source venv/bin/activate
celery -A jobs.consolidator worker --loglevel=info
```

## Troubleshooting

### "Connection refused" en PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
psql -U testigo -d testigo_db

# Si no existe, crear:
createdb -U postgres testigo_db
```

### "ANTHROPIC_API_KEY not found"

```bash
# Asegúrate de que .env tiene la clave:
grep ANTHROPIC_API_KEY .env

# Debe verse: ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### "Port 3000 already in use"

```bash
# Cambiar en .env y docker-compose.yml:
ports:
  - "3001:3000"  # Usar 3001 en lugar de 3000
```

### Tests fallando

```bash
# Instalar dependencias de test
pip install pytest pytest-asyncio pytest-cov

# Correr tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=api,core --cov-report=html
# Abre htmlcov/index.html
```

## Verificación

Después de iniciar, verifica:

```bash
# Health check de API
curl http://localhost:8000/health

# Debe responder:
{"status": "healthy", "version": "1.0.0"}

# Usuarios cargados
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer {\"user_id\": \"...\""

# Frontend accesible
open http://localhost:3000
```

## Actualizar modelo LLM

Para cambiar Claude a otro modelo:

```bash
# En .env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229  # Cambiar aquí

# Reiniciar API
docker-compose restart api
```

Para usar otro proveedor (OpenAI, local):
1. Implementar adaptador en `core/adapters/openai_adapter.py`
2. Cambiar `LLM_PROVIDER=openai` en .env
3. Agregar clave: `OPENAI_API_KEY=...`

## Performance

Para usar en producción:

```yaml
# docker-compose.yml
services:
  api:
    environment:
      - WORKERS=4  # Aumentar threads
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  postgres:
    environment:
      - shared_buffers=256MB
      - effective_cache_size=1GB
```

## Backups

```bash
# Backup manual
docker-compose exec postgres pg_dump -U testigo testigo_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U testigo testigo_db < backup.sql
```

---

¿Problemas? Abre un issue: https://github.com/yourusername/testigo/issues
