# ============================================================
# CRUD.PY - Operaciones CRUD con SQLAlchemy
# Ahora llamado task_service
# ============================================================
# CRUD = Create, Read, Update, Delete
# (Crear, Leer, Actualizar, Eliminar)
#
# Este archivo contiene TODA la lógica de acceso a la base
# de datos. Es la capa de "repositorio" o "DAL" (Data Access Layer).
#
# PRINCIPIO DE RESPONSABILIDAD ÚNICA (SRP):
#   Cada función tiene UNA responsabilidad específica.
#   Los endpoints en main.py se encargan de HTTP.
#   Este archivo se encarga de la BD.
#   Mantenerlos separados hace el código más mantenible y testeable.
#
# CONCEPTOS QUE DEBES DOMINAR:
#   - Funciones en Python
#   - Parámetros con type hints
#   - SQLAlchemy Session (sesiones de BD)
#   - Queries de SQLAlchemy (query, filter, first, all)
#   - ¿Qué es CRUD en el contexto de APIs?
#   - HTTP Methods: GET, POST, PUT, PATCH, DELETE
# ============================================================

# Session: el tipo de las sesiones de SQLAlchemy
# Lo usamos en las type hints de los parámetros
# joinedload: carga EAGERLY una relación (JOIN en la consulta SQL)
# Necesario para que la relación esté disponible DESPUÉS de cerrar la sesión
from sqlalchemy.orm import Session, joinedload

from models.task import Task

from schemas.task import TaskCreate, TaskUpdate



# ============================================================
# CRUD DE TASKS (Tareas)
# ============================================================

def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    completed: bool | None = None,
    priority: int | None = None
):
    """
    LEE todas las tareas con filtros opcionales.

    PARÁMETROS:
    - db: sesión de BD
    - skip, limit: paginación
    - completed: filtrar por estado (True=completadas, False=pendientes, None=todas)
    - priority: filtrar por prioridad (1, 2, 3 o None para todas)

    RETORNA: tupla (total, lista de Task)
        - total: conteo total (sin paginación) para el frontend
        - tasks: lista paginada de tareas

    ¿POR QUÉ RETORNAR EL TOTAL?
        Cuando paginamos, el cliente necesita saber cuántos
        registros existen en total para mostrar la paginación.
        Si solo devuelves 10 tareas, ¿cómo sabe que hay 150 en total?
    """
    # Empezamos la query base
    query = db.query(Task)

    # Aplicamos filtros dinámicamente (solo si el parámetro no es None)
    # Esto es el patrón "filtros opcionales"
    if completed is not None:
        # SQL: WHERE completed = completed
        query = query.filter(Task.completed == completed)

    if priority is not None:
        # SQL: WHERE priority = priority
        query = query.filter(Task.priority == priority)

    # Contamos el total ANTES de aplicar paginación
    # SQL: SELECT COUNT(*) FROM tasks WHERE ...
    total = query.count()

    # Aplicamos paginación y ejecutamos la query
    # SQL: SELECT * FROM tasks WHERE ... LIMIT limit OFFSET skip
    # joinedload: hace un LEFT JOIN para cargar .category en la misma query
    tasks = query.options(joinedload(Task.category)).offset(skip).limit(limit).all()

    return total, tasks


def get_task(db: Session, task_id: int):
    """
    LEE una tarea específica por su ID.

    Usa joinedload para cargar EAGERLY la relación category.

    ¿Qué es EAGER LOADING?
        Por defecto, SQLAlchemy usa "lazy loading" para las relaciones:
        la relación se carga solo cuando la accedes por primera vez.
        Esto requiere que la sesión siga abierta.

        Con joinedload (eager loading), la relación se carga en la misma
        consulta SQL usando un JOIN. La relación ya está en memoria y no
        necesita la sesión para accederse después.

        SQL EQUIVALENTE con joinedload:
            SELECT tasks.*, categories.*
            FROM tasks
            LEFT OUTER JOIN categories ON tasks.category_id = categories.id
            WHERE tasks.id = task_id

    RETORNA: objeto Task (con .category ya cargado) o None si no existe
    """
    return (
        db.query(Task)
        .options(joinedload(Task.category))  # LEFT JOIN con categories
        .filter(Task.id == task_id)
        .first()
    )


def create_task(db: Session, task: TaskCreate):
    """
    CREA una nueva tarea en la base de datos.

    PARÁMETROS:
    - db: sesión de BD
    - task: schema TaskCreate validado por Pydantic

    RETORNA: objeto Task creado con su ID, timestamps y category cargada

    SQL EQUIVALENTE:
        INSERT INTO tasks (title, description, priority, category_id)
        VALUES (title, description, priority, category_id);
    """
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    # Recargamos el objeto con joinedload para obtener la relación category
    # No podemos usar db.refresh() directamente con options(), así que
    # hacemos una nueva query por el id recién creado
    return get_task(db, db_task.id)


def update_task(db: Session, task_id: int, task_update: TaskUpdate):
    """
    ACTUALIZA una tarea existente (actualización parcial).

    PARÁMETROS:
    - db: sesión de BD
    - task_id: ID de la tarea a actualizar
    - task_update: schema con los campos a modificar (todos opcionales)

    RETORNA: Task actualizada o None si no existe

    CASOS DE USO:
    - Marcar como completada: { "completed": true }
    - Cambiar prioridad: { "priority": 3 }
    - Cambiar título: { "title": "Nuevo título" }
    - Actualización completa: { "title": "...", "description": "...", ... }
    """
    db_task = get_task(db, task_id)

    if db_task is None:
        return None

    # exclude_unset=True: solo campos que el usuario envió explícitamente
    update_data = task_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    # Recargamos con joinedload para tener la relación category disponible
    return get_task(db, db_task.id)


def delete_task(db: Session, task_id: int):
    """
    ELIMINA una tarea de la base de datos.

    RETORNA: Task eliminada o None si no existía

    SQL EQUIVALENTE:
        DELETE FROM tasks WHERE id = task_id;

    NOTA SOBRE EAGER LOADING EN DELETE:
        Usamos get_task() que ya tiene joinedload para cargar category.
        Después de db.delete() + db.commit(), el objeto queda "detached"
        (desconectado de la sesión). Si la relación no estuviera ya cargada
        en memoria, SQLAlchemy lanzaría DetachedInstanceError al intentar
        acceder a .category durante la serialización de la respuesta.
    """
    # get_task ya usa joinedload, así que .category estará cargado en memoria
    db_task = get_task(db, task_id)

    if db_task is None:
        return None

    db.delete(db_task)
    db.commit()

    # Retornamos el objeto eliminado (ya no está en la BD, pero el objeto
    # sigue en memoria con todos sus atributos, incluida .category)
    return db_task


def get_tasks_by_category(db: Session, category_id: int):
    """
    LEE todas las tareas de una categoría específica.

    PARÁMETROS:
    - db: sesión de BD
    - category_id: ID de la categoría

    RETORNA: lista de Tasks de esa categoría

    SQL EQUIVALENTE:
        SELECT * FROM tasks WHERE category_id = category_id;
    """
    return (
        db.query(Task)
        .options(joinedload(Task.category))  # LEFT JOIN con categories
        .filter(Task.category_id == category_id)
        .all()
    )
