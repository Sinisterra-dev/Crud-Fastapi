from typing import Optional, List

# datetime: tipo de dato para fechas y horas
from datetime import datetime

# BaseModel: clase base de Pydantic. Todos tus schemas heredan de ella
# Field: permite agregar metadatos y validaciones extra a los campos
from pydantic import BaseModel, Field

from .category import CategoryResponse


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
