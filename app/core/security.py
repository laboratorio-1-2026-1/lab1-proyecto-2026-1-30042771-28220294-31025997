from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, status
from datetime import datetime, timedelta, UTC

from app.core.config import settings # Importacion para cargar variables de entorno.

# Definicion de esquema OAuth2 para proteccion de endpoints y URL para envio de credenciales.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# Creacion de utilidad para el manejo de las claves de usuario, con la configuracion recomendada.
password_hash = PasswordHash.recommended()

def get_password_hash(plain_password: str):
    """Funcion para obtener el hash de una clave ingresada por el usuario."""
    return password_hash.hash(plain_password)

def verify_password(password_to_verify: str, clave_hash: str):
    """
    Funcion para comparar la clave de usuario enviada para inicio de sesion contra la almacenada 
    en base de datos.
    """
    return password_hash.verify(password_to_verify, clave_hash)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Funcion para crear Bearer Tokens de acceso (bajo estandar JWT)."""
    # Se copia el contenido del token para codificar.
    to_encode = data.copy()

    # Se valida si se proporciona un tiempo de expiracion. En caso negativo, se asigna la hora
    # actual (UTC) mas el tiempo definido en las variables de entorno.
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_DURATION)

    # Se actualiza la carga util del Token con la fecha de expiracion.
    to_encode.update({"exp": expire})

    # Se codifica la carga util del Token, aplicando la clave secreta y algoritmo definidos en las
    # variables de entorno para firmarlo.
    encoded_jwt = jwt.encode(to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # Se retorna el token.
    return encoded_jwt

def validate_access_token(token: str):
    """Funcion para verificar la validez de un Token."""
    
    try:
        # Se decodifica el token y se obtiene su propietario (usuario).
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        username = payload.get("sub")

        # Si no tiene propietario, lanzamos una excepcion.
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudieron validar las credenciales.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
    # Si el proceso de decodificacion falla, lanzamos una excepcion.
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Se retorna la carga util del token decodificada.
    return payload

# =======
# NOTA: En este archivo no se emplean las clases de error definidas, para cumplir con la 
#       especificacion general (incluir el header, {"WWW-Authenticate": "Bearer"}).
# =======
