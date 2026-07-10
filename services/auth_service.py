from sqlalchemy.orm import Session
from typing import Optional
import models.user
import schemas.user
from core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from core.config import settings


# ------------------------------------------------------------
# SERVICIO DE AUTENTICACIÓN
# ------------------------------------------------------------

def get_user_by_email(db: Session, email: str) -> Optional[models.user.User]:
    """
    Busca un usuario por su email.
    
    ### Parámetros:
    - db: Sesión de SQLAlchemy
    - email: Email del usuario a buscar
    
    ### Retorna:
    - Objeto User si existe, None si no
    
    ### Uso típico:
    Se usa para verificar si un email ya está registrado (durante el registro)
    o para obtener el usuario durante el login.
    """
    return db.query(models.user.User).filter(models.user.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.user.User]:
    """
    Busca un usuario por su username.
    
    ### Parámetros:
    - db: Sesión de SQLAlchemy
    - username: Username del usuario a buscar
    
    ### Retorna:
    - Objeto User si existe, None si no
    
    ### Uso típico:
    Se usa para verificar si un username ya está registrado (durante el registro).
    """
    return db.query(models.user.User).filter(models.user.User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[models.user.User]:
    """
    Busca un usuario por su ID.
    
    ### Parámetros:
    - db: Sesión de SQLAlchemy
    - user_id: ID del usuario a buscar
    
    ### Retorna:
    - Objeto User si existe, None si no
    
    ### Uso típico:
    Se usa en el endpoint /auth/me para obtener el perfil del usuario autenticado.
    """
    return db.query(models.user.User).filter(models.user.User.id == user_id).first()


def create_user(db: Session, user: schemas.user.UserCreate) -> models.user.User:
    """
    Crea un nuevo usuario en la base de datos.
    
    ### Parámetros:
    - db: Sesión de SQLAlchemy
    - user: Schema UserCreate con los datos del nuevo usuario
    
    ### Retorna:
    - Objeto User creado (sin la contraseña en texto plano)
    
    ### Proceso:
    1. Verifica que el email no esté registrado
    2. Verifica que el username no esté registrado
    3. Hashea la contraseña (NUNCA almacenar en texto plano)
    4. Crea el usuario con la contraseña hasheada
    5. Guarda en la base de datos
    
    ### Excepciones que puede lanzar:
    - ValueError: Si el email o username ya existen
    """
    # Verificar si el email ya existe
    existing_email = get_user_by_email(db, user.email)
    if existing_email:
        raise ValueError(f"El email '{user.email}' ya está registrado")
    
    # Verificar si el username ya existe
    existing_username = get_user_by_username(db, user.username)
    if existing_username:
        raise ValueError(f"El username '{user.username}' ya está registrado")
    
    # Hashear la contraseña antes de almacenarla
    hashed_password = get_password_hash(user.password)
    
    # Crear el objeto User con la contraseña hasheada
    db_user = models.user.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role if hasattr(user, 'role') else "user"
    )
    
    # Guardar en la base de datos
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.user.User]:
    """
    Autentica un usuario verificando email y contraseña.
    
    ### Parámetros:
    - db: Sesión de SQLAlchemy
    - email: Email del usuario
    - password: Contraseña en texto plano
    
    ### Retorna:
    - Objeto User si las credenciales son correctas
    - None si el usuario no existe o la contraseña es incorrecta
    
    ### Proceso:
    1. Busca el usuario por email
    2. Si no existe, retorna None
    3. Si existe, verifica la contraseña usando el hash
    4. Si la contraseña es correcta, retorna el usuario
    5. Si la contraseña es incorrecta, retorna None
    
    ### Uso típico:
    Se usa en el endpoint de login para verificar las credenciales
    antes de generar el token JWT.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def create_user_token(user: models.user.User) -> schemas.user.Token:
    """
    Crea un token JWT para un usuario autenticado.
    
    ### Parámetros:
    - user: Objeto User autenticado
    
    ### Retorna:
    - Schema Token con access_token y token_type
    
    ### Proceso:
    1. Crea el payload del token con el email como subject (sub)
    2. Genera el token con el tiempo de expiración configurado
    3. Retorna el schema Token con el token generado
    
    ### Uso típico:
    Se usa después de un login exitoso para generar el token
    que se enviará al cliente.
    """
    # Crear el access token con el email como subject
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    # Retornar el schema Token
    return schemas.user.Token(access_token=access_token, token_type="bearer")
