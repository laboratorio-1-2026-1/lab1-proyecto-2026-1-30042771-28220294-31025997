# Proyecto API para Gestión Integral de Gimnasios (SmartGym)

El objetivo de este proyecto es diseñar y construir una **API** robusta y escalable que permita la gestión operativa, financiera y administrativa de un gimnasio moderno.

Esta API está documentada bajo el estándar <ins>**OpenAPI/Swagger**</ins> y protegida mediante autenticación robusta por tokens.

## Especificaciones Técnicas

| Descripción | Tecnología | Versión |
| :--- | :---: | :---: |
| Lenguaje de Programación | `Python` | 3.13 o superior |
| Framework Backend | `FastAPI` | 0.136.1 o superior |
| Mapeador de Objeto-Relacional (ORM) | `SQLAlchemy` | 2.0.49 o superior |
| Controlador Asíncrono de BD | `Asyncpg` | 0.31 o superior |
| Motor de Base de Datos | `PostgreSQL` | 18.3 o superior |
| Sistema de Control de Versiones | `Git` | 2.54 o superior |

## Características Principales de la API

El backend del sistema está diseñado bajo una arquitectura **RESTful**, garantizando escalabilidad, consistencia en los datos y seguridad perimetral. Sus características técnicas clave incluyen:

*   **Control de Acceso Basado en Roles (RBAC):** Restricción estricta de endpoints sensibles (escritura/modificación) exclusiva para los roles de `Administración`, `Finanzas` y `Entrenadores`, manteniendo consultas públicas controladas para los `Clientes`.
*   **Paginación y Escalabilidad:** Endpoints de listado masivo parametrizados de forma nativa mediante query parameters (`page` y `size`), con un límite operativo máximo de 100 registros por solicitud para optimizar el rendimiento de la base de datos.
*   **Transaccionalidad Atómica y Consistencia:** Protección contra inconsistencias comerciales, tales como el bloqueo automático de duplicidad de membresías activas o la anulación total de una venta en tienda si existe insuficiencia de stock en alguno de los artículos seleccionados.
*   **Integración de Hardware en Tiempo Real:** Optimización de tiempos de respuesta en endpoints específicos pensados para su consumo directo por sistemas de acceso físicos (torniquetes o lectores biométricos).

## Pasos para Levantar el Proyecto

## Opción 1: En Entorno Local

### Requisitos Previos

Antes de seguir los pasos siguientes, debe instalar:

*   **Python 3.10+**
*   **Git**
*   **PostgreSQL 16+ (Instalado y configurado con su usuario y contraseña)**

Siga las siguientes instrucciones a continuación para clonar, configurar e iniciar el entorno de desarrollo local en su computadora.

### 1. Clonar el Repositorio y Moverse a la Rama de Trabajo
Abra la terminal Git Bash y ejecute los comandos para clonar el proyecto y acceder a la rama con los últimos avances:

```bash
# Clona el repositorio desde GitHub al repositorio local
git clone https://github.com/laboratorio-1-2026-1/lab1-proyecto-2026-1-30042771-28220294-31025997.git

# Posicionarse en la carpeta del repositorio local
cd lab1-proyecto-2026-1-30042771-28220294-31025997

# Revisa y descarga los últimos cambios del repositorio remoto
git fetch origin

# Crea una copia en el repositorio local de la rama y se posiciona en ella
git checkout main
```
### 2. Configuración de la Base de Datos Local

- Abra **pgAdmin 4** (o su gestor de PostgreSQL preferido) y conéctese a su servidor local empleando las credenciales de su usuario postgres.
- Haga clic derecho sobre la sección `Databases`, seleccione `Create` <kbd>-></kbd> `Database...` y cree una base de datos vacía llamada `smartgym`.

<ins>*Nota*</ins>: No es necesario crear tablas manualmente; el ORM se encargará de mapear la estructura automáticamente al iniciar la aplicación.

### 3. Creación y Activación del Entorno Virtual

