#!/bin/bash
set -e
echo 'Iniciando el contenedor de la aplicacion SmartGym...'

echo 'Asegurando la creacion de tablas en PostgreSQL...'
python -c 'import asyncio; from app.database.session import create_db; from app.models import *; asyncio.run(create_db())'
sleep 6

echo 'Ejecutando script para cargar los datos semilla...'
python scripts/seed.py

echo 'Iniciando servidor uvicorn en el puerto 8000 del contenedor...'
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
