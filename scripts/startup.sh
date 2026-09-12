#!/bin/bash

echo "🚀 Iniciando TESTIGO v1.0.0..."

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a PostgreSQL..."
until pg_isready -h $DATABASE_HOST -U $POSTGRES_USER -d $POSTGRES_DB 2>/dev/null; do
  sleep 1
done

echo "✓ PostgreSQL está listo"

# Crear tablas con SQLAlchemy
echo "🗄️  Creando schema..."
python -c "from core.database import init_db; init_db()"

# Cargar datos ficticios
echo "🌱 Cargando datos de demostración..."
python scripts/seed_data.py

echo "✅ Base de datos inicializada"

# Iniciar API
echo "🌐 Iniciando API..."
exec "$@"
