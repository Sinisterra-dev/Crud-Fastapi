from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from core.config import settings

# Contexto para el hash de contraseñas usando bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ------------------------------------------------------------
# FUNCIONES DE HASH DE CONTRASEÑAS
# ------------------------------------------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con el hash almacenado.
    
    ### Parámetros:
    - plain_password: Contraseña proporcionada por el usuario (texto plano)
    - hashed_password: Hash almacenado en la base de datos
    
    ### Retorna:
    - True si la contraseña es correcta, False si no
    
    ### Uso típico:
    Se usa durante el login para verificar las credenciales del usuario.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña en texto plano.
    
    ### Parámetros:
    - password: Contraseña en texto plano
    
    ### Retorna:
    - Hash de la contraseña (para almacenar en la base de datos)
    
    ### Uso típico:
    Se usa al registrar un nuevo usuario para almacenar su contraseña de forma segura.
    NUNCA se debe almacenar la contraseña en texto plano.
    """
    return pwd_context.hash(password)


# ------------------------------------------------------------
# FUNCIONES DE TOKEN JWT
# ------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso.
    
    ### Parámetros:
    - data: Diccionario con los datos a codificar en el token (usualmente el user_id o email)
    - expires_delta: Tiempo de expiración del token (opcional, usa default si no se proporciona)
    
    ### Retorna:
    - Token JWT codificado como string
    
    ### Uso típico:
    Se usa después de un login exitoso para generar el token que el cliente usará
    para autenticarse en requests subsiguientes.
    
    ### Estructura del token:
    El token contiene:
    - sub (subject): identificador del usuario (usualmente email o user_id)
    - exp (expiration): timestamp de expiración
    - iat (issued at): timestamp de creación
    """
    to_encode = data.copy()
    
    # Si no se proporciona expiración, usa el default (ej: 30 minutos)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    
    # Codifica el token usando la SECRET_KEY y el algoritmo configurado
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verifica y decodifica un token JWT.
    
    ### Parámetros:
    - token: Token JWT proporcionado por el cliente (usualmente en el header Authorization)
    
    ### Retorna:
    - Email del usuario si el token es válido
    - None si el token es inválido o ha expirado
    
    ### Uso típico:
    Se usa en los endpoints protegidos para verificar que el token del cliente es válido
    y extraer el email del usuario autenticado.
    
    ### Errores que maneja:
    - JWTError: Token malformado o inválido
    - ExpiredSignatureError: Token ha expirado
    """
    try:
        # Decodifica el token usando la SECRET_KEY y el algoritmo
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            return None
        
        return email
    except JWTError:
        return None
