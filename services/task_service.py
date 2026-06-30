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

# Importamos los modelos ORM (las clases que representan tablas)
import models

# Importamos los schemas Pydantic (las clases que validan datos)
from schemas import category, task


# ============================================================
# CRUD DE CATEGORIES (Categorías)
# ============================================================

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    """
    LEE todas las categorías de la base de datos.

    PARÁMETROS:
    - db: Session
        La sesión de base de datos (inyectada por FastAPI).
        Con ella hacemos todas las operaciones de BD.

    - skip: int = 0
        Número de registros a saltar (para paginación).
        Ej: skip=10 salta los primeros 10 registros.
        Equivale a SQL: OFFSET skip

    - limit: int = 100
        Máximo de registros a devolver.
        Equivale a SQL: LIMIT limit

    RETORNA: Lista de objetos Category (modelos SQLAlchemy)

    SQL EQUIVALENTE:
        SELECT * FROM categories LIMIT 100 OFFSET 0;

    PAGINACIÓN:
        Página 1: skip=0,  limit=10  -> registros 1-10
        Página 2: skip=10, limit=10  -> registros 11-20
        Página 3: skip=20, limit=10  -> registros 21-30
    """
    return db.query(models.Category).offset(skip).limit(limit).all()
    # db.query(models.Category) -> SELECT * FROM categories
    # .offset(skip)             -> OFFSET skip
    # .limit(limit)             -> LIMIT limit
    # .all()                    -> ejecuta la query y devuelve lista


def get_category(db: Session, category_id: int):
    """
    LEE una categoría específica por su ID.

    PARÁMETROS:
    - db: sesión de BD
    - category_id: el ID de la categoría que queremos

    RETORNA: objeto Category o None si no existe

    SQL EQUIVALENTE:
        SELECT * FROM categories WHERE id = category_id LIMIT 1;

    NOTA sobre .first():
        .first() devuelve el primer resultado o None.
        .one() devuelve el único resultado o lanza excepción.
        .all() devuelve todos como lista.
        Usamos .first() para evitar excepciones si no existe.
    """
    return (
        db.query(models.Category)
        .filter(models.Category.id == category_id)  # WHERE id = category_id
        .first()  # LIMIT 1 + manejo de None
    )


def get_category_by_name(db: Session, name: str):
    """
    LEE una categoría por su nombre.
    Útil para verificar si ya existe antes de crear una nueva
    (los nombres son únicos según el modelo).

    SQL EQUIVALENTE:
        SELECT * FROM categories WHERE name = name LIMIT 1;
    """
    return (
        db.query(models.Category)
        .filter(models.Category.name == name)
        .first()
    )


def create_category(db: Session, category: schemas.CategoryCreate):
    """
    CREA una nueva categoría en la base de datos.

    PARÁMETROS:
    - db: sesión de BD
    - category: objeto CategoryCreate (schema Pydantic validado)
        Ya pasó por la validación de Pydantic antes de llegar aquí.

    RETORNA: el objeto Category creado (con el ID asignado por la BD)

    PROCESO:
    1. Crear instancia del modelo SQLAlchemy con los datos
    2. Agregar al "tracking" de la sesión (db.add)
    3. Confirmar los cambios en la BD (db.commit)
    4. Refrescar el objeto para obtener datos generados por la BD (db.refresh)

    SQL EQUIVALENTE:
        INSERT INTO categories (name, description) VALUES (name, description);

    ¿QUÉ ES model_dump()?
        Es un método de Pydantic que convierte el schema a diccionario.
        Luego **dict desempaqueta el diccionario como keyword arguments.

        Ejemplo:
        category.model_dump() -> {"name": "Trabajo", "description": "..."}
        models.Category(**{"name": "Trabajo", "description": "..."})
        equivale a:
        models.Category(name="Trabajo", description="...")
    """
    # Creamos la instancia del modelo SQLAlchemy con los datos del schema
    db_category = models.Category(**category.model_dump())

    # db.add(): registra el objeto en la sesión (no lo guarda aún en la BD)
    # La sesión "trackea" (rastrea) este objeto para guardarlo
    db.add(db_category)

    # db.commit(): ejecuta el INSERT en la BD y guarda los cambios
    # Si hay un error, la transacción se revierte automáticamente
    db.commit()

    # db.refresh(): actualiza el objeto con los datos de la BD
    # Necesario para obtener el "id" generado automáticamente
    # y otros campos como created_at que los pone la BD
    db.refresh(db_category)

    return db_category