Genere un entorno virtual en la raíz del proyecto y actívelo.

```bash
# Crea el entorno virtual
python -m venv envi

# Activa el entorno virtual (en Windows):
envi/Scripts/Activate.ps1

# Activa el entorno virtual (en Mac/Linux):
source envi/Scripts/activate
```

### 4. Instalación de Dependencias

Con el entorno virtual activado, instale todos los módulos de FastAPI, SQLAlchemy y utilidades requeridas por el sistema.

```bash
# Instala la lista de dependencias del proyecto
pip install -r requirements.txt
```

### 5. Configuración de Variables de Entorno

Cree un archivo de texto plano en la raíz del proyecto y nómbrelo estrictamente como `.env`. Copie
el contenido del archivo `.env.example` dentro del archivo `.env` que acaba de crear y configure 
la siguiente estructura con sus credenciales locales:

`DATABASE_USER` -> Nombre de usuario de base de datos. Por defecto, 'postgres'.
`DATABASE_PASSWORD` -> Contraseña definida al instalar PostgreSQL. Reemplazar por la suya.
`DATABASE_NAME_DB` -> Nombre de la base de datos local a conectar. Por defecto, 'smartgym'.
`DATABASE_HOST` -> Host para conexión con base de datos. Por defecto, 'localhost'.
`DATABASE_PORT` -> Puerto para conexión con la base de datos. Por defecto, '5432'.
`DATABASE_URL` -> URL de conexión final a la base de datos. Toma todos los valores definidos
                en las variables anteriores (no necesita modificarse directamente).
`SECRET_KEY` -> Clave API secreta para firmar tokens JWT:

*Nota*:
Si tiene OpenSSL instalado, genere una clave API con el comando: `openssl rand -hex 32`.
Si solo cuenta con Python, utilice en la terminal: 
`python -c 'import secrets; print(secrets.token_hex(32))'`

`ALGORITHM` -> Algoritmo para gestión de firmas de tokens. Por defecto: 'HS256'.
`ACCESS_TOKEN_DURATION` -> Duración en minutos de los tokens de acceso. Puede cambiarse. Por defecto, 30.

Una vez configuradas las variables de entorno anteriores, el contenido de su archivo `.env` debe
verse como el siguiente ejemplo:

```env
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "clave_super_secreta"
DATABASE_NAME_DB = "smartgym"
DATABASE_HOST = "localhost"
DATABASE_PORT = "5432"
DATABASE_URL = "postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME_DB}"

SECRET_KEY="su_clave_secreta_encriptacion_jwt"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 6. Inicialización del Servidor de Desarrollo

Para poner en marcha el backend de la API con el sistema de autorecarga en tiempo real incorporado, ejecute el siguiente comando en la terminal.

```bash
# Inicializa el servidor
uvicorn app.main:app --reload
```

Una vez que el servidor reporte un estado exitoso, podrá acceder a la documentación interactiva en vivo abriendo su navegador web en la siguiente dirección:

- **Swagger UI (OpenAPI)**: `http://127.0.0.1:8000/docs`

### 7. Población Inicial de la Base de Datos (Seeding)

Carga los datos maestros iniciales (roles por defecto, planes base y usuarios administradores de prueba) en la base de datos `smartgym`.

Con el entorno virtual (`envi`) activo, ejecute el script automatizado de población ejecutando el siguiente comando:

```bash
# Ejecuta el script de carga de datos iniciales
python scripts/seed.py
```

## Opción 2: Usando Docker (Recomendado)

### Requisitos Previos

Antes de seguir los pasos siguientes, debe instalar:

*   **Docker Desktop (Incluye Compose y Docker Engine)**
*   **Git**

Ejecutar el proyecto con Docker le evita la instalación de Python y PostgreSQL. Siga los pasos
siguientes para lograrlo:

### 1. Clonar el Repositorio y Ubicarse en la Rama de Trabajo Principal (Main)
Abra la terminal Git Bash y ejecute los comandos para clonar el proyecto y acceder a la rama con los últimos avances:

