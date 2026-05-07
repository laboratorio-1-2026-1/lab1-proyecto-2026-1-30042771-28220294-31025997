import os
import sys
from dotenv import load_dotenv

# Carga de variables de entorno en proceso actual.
load_dotenv()

class Global_settings():

    # Se cargan las variables de entorno para la configuracion de la aplicacion.
    access_token_var = os.getenv("ACCESS_TOKEN_DURATION", 30)
    database_url_var = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    # Si alguna de las variables de entorno principales no se encuentra, se cierra la 
    # ejecucion de la aplicacion.
    if database_url_var is None:
        print("ERROR: URL de base de datos no encontrada.")
        sys.exit(1)

    if SECRET_KEY is None:
        print("ERROR: Clave API secreta no encontrada.")
        sys.exit(1)

    if ALGORITHM is None:
        print("ERROR: Algoritmo de encriptación no encontrado.")
        sys.exit(1)
    
    # Se modifica la URL de la base de datos para incluir el driver utilizado para la conexion.
    DATABASE_URL = database_url_var.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Se convierte la valor de la duracion del token (en minutos) a un entero.
    ACCESS_TOKEN_DURATION = int(access_token_var)

# Creacion de objeto para importacion de variables de configuracion en otros archivos.
settings = Global_settings()
