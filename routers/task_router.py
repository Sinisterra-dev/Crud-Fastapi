from fastapi import FastAPI, HTTPException, Depends, Query, status, APIRouter

# Session: tipo de SQLAlchemy para type hints
from sqlalchemy.orm import Session

# List, Optional: tipos para type hints
from typing import List, Optional

# Importamos todo lo que creamos en los otros archivos
import models.task
import models.category
import schemas.task
import schemas.category
from core.database import engine, get_db, Base   # Conexión a la BD y generador de sesiones
from services import task_service as crud


router = APIRouter(
prefix="/api/tasks",
    tags=["Tasks"]
)

# ------------------------------------------------------------
# GET /tasks - Listar tareas (con filtros opcionales)
# ------------------------------------------------------------
@router.get(
    "/tasks",
    response_model=schemas.TaskListResponse,  # Incluye total + lista
    tags=["Tareas"],
    summary="Listar tareas con filtros opcionales"
)
def read_tasks(
    skip: int = Query(default=0, ge=0, description="Registros a saltar"),
    limit: int = Query(default=100, ge=1, le=200, description="Máximo de registros"),
    # Optional[bool]: puede ser True, False, o None (no filtrar)
    completed: Optional[bool] = Query(
        default=None,
        description="Filtrar por estado: true=completadas, false=pendientes"
    ),
    priority: Optional[int] = Query(
        default=None,
        ge=1,
        le=3,
        description="Filtrar por prioridad: 1=Baja, 2=Media, 3=Alta"
    ),
    db: Session = Depends(get_db)
):
    """
    Devuelve la lista de tareas con filtros opcionales.

    ### Parámetros de query:
    - **skip** / **limit**: paginación
    - **completed**: filtrar por estado (true/false)
    - **priority**: filtrar por prioridad (1, 2 o 3)

    ### Ejemplos de uso:
    ```
    GET /tasks                          -> todas las tareas
    GET /tasks?completed=false          -> solo tareas pendientes
    GET /tasks?completed=true           -> solo tareas completadas
    GET /tasks?priority=3               -> solo tareas de alta prioridad
    GET /tasks?completed=false&priority=3  -> pendientes y alta prioridad
    GET /tasks?skip=0&limit=10          -> primera página de 10 tareas
    ```

    ### Respuesta:
    ```json
    {
        "total": 25,
        "tasks": [...]
    }
    ```
    El campo `total` es útil para construir paginación en el frontend.
    """
    total, tasks = crud.get_tasks(
        db,
        skip=skip,
        limit=limit,
        completed=completed,
        priority=priority
    )
    # Construimos la respuesta usando el schema TaskListResponse
    return schemas.TaskListResponse(total=total, tasks=tasks)


# ------------------------------------------------------------
# POST /tasks - Crear una nueva tarea
# ------------------------------------------------------------
@router.post(
    "/tasks",
    response_model=schemas.TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tareas"],
    summary="Crear una nueva tarea"
)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva tarea.

    ### Cuerpo del request (JSON):
    ```json
    {
        "title": "Estudiar FastAPI",
        "description": "Leer la documentación oficial",
        "priority": 2,
        "category_id": 1
    }
    ```

    ### Campos:
    - **title** (obligatorio): nombre de la tarea
    - **description** (opcional): descripción detallada
    - **priority** (opcional, default 1): 1=Baja, 2=Media, 3=Alta
    - **category_id** (opcional): ID de la categoría

    ### Respuesta exitosa (201 Created):
    Devuelve la tarea creada con su ID, timestamps y el objeto categoría anidado.
    """
    # Si se especificó una categoría, verificamos que exista
    if task.category_id is not None:
        category = crud.get_category(db, task.category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con id={task.category_id} no encontrada"
            )

    return crud.create_task(db, task)


# ------------------------------------------------------------
# GET /tasks/{task_id} - Obtener una tarea por ID
# ------------------------------------------------------------
@router.get(
    "/tasks/{task_id}",
    response_model=schemas.TaskResponse,
    tags=["Tareas"],
    summary="Obtener una tarea por ID"
)
def read_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una tarea específica por su ID.

    Incluye el objeto de categoría anidado (si tiene categoría asignada).

    ### Ejemplo de respuesta:
    ```json
    {
        "id": 1,
        "title": "Estudiar FastAPI",
        "description": "Leer la documentación",
        "priority": 2,
        "completed": false,
        "category_id": 1,
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00",
        "category": {
            "id": 1,
            "name": "Trabajo",
            "description": "Tareas de trabajo"
        }
    }
    ```
    """
    db_task = crud.get_task(db, task_id)

    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea con id={task_id} no encontrada"
        )

    return db_task


# ------------------------------------------------------------
# PATCH /tasks/{task_id} - Actualizar una tarea
# ------------------------------------------------------------
@router.patch(
    "/tasks/{task_id}",
    response_model=schemas.TaskResponse,
    tags=["Tareas"],
    summary="Actualizar una tarea (parcialmente)"
)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza parcialmente una tarea.

    ### Casos de uso comunes:

    **Marcar como completada:**
    ```json
    { "completed": true }
    ```

    **Cambiar prioridad:**
    ```json
    { "priority": 3 }
    ```

    **Actualización completa:**
    ```json
    {
        "title": "Nuevo título",
        "description": "Nueva descripción",
        "priority": 2,
        "completed": false,
        "category_id": 2
    }
    ```

    **Quitar categoría:**
    ```json
    { "category_id": null }
    ```
    """
    # Si se está cambiando la categoría, verificar que exista
    if task_update.category_id is not None:
        category = crud.get_category(db, task_update.category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con id={task_update.category_id} no encontrada"
            )

    db_task = crud.update_task(db, task_id, task_update)

    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea con id={task_id} no encontrada"
        )

    return db_task


# ------------------------------------------------------------
# DELETE /tasks/{task_id} - Eliminar una tarea
# ------------------------------------------------------------
@router.delete(
    "/tasks/{task_id}",
    response_model=schemas.TaskResponse,
    tags=["Tareas"],
    summary="Eliminar una tarea"
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina una tarea por su ID.

    Devuelve la tarea eliminada para confirmar la operación.
    """
    db_task = crud.delete_task(db, task_id)

    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea con id={task_id} no encontrada"
        )

    return db_task


# ------------------------------------------------------------
# GET /categories/{category_id}/tasks - Tareas de una categoría
# ------------------------------------------------------------
@router.get(
    "/categories/{category_id}/tasks",
    response_model=List[schemas.TaskResponse],
    tags=["Categorías", "Tareas"],    # Aparece en ambas secciones en /docs
    summary="Obtener todas las tareas de una categoría"
)
def read_tasks_by_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Devuelve todas las tareas que pertenecen a una categoría específica.

    ### Ejemplo:
    ```
    GET /categories/1/tasks  -> todas las tareas de la categoría 1
    ```

    ---
    **RUTAS ANIDADAS (Nested Routes)**:

    Este endpoint es un ejemplo de "ruta anidada".
    La URL refleja la relación: una categoría TIENE tareas.
    Es una buena práctica REST: `/recurso-padre/{id}/recurso-hijo`
    """
    # Verificar que la categoría existe
    db_category = crud.get_category(db, category_id)
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con id={category_id} no encontrada"
        )

    tasks = crud.get_tasks_by_category(db, category_id)
    return tasks
