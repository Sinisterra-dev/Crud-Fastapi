from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

# Importamos schemas y modelos
import schemas.user
import models.user

# Importamos dependencias de base de datos y servicios
from core.database import get_db
from core.security import verify_token
import services.auth_service as auth_service


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)


# ------------------------------------------------------------
# DEPENDENCIA PARA OBTENER USUARIO ACTUAL
# ------------------------------------------------------------

def get_current_user(
    token: str = Depends(...),  # Se inyectará desde el header Authorization
    db: Session = Depends(get_db)
) -> models.user.User:
    """
    Dependencia para obtener el usuario autenticado desde el token JWT.
    
    ### Proceso:
    1. Extrae el token del header Authorization (formato: "Bearer <token>")
    2. Verifica y decodifica el token usando verify_token()
    3. Busca el usuario en la base de datos usando el email del token
    4. Retorna el usuario autenticado
    
    ### Errores:
    - 401: Si el token es inválido, ha expirado o el usuario no existe
    
    ### Uso típico:
    Se usa como dependencia en endpoints protegidos:
    @router.get("/auth/me")
    def get_profile(current_user: User = Depends(get_current_user)):
        return current_user
    
    ### PRÓXIMOS ENDPOINTS QUE UTILIZARÁ ESTA DEPENDENCIA:
    - GET /auth/me (ya implementado)
    - PUT /auth/me (actualizar perfil)
    - PATCH /auth/me/password (cambiar contraseña)
    - DELETE /auth/me (eliminar cuenta)
    - Cualquier endpoint protegido del sistema (tasks, categories, etc.)
    """
    # NOTA: En una implementación completa, esto debería usar OAuth2PasswordBearer
    # de FastAPI para extraer el token del header Authorization automáticamente.
    # Por simplicidad, aquí asumimos que el token se pasa directamente.
    
    # Verificar el token y obtener el email
    email = verify_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar el usuario por email
    user = auth_service.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# ------------------------------------------------------------
# POST /auth/register - Registrar nuevo usuario
# ------------------------------------------------------------
@router.post(
    "/register",
    response_model=schemas.user.UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Autenticación"],
    summary="Registrar un nuevo usuario"
)
def register(
    user: schemas.user.UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario en el sistema.
    
    ### Cuerpo del request (JSON):
    ```json
    {
        "username": "jose_roberto",
        "email": "jose@example.com",
        "password": "password123"
    }
    ```
    
    ### Campos:
    - **username** (obligatorio, min 3 caracteres): Nombre de usuario único
    - **email** (obligatorio): Email válido y único
    - **password** (obligatorio, min 8 caracteres): Contraseña del usuario
    
    ### Respuesta exitosa (201 Created):
    ```json
    {
        "id": 1,
        "username": "jose_roberto",
        "email": "jose@example.com",
        "role": "user",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00"
    }
    ```
    
    ### Errores:
    - 400: Si el email o username ya están registrados
    - 422: Si los datos no cumplen las validaciones
    
    ### NOTA DE SEGURIDAD:
    La contraseña NUNCA se devuelve en la respuesta. Solo se almacena el hash.
    """
    try:
        # Crear el usuario usando el servicio
        db_user = auth_service.create_user(db, user)
        return db_user
    except ValueError as e:
        # Si el email o username ya existen
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ------------------------------------------------------------
# POST /auth/login - Iniciar sesión
# ------------------------------------------------------------
@router.post(
    "/login",
    response_model=schemas.user.Token,
    tags=["Autenticación"],
    summary="Iniciar sesión y obtener token JWT"
)
def login(
    user_credentials: schemas.user.UserLogin,
    db: Session = Depends(get_db)
):
    """
    Autentica un usuario y devuelve un token JWT.
    
    ### Cuerpo del request (JSON):
    ```json
    {
        "email": "jose@example.com",
        "password": "password123"
    }
    ```
    
    ### Campos:
    - **email** (obligatorio): Email del usuario
    - **password** (obligatorio): Contraseña del usuario
    
    ### Respuesta exitosa (200 OK):
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    ```
    
    ### Errores:
    - 401: Si el email no existe o la contraseña es incorrecta
    
    ### CÓMO USAR EL TOKEN:
    El cliente debe incluir el token en el header Authorization de requests subsiguientes:
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    
    ### PRÓXIMOS ENDPOINTS RELACIONADOS:
    - POST /auth/refresh (refrescar token cuando esté próximo a expirar)
    - POST /auth/logout (invalidar token - requiere blacklist o implementación específica)
    - POST /auth/forgot-password (iniciar recuperación de contraseña)
    - POST /auth/reset-password (completar recuperación de contraseña)
    """
    # Autenticar al usuario
    user = auth_service.authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        # Credenciales inválidas
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar si el usuario está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado. Contacte al administrador."
        )
    
    # Crear y retornar el token JWT
    token = auth_service.create_user_token(user)
    return token


# ------------------------------------------------------------
# GET /auth/me - Obtener perfil del usuario actual
# ------------------------------------------------------------
@router.get(
    "/me",
    response_model=schemas.user.UserResponse,
    tags=["Autenticación"],
    summary="Obtener perfil del usuario autenticado"
)
def get_me(
    current_user: models.user.User = Depends(get_current_user)
):
    """
    Obtiene el perfil del usuario autenticado.
    
    ### Autenticación requerida:
    Este endpoint requiere el token JWT en el header Authorization:
    ```
    Authorization: Bearer <access_token>
    ```
    
    ### Respuesta exitosa (200 OK):
    ```json
    {
        "id": 1,
        "username": "jose_roberto",
        "email": "jose@example.com",
        "role": "user",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00"
    }
    ```
    
    ### Errores:
    - 401: Si el token es inválido, ha expirado o no se proporciona
    
    ### PRÓXIMOS ENDPOINTS RELACIONADOS:
    - PUT /auth/me (actualizar perfil completo: username, email)
    - PATCH /auth/me (actualización parcial del perfil)
    - PATCH /auth/me/password (cambiar contraseña - requiere contraseña actual)
    - DELETE /auth/me (eliminar cuenta del usuario)
    - GET /auth/me/tasks (obtener tareas del usuario actual)
    - GET /auth/me/activity (obtener historial de actividad del usuario)
    """
    return current_user
