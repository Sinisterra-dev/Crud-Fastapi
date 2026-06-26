from typing import Optional, List

# datetime: tipo de dato para fechas y horas
from datetime import datetime

# BaseModel: clase base de Pydantic. Todos tus schemas heredan de ella
# Field: permite agregar metadatos y validaciones extra a los campos
from pydantic import BaseModel, Field
# ============================================================
# SCHEMAS DE CATEGORY (Categoría)
# ============================================================
# Seguimos el patrón: Base -> Create -> Update -> Response
#
# PATRÓN DE SCHEMAS:
#   CategoryBase    : campos comunes (compartidos por todos)
#   CategoryCreate  : campos para CREAR (hereda de Base)
#   CategoryUpdate  : campos para ACTUALIZAR (todos opcionales)
#   CategoryResponse: lo que devuelve la API (incluye id, etc.)
#
# ¿Por qué este patrón?
#   - Reutilización de código (no repetir campos)
#   - Control preciso sobre qué datos acepta vs. qué devuelve la API
#   - Seguridad: nunca expones campos internos que no deberías
# ============================================================

class CategoryBase(BaseModel):
    """
    Schema base con los campos comunes de una categoría.
    No se usa directamente en los endpoints, sino como base
    para los otros schemas.

    HERENCIA: CategoryCreate y CategoryUpdate heredan de aquí.
    """

    # Field() permite agregar:
    #   - description: se muestra en la documentación automática (/docs)
    #   - min_length: validación de longitud mínima
    #   - max_length: validación de longitud máxima
    #   - example: valor de ejemplo para la documentación
    name: str = Field(
        ...,                          # "..." = campo OBLIGATORIO (sin valor por defecto)
        min_length=1,
        max_length=50,
        description="Nombre único de la categoría",
        examples=["Trabajo"]
    )

    description: Optional[str] = Field(
        default=None,                 # None = campo OPCIONAL
        max_length=200,
        description="Descripción opcional de la categoría",
        examples=["Tareas relacionadas con el trabajo"]
    )


class CategoryCreate(CategoryBase):
    """
    Schema para CREAR una categoría.
    Hereda todos los campos de CategoryBase.
    En este caso no agrega campos nuevos, pero el patrón
    permite agregar campos específicos de creación en el futuro.

    Recibe: { "name": "Trabajo", "description": "..." }
    """
    pass  # pass = no agrega nada nuevo, solo hereda de CategoryBase


class CategoryUpdate(BaseModel):
    """
    Schema para ACTUALIZAR una categoría (PATCH/PUT).
    TODOS los campos son opcionales porque el usuario puede
    querer actualizar solo el nombre, solo la descripción, o ambos.

    Nota: NO hereda de CategoryBase porque aquí los campos son opcionales.
    En CategoryBase, "name" es obligatorio.

    Recibe: { "name": "Nuevo nombre" } o { "description": "Nueva desc" }
    """
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Nuevo nombre de la categoría"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Nueva descripción"
    )


class CategoryResponse(CategoryBase):
    """
    Schema de RESPUESTA para una categoría.
    Esto es lo que la API devuelve al cliente.
    Hereda de CategoryBase (name, description) y agrega
    el campo "id" que solo existe después de crear en la BD.

    ¿Por qué no incluir "id" en CategoryCreate?
        El "id" lo asigna la BD automáticamente (autoincrement).
        El usuario no debe (ni puede) enviarlo al crear.
        Solo lo devolvemos en la respuesta.
    """
    id: int  # El id que la BD asignó automáticamente

    # model_config con from_attributes=True es FUNDAMENTAL:
    # Le dice a Pydantic que puede crear este schema a partir de
    # un objeto SQLAlchemy (que usa atributos, no diccionarios).
    #
    # Sin esto, Pydantic esperaría un diccionario y fallaría
    # al recibir un objeto Task/Category de SQLAlchemy.
    #
    # En Pydantic v1 esto era: class Config: orm_mode = True
    # En Pydantic v2 es: model_config = ConfigDict(from_attributes=True)
    model_config = {"from_attributes": True}