from fastapi import APIRouter, HTTPException, Depends, Query, status, APIRouter

# Session: tipo de SQLAlchemy para type hints
from sqlalchemy.orm import Session

# List, Optional: tipos para type hints
from typing import List, Optional

# Importamos todo lo que creamos en los otros archivos
import models.task
import models.category
import schemas.category
from core.database import engine, get_db, Base   # Conexión a la BD y generador de sesiones
from services import task_service as crud





router = APIRouter(
prefix="/api/categories",
    tags=["Categories"]
)






# ------------------------------------------------------------
# GET /categories - Listar todas las categorías
# ------------------------------------------------------------
@router.get(
    "/categories",                          # URL del endpoint
    response_model=List[schemas.CategoryResponse],  # Schema de respuesta
    tags=["Categorías"],                    # Agrupa en /docs
    summary="Listar todas las categorías"  # Descripción corta en /docs
)
def read_categories(
    skip: int = Query(default=0, ge=0, description="Registros a saltar (paginación)"),
    limit: int = Query(default=100, ge=1, le=200, description="Máximo de registros a devolver"),
    db: Session = Depends(get_db)  # FastAPI inyecta la sesión automáticamente
):
    """
    Devuelve la lista de todas las categorías.

    ### Parámetros de query (opcionales):
    - **skip**: cuántos registros saltar (para paginación). Default: 0
    - **limit**: cuántos registros devolver. Default: 100

    ### Ejemplo de uso:
    ```
    GET /categories          -> todas las categorías
    GET /categories?skip=10  -> desde la categoría 11
    GET /categories?limit=5  -> solo 5 categorías
    ```

    ---
    **¿QUÉ ES @router.get?**

    Es un "decorador de ruta" (route decorator).
    Le dice a FastAPI: "cuando llegue una petición GET a /categories,
    ejecuta esta función".

    **¿QUÉ ES Query()?**

    Es una forma de declarar parámetros de query string con validación.
    Los parámetros de query van en la URL: /categories?skip=0&limit=10
    """
    # Llamamos a la función CRUD que hace la consulta a la BD
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories


# ------------------------------------------------------------
# POST /categories - Crear una nueva categoría
# ------------------------------------------------------------
@router.post(
    "/categories",
    response_model=schemas.CategoryResponse,   # Lo que devolvemos
    status_code=status.HTTP_201_CREATED,       # Código HTTP 201 = Created
    tags=["Categorías"],
    summary="Crear una nueva categoría"
)
def create_category(
    category: schemas.CategoryCreate,  # Cuerpo del request (automáticamente validado)
    db: Session = Depends(get_db)
):
    """
    Crea una nueva categoría.

    ### Cuerpo del request (JSON):
    ```json
    {
        "name": "Trabajo",
        "description": "Tareas relacionadas con el trabajo"
    }
    ```

    ### Respuesta exitosa (201 Created):
    ```json
    {
        "id": 1,
        "name": "Trabajo",
        "description": "Tareas relacionadas con el trabajo"
    }
    ```

    ---
    **VALIDACIONES:**
    - El nombre es obligatorio
    - El nombre debe ser único (no puede haber dos categorías con el mismo nombre)
    - El nombre tiene mínimo 1 y máximo 50 caracteres

    **¿CÓMO FUNCIONA LA VALIDACIÓN AUTOMÁTICA?**

    Cuando declares `category: schemas.CategoryCreate` en la firma,
    FastAPI automáticamente:
    1. Lee el body del request (JSON)
    2. Lo valida con Pydantic (tipos, longitudes, etc.)
    3. Si hay error, devuelve 422 Unprocessable Entity automáticamente
    4. Si es válido, llama a esta función con el objeto validado
    """
    # Verificamos que no exista ya una categoría con ese nombre
    # Las categorías tienen nombre único (unique=True en el modelo)
    existing = crud.get_category_by_name(db, category.name)
    if existing:
        # HTTPException: lanza un error HTTP con el código y mensaje indicados
        # status_code=400: Bad Request (el cliente envió datos incorrectos)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una categoría con el nombre '{category.name}'"
        )

    # Si no existe, la creamos
    return crud.create_category(db, category)


