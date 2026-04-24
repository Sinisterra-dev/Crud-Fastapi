# ============================================================
# SCHEMAS.PY - Esquemas Pydantic (Validación de datos)
# ============================================================
# Pydantic es la librería que FastAPI usa para:
#   1. VALIDAR datos de entrada (request body, parámetros)
#   2. SERIALIZAR datos de salida (convertir objetos a JSON)
#   3. DOCUMENTAR automáticamente la API
#
# ¿POR QUÉ SCHEMAS SEPARADOS DE LOS MODELOS?
#   Los modelos SQLAlchemy (models.py) representan la BD.
#   Los schemas Pydantic representan lo que la API acepta/devuelve.
#   Son capas diferentes con responsabilidades diferentes:
#
#   ENTRADA (request):
#     Usuario envía JSON --> Pydantic lo valida --> SQLAlchemy lo guarda
#
#   SALIDA (response):
#     SQLAlchemy devuelve objeto --> Pydantic lo serializa --> JSON al usuario
#
# CONCEPTOS QUE DEBES DOMINAR:
#   - Type hints en Python (int, str, Optional, List, etc.)
#   - Clases y herencia en Python
#   - ¿Qué es la validación de datos?
#   - ¿Qué es JSON?
#   - ¿Qué es serialización/deserialización?
#   - Decoradores en Python (@algo)
# ============================================================

# Optional: tipo que puede ser None o el tipo especificado
# List: lista tipada (List[str] = lista de strings)
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


# ============================================================
# SCHEMAS DE TASK (Tarea)
# ============================================================
# Mismo patrón: Base -> Create -> Update -> Response
# ============================================================

class TaskBase(BaseModel):
    """
    Schema base con los campos comunes de una tarea.
    Compartido por TaskCreate y como referencia para TaskUpdate.
    """

    title: str = Field(
        ...,              # Obligatorio
        min_length=1,
        max_length=100,
        description="Título de la tarea",
        examples=["Estudiar FastAPI"]
    )

    description: Optional[str] = Field(
        default=None,     # Opcional
        description="Descripción detallada de la tarea",
        examples=["Leer la documentación oficial de FastAPI"]
    )

    # ge=1, le=3: "greater or equal to 1, less or equal to 3"
    # Pydantic validará que priority esté entre 1 y 3
    priority: int = Field(
        default=1,
        ge=1,             # >= 1 (mínimo 1)
        le=3,             # <= 3 (máximo 3)
        description="Prioridad: 1=Baja, 2=Media, 3=Alta"
    )

    # ID de la categoría a la que pertenece (opcional)
    # Si es None, la tarea no tiene categoría
    category_id: Optional[int] = Field(
        default=None,
        description="ID de la categoría (opcional)",
        examples=[1]
    )


class TaskCreate(TaskBase):
    """
    Schema para CREAR una tarea.
    Hereda de TaskBase: title, description, priority, category_id.

    Recibe:
    {
        "title": "Estudiar FastAPI",
        "description": "Leer la documentación",
        "priority": 2,
        "category_id": 1
    }
    """
    pass


class TaskUpdate(BaseModel):
    """
    Schema para ACTUALIZAR una tarea (PATCH - actualización parcial).
    TODOS los campos son opcionales: el usuario puede enviar
    solo los campos que quiere cambiar.

    Ejemplo - Solo marcar como completada:
        PATCH /tasks/1
        { "completed": true }

    Ejemplo - Cambiar título y prioridad:
        PATCH /tasks/1
        { "title": "Nuevo título", "priority": 3 }
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)
    completed: Optional[bool] = Field(default=None)
    priority: Optional[int] = Field(default=None, ge=1, le=3)
    category_id: Optional[int] = Field(default=None)


class TaskResponse(TaskBase):
    """
    Schema de RESPUESTA para una tarea.
    Esto es lo que el cliente recibe cuando consulta una tarea.

    Agrega a los campos de TaskBase:
    - id: asignado por la BD
    - completed: estado actual
    - created_at: cuándo se creó
    - updated_at: cuándo se actualizó por última vez
    - category: el objeto Category anidado (si tiene categoría)

    DATO INTERESANTE - "category" anidado:
        En vez de devolver solo category_id (un número),
        devolvemos el objeto Category completo.
        Esto se llama "eager loading" o respuesta anidada.
        Es útil para el frontend que no tiene que hacer
        otra petición para obtener la info de la categoría.
    """
    id: int
    completed: bool

    # Estos campos vienen de la BD automáticamente
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Objeto Category anidado (puede ser None si no tiene categoría)
    # CategoryResponse es el schema que definimos arriba
    category: Optional[CategoryResponse] = None

    # Necesario para convertir objetos SQLAlchemy a Pydantic
    model_config = {"from_attributes": True}


# ============================================================
# SCHEMAS PARA RESPUESTAS DE LISTA
# ============================================================
# Cuando devolvemos múltiples tareas o categorías, es útil
# incluir metadatos como el total de elementos.
# ============================================================

class TaskListResponse(BaseModel):
    """
    Schema para la respuesta de lista de tareas.
    Incluye metadatos útiles para el cliente:
    - total: cuántas tareas existen en total (para paginación)
    - tasks: la lista de tareas

    PAGINACIÓN: cuando hay muchos registros, no devuelves todos.
    Devuelves por páginas. El "total" ayuda al frontend a saber
    cuántas páginas mostrar.
    """
    total: int = Field(description="Total de tareas en la BD")
    tasks: List[TaskResponse] = Field(description="Lista de tareas")

    model_config = {"from_attributes": True}
