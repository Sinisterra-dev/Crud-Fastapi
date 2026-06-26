# ============================================================
# MAIN.PY - Aplicación principal de FastAPI
print("ESTE ES EL MAIN QUE SE ESTÁ EJECUTANDO")
# ============================================================
# Este es el punto de entrada de nuestra aplicación.
# Aquí es donde:
#   1. Creamos la instancia de FastAPI
#   2. Configuramos la aplicación (CORS, metadatos, etc.)
#   3. Definimos TODOS los endpoints (rutas de la API)
#   4. Conectamos todo: BD, schemas, lógica CRUD
#
# FLUJO DE UNA PETICIÓN HTTP:
#   Cliente (ej: navegador, Postman)
#       --> HTTP Request (GET /tasks, POST /tasks, etc.)
#       --> Uvicorn (servidor ASGI)
#       --> FastAPI (router, validación)
#       --> Función del endpoint
#       --> task_service.py (lógica de BD)
#       --> SQLAlchemy (ORM)
#       --> SQLite (base de datos)
#   Y el camino de vuelta es el inverso.
#
# CONCEPTOS QUE DEBES DOMINAR:
#   - HTTP (métodos: GET, POST, PUT, PATCH, DELETE; códigos de estado)
#   - REST API y sus principios
#   - Decoradores en Python (@app.get, @app.post, etc.)
#   - Parámetros en Python (posicionales, keyword, *args, **kwargs)
#   - Type hints en Python
#   - Async/Await en Python (programación asíncrona)
# ============================================================

# FastAPI: la clase principal del framework
# HTTPException: para lanzar errores HTTP (404, 400, etc.)
# Depends: para inyección de dependencias (como la sesión de BD)
# Query: para documentar y validar parámetros de query string
# status: constantes de códigos HTTP (200, 201, 404, etc.)
from fastapi import FastAPI, HTTPException, Depends, Query, status

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


# ============================================================
# CREACIÓN DE TABLAS EN LA BASE DE DATOS
# ============================================================
# create_all() crea todas las tablas definidas en models.txt
# si no existen todavía.
#
# Base.metadata contiene toda la información de los modelos
# (tablas, columnas, tipos de datos, relaciones).
#
# checkfirst=True (comportamiento por defecto con create_all):
#   Solo crea las tablas que NO existen todavía.
#   No sobreescribe datos existentes.
#
# NOTA: En producción usarías "Alembic" para migraciones
# de base de datos. Alembic puede crear, modificar y versionar
# el esquema de la BD. create_all() es solo para desarrollo.
# ============================================================
Base.metadata.create_all(bind=engine)


# ============================================================
# INSTANCIA DE FASTAPI
# ============================================================
# FastAPI() crea la aplicación. Los parámetros son metadatos
# que se muestran en la documentación automática (/docs).
#
# DOCUMENTACIÓN AUTOMÁTICA:
#   FastAPI genera documentación interactiva automáticamente:
#   - /docs  : Swagger UI (interfaz gráfica para probar la API)
#   - /redoc : ReDoc (documentación más formal)
#
#   ¡Puedes probar todos los endpoints directamente desde el navegador!
# ============================================================
app = FastAPI(
    # Título de la API (aparece en /docs)
    title="Task Manager API",

    # Descripción de la API (aparece en /docs, soporta Markdown)
    description="""
    ## API de Gestión de Tareas - Proyecto Educativo FastAPI

    Esta API es un CRUD completo para manejar tareas organizadas en categorías.

    ### Entidades:
    * **Categorías** - Grupos para organizar las tareas (Trabajo, Personal, etc.)
    * **Tareas** - Las actividades a realizar, con título, descripción, prioridad y estado

    ### Operaciones disponibles:
    * **CRUD de Categorías** - Crear, leer, actualizar y eliminar categorías
    * **CRUD de Tareas** - Crear, leer, actualizar y eliminar tareas
    * **Filtros** - Filtrar tareas por estado (completada/pendiente) y prioridad
    """,

    # Versión de la API (aparece en /docs y en /openapi.json)
    version="1.0.0",
)