```bash
# Clona el repositorio desde GitHub al repositorio local
git clone https://github.com/laboratorio-1-2026-1/lab1-proyecto-2026-1-30042771-28220294-31025997.git

# Posicionarse en la carpeta del repositorio local
cd lab1-proyecto-2026-1-30042771-28220294-31025997

# Revisa y descarga los últimos cambios del repositorio remoto
git fetch origin

# Crea una copia en el repositorio local de la rama y se posiciona en ella
git checkout main
```

### 2. Configuración de Variables de Entorno

Cree un archivo de texto plano en la raíz del proyecto y nómbrelo estrictamente como `.env`. Copie
el contenido del archivo `.env.example` dentro del archivo `.env` que acaba de crear y configure 
la estructura con sus credenciales locales:

`DATABASE_USER` -> Nombre de usuario de base de datos. Por defecto, 'postgres'.
`DATABASE_PASSWORD` -> Contraseña definida al instalar PostgreSQL. Reemplazar por la suya.
`DATABASE_NAME_DB` -> Nombre de la base de datos local a conectar. Por defecto, 'smartgym'.
`DATABASE_HOST` -> Para la ejecución con Docker, debe ser estrictamente *db*.
`DATABASE_PORT` -> Puerto para conexión con la base de datos. Por defecto, '5432'.
`DATABASE_URL` -> URL de conexión final a la base de datos. Toma todos los valores definidos
                en las variables anteriores (no necesita modificarse directamente).
`SECRET_KEY` -> Clave API secreta para firmar tokens JWT.
`ALGORITHM` -> Algoritmo para gestión de firmas de tokens. Por defecto: 'HS256'.
`ACCESS_TOKEN_DURATION` -> Duración en minutos de los tokens de acceso. Puede cambiarse. Por defecto, 30

Una vez configuradas las variables de entorno anteriores, el contenido de su archivo `.env` debe
verse como el siguiente ejemplo:

```env
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "clave_super_secreta"
DATABASE_NAME_DB = "smartgym"
DATABASE_HOST = "db"
DATABASE_PORT = "5432"
DATABASE_URL = "postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME_DB}"

SECRET_KEY="su_clave_secreta_encriptacion_jwt"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

*Nota*: Puede consultar más información de las variables de entorno examinando el contenido del archivo `.env.example`.

### 3. Levantamiento de Contenedores

Para construir y levantar los contenedores del sistema, ejecute el siguiente comando en su terminal:

```bash
# Para iniciar los contenedores en primer plano.
docker compose up --build

# Para iniciar los contenedores en segundo plano (si desea seguir usando su terminal inicial).
docker compose up --build -d
```

Para detener los contenedores y liberar recursos de su equipo, detenga el proceso con el comando
`Ctrl + C` y ejecute los siguientes comandos para limpiar su entorno:

```bash
# Para detener y eliminar los contenedores (conserva las imágenes base).
docker compose down