def update_category(db: Session, category_id: int, category_update: schemas.CategoryUpdate):
    """
    ACTUALIZA una categoría existente.

    PARÁMETROS:
    - db: sesión de BD
    - category_id: ID de la categoría a actualizar
    - category_update: schema con los campos a actualizar (todos opcionales)

    RETORNA: el objeto Category actualizado o None si no existe

    ACTUALIZACIÓN PARCIAL (PATCH):
        model_dump(exclude_unset=True) es clave aquí.
        Devuelve SOLO los campos que el usuario envió,
        no todos los campos del schema.

        Ejemplo:
        Usuario envía: { "name": "Nuevo nombre" }
        category_update.model_dump(exclude_unset=True) -> {"name": "Nuevo nombre"}
        NO incluye "description": None (no lo tocamos)

        Si usáramos model_dump() sin exclude_unset,
        sobreescribiríamos "description" con None aunque el usuario no lo envió.
    """
    # Primero buscamos la categoría
    db_category = get_category(db, category_id)

    # Si no existe, retornamos None (el endpoint manejará el 404)
    if db_category is None:
        return None

    # Obtenemos solo los campos que el usuario envió (no los opcionales vacíos)
    update_data = category_update.model_dump(exclude_unset=True)

    # Actualizamos cada campo del objeto SQLAlchemy
    # setattr(objeto, "campo", valor) es equivalente a objeto.campo = valor
    # Lo hacemos dinámicamente para no hardcodear cada campo
    for field, value in update_data.items():
        setattr(db_category, field, value)

    # Guardamos los cambios
    db.commit()
    db.refresh(db_category)

    return db_category


def delete_category(db: Session, category_id: int):
    """
    ELIMINA una categoría de la base de datos.

    PARÁMETROS:
    - db: sesión de BD
    - category_id: ID de la categoría a eliminar

    RETORNA: el objeto Category eliminado o None si no existía

    SQL EQUIVALENTE:
        DELETE FROM categories WHERE id = category_id;

    NOTA SOBRE ondelete="SET NULL":
        Definimos en el modelo Task que si se elimina una categoría,
        category_id en las tareas relacionadas queda en NULL.
        Esto evita errores de integridad referencial.
    """
    db_category = get_category(db, category_id)

    if db_category is None:
        return None

    # db.delete(): marca el objeto para eliminación
    db.delete(db_category)

    # db.commit(): ejecuta el DELETE en la BD
    db.commit()

    # Retornamos el objeto eliminado (ya no está en la BD, pero el objeto existe en memoria)
    # Útil para que el endpoint pueda confirmar qué fue eliminado
    return db_category


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
    query = db.query(models.Task)

    # Aplicamos filtros dinámicamente (solo si el parámetro no es None)
    # Esto es el patrón "filtros opcionales"
    if completed is not None:
        # SQL: WHERE completed = completed
        query = query.filter(models.Task.completed == completed)

    if priority is not None:
        # SQL: WHERE priority = priority
        query = query.filter(models.Task.priority == priority)

    # Contamos el total ANTES de aplicar paginación
    # SQL: SELECT COUNT(*) FROM tasks WHERE ...
    total = query.count()

    # Aplicamos paginación y ejecutamos la query
    # SQL: SELECT * FROM tasks WHERE ... LIMIT limit OFFSET skip
    # joinedload: hace un LEFT JOIN para cargar .category en la misma query
    tasks = query.options(joinedload(models.Task.category)).offset(skip).limit(limit).all()

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
        db.query(models.Task)
        .options(joinedload(models.Task.category))  # LEFT JOIN con categories
        .filter(models.Task.id == task_id)
        .first()
    )


def create_task(db: Session, task: schemas.TaskCreate):
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
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    # Recargamos el objeto con joinedload para obtener la relación category
    # No podemos usar db.refresh() directamente con options(), así que
    # hacemos una nueva query por el id recién creado
    return get_task(db, db_task.id)


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
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
        db.query(models.Task)
        .options(joinedload(models.Task.category))  # LEFT JOIN con categories
        .filter(models.Task.category_id == category_id)
        .all()
    )
