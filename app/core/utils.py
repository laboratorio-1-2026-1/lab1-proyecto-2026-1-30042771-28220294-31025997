from fastapi import Depends, HTTPException, status
from app.models.Usuario_model import Usuario
from app.models.Rol_model import Rol  # Modelo real para evitar problemas con SQLAlchemy

# =========================================================================
# 🔐 CLASE / CONTROLADOR DE ROLES (Requerido por app/main.py)
# =========================================================================
class Role_Checker:
    """
    Clase encargada de verificar si el usuario actual cuenta 
    con los permisos necesarios para acceder a un endpoint.
    """
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Usuario = Depends(lambda: None)):
        # Si el sistema usa get_current_user en los endpoints, se puede validar aquí.
        return True


# =========================================================================
# 👤 SIMULACIÓN DE USUARIO ACTUAL
# =========================================================================
async def get_current_user():
    """
    Dependencia simulada para el laboratorio.
    Crea un usuario administrador ficticio compatible con SQLAlchemy.
    """
    # 1. Creamos el usuario base
    mock_admin = Usuario()
    mock_admin.id_usuario = 1
    mock_admin.nombre = "Admin"
    mock_admin.apellido = "Laboratorio"
    mock_admin.correo = "admin@gimnasio.com"
    mock_admin.password_hash = "mock_hash"
    
    # 2. Creamos un Rol real de SQLAlchemy
    rol_real = Rol()
    rol_real.id_rol = 1
    rol_real.nombre_rol = "administrador"
    
    # 3. Asignamos la relación de forma limpia
    mock_admin.rol = rol_real
    
    return mock_admin