# Para detener y eliminar los contenedores, y limpiar la base de datos.
docker compose down -v
```

## Estructura del Proyecto

El backend está organizado bajo un patrón modular y limpio que separa las responsabilidades de transporte, lógica de negocio, persistencia de datos y esquemas de validación:

```properties
lab1-proyecto-2026-1-30042771-28220294-31025997
|
├── app/                            # Directorio principal del código fuente del backend de la API
|   ├── core/                       # Configuraciones globales (seguridad, tokens, manejo de errores)
|   │   ├── config.py               # Orquestador del ciclo de vida y validación de variables de entorno
|   │   ├── enums.py                # Catálogo de tipos enumerados estrictos para las reglas del negocio
|   │   ├── errors.py               # Jerarquía de excepciones personalizadas basadas en códigos HTTP
|   │   ├── exception_manager.py    # Gestor centralizado e interceptor de excepciones globales de la API
|   │   ├── security.py             # Gestión de Hashes criptográficos (pwdlib) y ciclo de vida de JWT
|   │   └── utils.py                # Inyección de dependencias de sesión y validador de Roles dinámicos
|   │
|   ├── database/                   # Conexión y ciclo de vida de la base de datos
|   │   └── session.py              # Proveedor de sesiones asíncronas (get_session_db)
|   │
|   ├── models/                     # Modelos de entidades de SQLAlchemy (Mapeo de base de datos)
|   ├── repositories/               # Capa de persistencia y consultas directas a la base de datos
|   ├── routers/                    # Controladores API (Definición de rutas, métodos HTTP y Swagger)
|   ├── schemas/                    # Modelos de validación de datos Pydantic (Entradas/Salidas DTO)
|   ├── services/                   # Capa de lógica de negocio pura y reglas del software
|   |
|   └── main.py                     # Punto de entrada de FastAPI e inclusión de routers globales
|
├── envi/                           # Entorno virtual local (Aislado de dependencias globales)
├── scripts/                        # Scripts automatizados de mantenimiento y desarrollo
|   ├── seed_data.sql               # Sentencias SQL con registros maestros de configuración
|   └── seed.py                     # Script transaccional y asíncrono ejecutor del archivo SQL
|
├── .dockerignore                   # Archivos excluidos en la creación de contenedores.
├── .env                            # Archivo confidencial con credenciales y variables de entorno
├── .env.example                    # Plantilla guía para la configuración de credenciales
├── .gitignore                      # Archivos excluidos del control de versiones (ej: envi/, .env)
├── docker-compose.yml              # Orquestador para el levantamiento de contenedores (API y PostgreSQL).
├── Dockerfile                      # Archivo para definir la imágen Docker de la API.
├── entrypoint.sh                   # Script de bash para la ejecución con Docker.
├── README.md                       # Documentación general del proyecto
└── requirements.txt                # Lista de librerías del proyecto con sus versiones exactas
```

## ¿Cómo Probar la API?

Para interactuar con los endpoints protegidos desde la interfaz de **Swagger UI**, siga este flujo básico de autenticación:

1. Inicie el servidor con <kbd>uvicorn</kbd> y diríjase a `http://127.0.0.1:8000/docs`.
2. Despliegue el módulo de **Autenticación** y busque el endpoint `POST /api/v1/auth/token`.
3. Haga clic en <kbd>**Try it out**</kbd> e introduzca las credenciales de alguno de los usuarios maestros de prueba.

A continuación, se detallan las cuentas disponibles en el entorno local según el rol que desee evaluar:

| Rol de Acceso | Username (Correo) | Password (Contraseña) | Acceso |
| :--- | :--- | :--- | :--- |
| **Administrador** | `administrador@smartgym.com` | `admin123` | Acceso total, gestión de personal, planes y reportes globales. |
| **Finanzas** | `finanzas@smartgym.com` | `finanzas123` | Monitoreo contable, facturación y auditoría de ingresos por planes. |
| **Entrenador** | `entrenador1@smartgym.com` | `entrenador123` | Gestión de agendas operativas y sesiones de clases asignadas. |
| **Cliente** | `cliente@gmail.com` | `cliente123` | Reserva de clases dirigidas y consultas del perfil de membresía. |

4. Ejecute la petición y **copie el valor del campo `access_token`** generado en la respuesta JSON (sin las comillas).
5. Suba al inicio de la página de Swagger, haga clic en el botón **Authorize** (icono de candado), pegue el token en el campo de texto y presione *Authorize*.
6. En este punto contará con los permisos del rol con el que haya ingresado para ejecutar, registrar y probar los endpoints restringidos de las secciones accesibles para el mismo.

## Autores

Desarrollado como entrega académica para la asignatura Laboratorio I por:

- Ricardo Andrés González - C.I. 31.025.997
- Genesis Nazareth Carrasco - C.I. 30.042.771
- José Ángel Mendoza - C.I. 28.220.294