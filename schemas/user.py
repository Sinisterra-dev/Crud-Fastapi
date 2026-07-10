from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime


# UserBase: Clase base que contiene los campos comunes para todas las operaciones de usuario.
# Sirve como fundamento para otras clases de esquema, evitando la duplicación de código.
# Se utiliza para definir los campos esenciales que todo usuario debe tener.
class UserBase (BaseModel):
    username: str = Field(
        ...,  # "..." = campo OBLIGATORIO (sin valor por defecto)
        min_length=3,
        max_length=50,
        description="Nombre del usuario",
        examples=["José Roberto"]
    )
    email: EmailStr = Field(
        ...,  # "..." = campo OBLIGATORIO (sin valor por defecto)
        description="email del usuario",
        examples=["ejemplo@gmail.com"]
    )


# UserCreate: Hereda de UserBase y agrega el campo password.
# Se utiliza específicamente para la creación de nuevos usuarios (endpoint de registro).
# El password se incluye aquí porque es necesario al crear un usuario, pero no se debe exponer en respuestas.
class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Contraseña del usuario (mínimo 8 caracteres)",
        examples=["password123"]
    )


# UserResponse: Hereda de UserBase y agrega campos adicionales que se devuelven al cliente.
# Se utiliza para las respuestas de la API cuando se consulta información de un usuario.
# Incluye campos generados por el sistema como id, role, is_active, created_at y updated_at.
# NO incluye el password por razones de seguridad.
# from_attributes=True permite convertir objetos SQLAlchemy a Pydantic automáticamente.
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(
        ...,
        description="ID único del usuario en la base de datos",
        examples=[1]
    )
    role: str = Field(
        default="user",
        description="Rol del usuario (ej: 'user', 'admin')",
        examples=["user"]
    )
    is_active: bool = Field(
        default=True,
        description="Indica si el usuario está activo o no",
        examples=[True]
    )
    created_at: datetime = Field(
        ...,
        description="Fecha y hora de creación del usuario",
        examples=["2024-01-01T00:00:00"]
    )
    updated_at: datetime = Field(
        ...,
        description="Fecha y hora de la última actualización del usuario",
        examples=["2024-01-15T12:30:00"]
    )


# UserLogin: Clase independiente diseñada específicamente para el endpoint de login/autenticación.
# No hereda de UserBase porque solo requiere email y password, no username.
# Es más ligera y específica para el flujo de autenticación.
class UserLogin(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Email del usuario para autenticación",
        examples=["ejemplo@gmail.com"]
    )
    password: str = Field(
        ...,
        description="Contraseña del usuario para autenticación",
        examples=["password123"]
    )


# Token: Schema para la respuesta del endpoint de login con JWT.
# Devuelve el access_token generado y el tipo de token (usualmente 'bearer').
# Este es el formato estándar para respuestas de autenticación OAuth2/JWT.
class Token(BaseModel):
    access_token: str = Field(
        ...,
        description="Token JWT de acceso para autenticar requests",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo de token (generalmente 'bearer' para JWT)",
        examples=["bearer"]
    )