# ------------------------------------------------------------
# GET /categories/{category_id} - Obtener una categoría por ID
# ------------------------------------------------------------
@router.get(
    "/categories/{category_id}",              # {category_id} es un "path parameter"
    response_model=schemas.CategoryResponse,
    tags=["Categorías"],
    summary="Obtener una categoría por ID"
)
def read_category(
    category_id: int,  # FastAPI extrae el valor de la URL y lo convierte a int
    db: Session = Depends(get_db)
):
    """
    Obtiene una categoría específica por su ID.

    ### Path Parameter:
    - **category_id**: el ID numérico de la categoría

    ### Ejemplo:
    ```
    GET /categories/1  -> devuelve la categoría con id=1
    ```

    ---
    **¿QUÉ SON LOS PATH PARAMETERS?**

    Son variables dentro de la URL, indicadas con `{}`.
    `{category_id}` captura el número que va después de /categories/.
    FastAPI automáticamente convierte el string de la URL al tipo
    declarado (int en este caso).

    Si el usuario envía `/categories/abc`, FastAPI devuelve
    422 Unprocessable Entity porque "abc" no es un int.
    """
    db_category = crud.get_category(db, category_id)

    # Si la categoría no existe, devolvemos 404 Not Found
    # 404 = "No encontrado" - el recurso solicitado no existe
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con id={category_id} no encontrada"
        )

    return db_category


# ------------------------------------------------------------
# PATCH /categories/{category_id} - Actualizar una categoría
# ------------------------------------------------------------
@router.patch(
    "/categories/{category_id}",
    response_model=schemas.CategoryResponse,
    tags=["Categorías"],
    summary="Actualizar una categoría (parcialmente)"
)
def update_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,   # Los campos a actualizar
    db: Session = Depends(get_db)
):
    """
    Actualiza parcialmente una categoría.

    Puedes enviar solo los campos que quieres modificar.

    ### Ejemplos:
    Solo cambiar el nombre:
    ```json
    { "name": "Trabajo Remoto" }
    ```

    Solo cambiar la descripción:
    ```json
    { "description": "Nueva descripción" }
    ```

    Cambiar ambos:
    ```json
    {
        "name": "Trabajo Remoto",
        "description": "Trabajo desde casa"
    }
    ```

    ---
    **PATCH vs PUT:**
    - **PATCH**: actualización parcial (solo envías lo que cambia)
    - **PUT**: reemplaza el recurso completo (debes enviar todos los campos)

    En APIs modernas, PATCH es más común porque es más flexible.
    """
    # Verificamos si el nuevo nombre ya existe (si se está cambiando)
    if category_update.name:
        existing = crud.get_category_by_name(db, category_update.name)
        # Si existe y no es la misma categoría que estamos editando
        if existing and existing.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una categoría con el nombre '{category_update.name}'"
            )

    db_category = crud.update_category(db, category_id, category_update)

    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con id={category_id} no encontrada"
        )

    return db_category


# ------------------------------------------------------------
# DELETE /categories/{category_id} - Eliminar una categoría
# ------------------------------------------------------------
@router.delete(
    "/categories/{category_id}",
    response_model=schemas.CategoryResponse,
    tags=["Categorías"],
    summary="Eliminar una categoría"
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina una categoría por su ID.

    Las tareas que pertenecían a esta categoría quedarán
    sin categoría (category_id = NULL), NO serán eliminadas.

    ### Respuesta:
    Devuelve la categoría eliminada para confirmar qué fue borrado.

    ---
    **¿POR QUÉ DEVOLVER LA CATEGORÍA ELIMINADA?**

    Es una buena práctica devolver el recurso eliminado.
    Así el cliente puede:
    - Confirmar qué fue eliminado
    - Actualizar su estado local (ej: remover de una lista en UI)
    - Mostrar un mensaje de confirmación al usuario
    """
    db_category = crud.delete_category(db, category_id)

    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con id={category_id} no encontrada"
        )

    return db_category