# ============================================================
# ====== ENDPOINTS DE CATEGORÍAS ======
# ============================================================
# Los "endpoints" son las URLs que la API expone.
# Cada endpoint tiene:
#   - URL (path): la ruta, como "/categories" o "/categories/{id}"
#   - Método HTTP: GET, POST, PUT, PATCH, DELETE
#   - Función handler: el código que se ejecuta cuando llega la petición
#
# MÉTODOS HTTP Y SU SIGNIFICADO:
#   GET    -> Obtener/leer datos (no modifica nada)
#   POST   -> Crear nuevos datos
#   PUT    -> Reemplazar completamente un recurso
#   PATCH  -> Actualizar parcialmente un recurso
#   DELETE -> Eliminar un recurso
#
# PREFIJO /categories:
#   Todas las rutas de categorías empiezan con /categories.
#   Es una convención REST: el path refleja el "recurso".
# ============================================================


# ------------------------------------------------------------
# GET /categories - Listar todas las categorías
# ------------------------------------------------------------
@app.get(
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
    **¿QUÉ ES @app.get?**

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
@app.post(
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
@app.get(
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
@app.patch(
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
@app.delete(
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


# ============================================================
# ====== ENDPOINTS DE TAREAS ======
# ============================================================
# Patrón similar al de categorías, pero con más funcionalidades:
# - Filtros por estado y prioridad
# - Respuesta con metadatos (total de tareas)
# - Relación con categorías
# ============================================================


# ------------------------------------------------------------
# GET /tasks - Listar tareas (con filtros opcionales)
# ------------------------------------------------------------
@app.get(
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
@app.post(
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
@app.get(
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
@app.patch(
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
@app.delete(
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
@app.get(
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


# ------------------------------------------------------------
# GET / - Endpoint raíz (health check / bienvenida)
# ------------------------------------------------------------
@app.get(
    "/",
    tags=["General"],
    summary="Bienvenida y estado de la API"
)
def root():
    """
    Endpoint raíz. Sirve como "health check" básico.

    Un "health check" es un endpoint simple que confirma
    que la API está corriendo y respondiendo peticiones.
    Útil para monitoreo y para verificar que el servidor está activo.

    ### Respuesta:
    ```json
    {
        "message": "Bienvenido a Task Manager API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
    ```
    """
    return {
        "message": "¡Bienvenido a Task Manager API! 🚀",
        "descripcion": "API educativa de CRUD con FastAPI",
        "documentacion_interactiva": "/docs",
        "documentacion_alternativa": "/redoc",
        "endpoints": {
            "categorias": "/categories",
            "tareas": "/tasks"
        }
    }


# ============================================================
# PUNTO DE ENTRADA PARA EJECUTAR DIRECTAMENTE
# ============================================================
# Este bloque se ejecuta SOLO si corres el archivo directamente:
#   python main.py
#
# Si importas main.py desde otro módulo (como los tests),
# este bloque NO se ejecuta.
#
# ¿POR QUÉ if __name__ == "__main__"?
#   __name__ es una variable especial de Python.
#   Cuando ejecutas "python main.py", __name__ vale "__main__".
#   Cuando importas el módulo, __name__ vale "main".
#   Esto previene que el servidor se inicie al importar el módulo.
#
# FORMA RECOMENDADA DE EJECUTAR (en lugar de python main.py):
#   uvicorn main:app --reload
#
# uvicorn: el servidor ASGI
# main: el módulo (main.py)
# app: la instancia de FastAPI
# --reload: reinicia automáticamente cuando detecta cambios en el código
# ============================================================
if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0": escucha en todas las interfaces de red (accesible desde LAN)
    # port=8000: puerto donde escucha el servidor
    # reload=True: modo desarrollo con recarga automática
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
