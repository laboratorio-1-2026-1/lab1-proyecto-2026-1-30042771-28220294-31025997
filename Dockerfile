# Creacion a partir de una imagen base de Python 3.13 (slim para menor tamaño).
FROM python:3.13-slim

# Configuracion de variables de entorno para Python.
# Evitan que Python cree archivos binarios ejecutables y almacene en bufer las salidas de terminal.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Especificacion de directorio de trabajo principal dentro del contenedor.
WORKDIR /workspace

# Ejecucion de comandos para instalar dependencias y compiladores necesarios para utilizar
# librerias de Python, como asyncpg.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia de archivo requirements.txt dentro de "workspace" e instalacion de dependencias de Python
# dentro del contenedor. Se actualiza "pip" antes de instalar las librerias necesarias.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia todo el codigo del espacio de tabajo actual (en Windows) al interior del contenedor (Linux).
# Respeta las indicaciones del .dockerignore.
COPY . .

# Conseción de permisos de ejecucion para el script de inicalizacion principal: entrypoint.sh
RUN chmod +x entrypoint.sh

# Especificacion del puerto del contenedor en que se recibiran conexiones entrantes.
EXPOSE 8000

# Ejecución del script principal, que crea las tablas de la base de datos, las puebla con los datos
# semilla y pone en marcha el servidor uvicorn de FastAPI.
ENTRYPOINT ["./entrypoint.sh"]
