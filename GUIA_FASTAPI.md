# 📘 GUÍA COMPLETA DE FASTAPI — Con el Proyecto Task Manager

> **Soy tu senior developer.** Esta guía explica cada concepto del proyecto,
> qué debes dominar para entenderlo, y cómo todo se conecta.
> No omitimos nada. Si hay un término que no conoces, está explicado aquí.

---

## 📑 Índice de Contenidos

1. [¿Qué es FastAPI y por qué existe?](#1-qué-es-fastapi-y-por-qué-existe)
2. [¿Qué es una API REST?](#2-qué-es-una-api-rest)
3. [¿Qué es HTTP?](#3-qué-es-http)
4. [Estructura del proyecto y sus responsabilidades](#4-estructura-del-proyecto-y-sus-responsabilidades)
5. [database.py — La conexión con la BD](#5-databasepy--la-conexión-con-la-bd)
6. [models.py — Los modelos ORM](#6-modelspy--los-modelos-orm)
7. [schemas.py — Validación con Pydantic](#7-schemaspy--validación-con-pydantic)
8. [crud.py — La capa de datos](#8-crudpy--la-capa-de-datos)
9. [main.py — Los endpoints de la API](#9-mainpy--los-endpoints-de-la-api)
10. [Dependency Injection en FastAPI](#10-dependency-injection-en-fastapi)
11. [Códigos de estado HTTP](#11-códigos-de-estado-http)
12. [Errores comunes y cómo resolverlos](#12-errores-comunes-y-cómo-resolverlos)
13. [Conceptos avanzados para seguir aprendiendo](#13-conceptos-avanzados-para-seguir-aprendiendo)

---

## 1. ¿Qué es FastAPI y por qué existe?

### Prerequisitos para entender esta sección:
- ¿Qué es Python?
- ¿Qué es una librería / framework?
- Conceptos básicos de programación web

### La historia rápida

Antes de FastAPI (2019), para hacer APIs en Python tenías dos opciones principales:

- **Flask**: microframework muy flexible pero sin validación automática. Tú manejabas todo.
- **Django REST Framework (DRF)**: muy completo pero pesado y verboso.

**FastAPI** llegó para combinar lo mejor de ambos mundos:
- La simplicidad de Flask
- La validación automática de datos (gracias a Pydantic)
- Documentación automática (Swagger UI)
- Soporte nativo para async/await
- Type hints de Python como fuente de verdad

### ¿Qué significa "framework"?

Un framework es un conjunto de herramientas, convenciones y código reutilizable
que te da una estructura para construir algo. FastAPI te da:
- Un sistema de routing (¿qué función se ejecuta para cada URL?)
- Validación automática de datos
- Documentación automática
- Manejo de errores
- Sistema de dependencias

### Las 3 grandes ventajas de FastAPI

1. **Velocidad de desarrollo**: escribes menos código para hacer lo mismo
2. **Velocidad de ejecución**: es uno de los frameworks Python más rápidos (comparable a Node.js y Go)
3. **Documentación automática**: crea Swagger UI y ReDoc sin ningún código extra

---

## 2. ¿Qué es una API REST?

### Prerequisitos para entender esta sección:
- ¿Qué es HTTP?
- ¿Qué es un servidor web?
- ¿Qué es JSON?

### API = Application Programming Interface

Una API es una forma de comunicación entre programas. Define:
- **Qué puede pedir** un programa (endpoints, métodos)
- **Cómo pedirlo** (formato de los requests)
- **Qué recibe** de vuelta (formato de los responses)

Piénsala como el menú de un restaurante:
- El menú = la documentación de la API (`/docs`)
- Pedir algo = hacer un request HTTP
- El plato que traen = el response de la API

### REST = Representational State Transfer

REST es un **estilo de arquitectura** para diseñar APIs. Sus principios principales:

1. **Recursos y URLs**: cada "cosa" de tu sistema es un recurso con su propia URL
   - `/tasks` = el recurso "tareas"
   - `/categories` = el recurso "categorías"
   - `/tasks/5` = la tarea específica con id=5

2. **Verbos HTTP**: el tipo de operación se define con el método HTTP
   - `GET /tasks` = "dame las tareas" (leer)
   - `POST /tasks` = "crea una tarea" (crear)
   - `PATCH /tasks/5` = "modifica la tarea 5" (actualizar parcialmente)
   - `DELETE /tasks/5` = "elimina la tarea 5" (eliminar)

3. **Sin estado (Stateless)**: cada request es independiente. El servidor no recuerda
   peticiones anteriores. Toda la info necesaria va en cada request.

4. **Respuestas en formato estándar**: normalmente JSON

---

## 3. ¿Qué es HTTP?

### Prerequisitos para entender esta sección:
- Conceptos básicos de redes (cliente-servidor)
- ¿Qué es una URL?

### HTTP = HyperText Transfer Protocol

Es el protocolo de comunicación de la web. Funciona con un modelo cliente-servidor:

```
Cliente (navegador, app)           Servidor (tu FastAPI)
         │                                    │
         │──── HTTP Request ──────────────────>│
         │                                    │ procesa
         │<─── HTTP Response ─────────────────│
         │                                    │
```

### Anatomía de un HTTP Request

```
POST /tasks HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Accept: application/json

{
    "title": "Estudiar FastAPI",
    "priority": 2
}
```

Partes:
- **Línea de inicio**: `POST /tasks HTTP/1.1`
  - Método: POST
  - Path: /tasks
  - Versión HTTP: HTTP/1.1
- **Headers**: metadatos (Content-Type, Authorization, etc.)
- **Body**: los datos que envías (solo en POST, PUT, PATCH)

### Anatomía de un HTTP Response

```
HTTP/1.1 201 Created
Content-Type: application/json

{
    "id": 1,
    "title": "Estudiar FastAPI",
    "priority": 2,
    "completed": false
}
```

Partes:
- **Status line**: `HTTP/1.1 201 Created`
  - Código de estado: 201
  - Texto descriptivo: Created
- **Headers**: metadatos de la respuesta
- **Body**: los datos de respuesta (JSON en nuestra API)

### Los Métodos HTTP y su significado semántico

| Método | ¿Qué hace? | ¿Tiene body? | ¿Es seguro? | ¿Es idempotente? |
|--------|-----------|--------------|-------------|------------------|
| GET | Lee datos | No | Sí | Sí |
| POST | Crea datos | Sí | No | No |
| PUT | Reemplaza datos | Sí | No | Sí |
| PATCH | Actualiza parcialmente | Sí | No | Sí |
| DELETE | Elimina datos | No | No | Sí |

**¿Qué es "seguro"?** Una operación segura no modifica el estado del servidor.
**¿Qué es "idempotente"?** Ejecutarlo múltiples veces produce el mismo resultado.
- `DELETE /tasks/5` ejecutado 2 veces → el resultado es el mismo (la tarea ya no existe)
- `POST /tasks` ejecutado 2 veces → crea 2 tareas diferentes (NO es idempotente)

---

## 4. Estructura del proyecto y sus responsabilidades

### Prerequisitos:
- Principios básicos de diseño de software (separación de responsabilidades)
- ¿Qué es la arquitectura en capas?

### El patrón de arquitectura de este proyecto

Este proyecto sigue un patrón de **arquitectura en capas** (Layered Architecture):

```
┌─────────────────────────────────────┐
│         CAPA DE PRESENTACIÓN        │  main.py
│    (HTTP, routing, validación)      │  Recibe requests, devuelve responses
├─────────────────────────────────────┤
│         CAPA DE VALIDACIÓN          │  schemas.py
│    (Pydantic, tipos de datos)       │  Define la forma de los datos
├─────────────────────────────────────┤
│        CAPA DE NEGOCIO/DATOS        │  crud.py
│    (lógica de acceso a la BD)       │  Contiene las queries SQLAlchemy
├─────────────────────────────────────┤
│         CAPA DE DOMINIO             │  models.py
│    (entidades del negocio)          │  Define las tablas y relaciones
├─────────────────────────────────────┤
│         CAPA DE DATOS               │  database.py + tasks.db
│    (conexión a la BD)               │  Engine, sessions, SQLite
└─────────────────────────────────────┘
```

### ¿Por qué no poner todo en un archivo?

**Separación de Responsabilidades (SRP - Single Responsibility Principle)**:
Cada módulo/archivo/función tiene UNA razón para cambiar.

Beneficios:
- **Mantenibilidad**: si cambias la BD (de SQLite a PostgreSQL), solo modificas `database.py` y `models.py`
- **Testabilidad**: puedes testear `crud.py` de forma aislada sin levantar el servidor HTTP
- **Legibilidad**: sabes dónde buscar cada tipo de código
- **Reusabilidad**: las funciones de `crud.py` se pueden usar desde múltiples endpoints

---

## 5. database.py — La conexión con la BD

### Prerequisitos para entender este archivo:
- ¿Qué es una base de datos relacional?
- ¿Qué es SQL?
- ¿Qué es un ORM?
- Generadores en Python (`yield`)
- Context managers en Python (`with`)

### ¿Qué es una base de datos relacional?

Una base de datos relacional organiza los datos en **tablas** (como hojas de Excel):
- Cada tabla tiene **columnas** (campos) y **filas** (registros)
- Las tablas se relacionan entre sí mediante **llaves** (IDs)

```
Tabla: categories
┌────┬──────────┬──────────────────────┐
│ id │   name   │     description      │
├────┼──────────┼──────────────────────┤
│  1 │ Trabajo  │ Tareas laborales     │
│  2 │ Personal │ Tareas personales    │
└────┴──────────┴──────────────────────┘

Tabla: tasks
┌────┬──────────────────┬───────────┬─────────────┬──────────────┐
│ id │      title       │ completed │   priority  │ category_id  │
├────┼──────────────────┼───────────┼─────────────┼──────────────┤
│  1 │ Estudiar FastAPI │   false   │      2      │      1       │
│  2 │ Comprar pan      │   false   │      1      │      2       │
└────┴──────────────────┴───────────┴─────────────┴──────────────┘
                                                          │
                                                          └─ Referencia a categories.id
```

### ¿Qué es un ORM?

**ORM = Object Relational Mapper**

Sin ORM, necesitarías escribir SQL así:
```python
cursor.execute("""
    INSERT INTO tasks (title, completed, priority, category_id)
    VALUES (?, ?, ?, ?)
""", ("Estudiar FastAPI", False, 2, 1))
connection.commit()
```

Con SQLAlchemy ORM, escribes Python puro:
```python
task = Task(title="Estudiar FastAPI", completed=False, priority=2, category_id=1)
db.add(task)
db.commit()
```

El ORM traduce las operaciones Python a SQL automáticamente. Ventajas:
- Más legible y pythonico
- Protección automática contra SQL injection
- Agnóstico de la BD (cambias SQLite por PostgreSQL sin tocar las queries)
- Autocompletado en tu IDE

### El objeto `engine` en detalle

```python
engine = create_engine(
    "sqlite:///./tasks.db",
    connect_args={"check_same_thread": False}
)
```

El `engine` es el corazón de SQLAlchemy. Gestiona:
- **El pool de conexiones**: no crea una conexión nueva por cada operación,
  reutiliza conexiones existentes (performance)
- **El dialecto**: traduce las operaciones Python al SQL específico de cada BD
  (SQLite usa `?` para parámetros, PostgreSQL usa `%s`, etc.)

### Sesiones vs Conexiones

Una **conexión** es el canal de comunicación con la BD (como una llamada telefónica).
Una **sesión** es una unidad de trabajo que puede involucrar múltiples conexiones (como una conversación).

```
Session (unidad de trabajo)
   │
   ├─ BEGIN TRANSACTION
   ├─ SELECT * FROM tasks WHERE ...
   ├─ INSERT INTO tasks (...)
   ├─ UPDATE tasks SET ...
   └─ COMMIT (o ROLLBACK si hay error)
```

### La función `get_db()` como generador

```python
def get_db():
    db = SessionLocal()
    try:
        yield db       # <── aquí la ejecución "pausa" y entrega db al endpoint
    finally:
        db.close()     # <── esto se ejecuta después de que el endpoint termina
```

La palabra `yield` convierte la función en un **generador**.
Con `yield`, la función puede "pausarse" en medio y luego continuar.

Timeline de ejecución:
```
get_db() llamada por FastAPI
    │
    ▼
db = SessionLocal()  ← se crea la sesión
    │
    ▼
yield db             ← se "entrega" la sesión al endpoint y se pausa
    │                   [el endpoint hace todo su trabajo aquí]
    ▼
finally: db.close()  ← la sesión se cierra siempre, pase lo que pase
```

---

## 6. models.py — Los modelos ORM

### Prerequisitos para entender este archivo:
- Clases y Programación Orientada a Objetos (POO) en Python
- Herencia en Python
- ¿Qué es una llave primaria (Primary Key)?
- ¿Qué es una llave foránea (Foreign Key)?

### La clase `Base` y por qué heredamos de ella

```python
from core.database import Base


class Category(Base):  # ← hereda de Base
    __tablename__ = "categories"
    ...
```

`Base` (creada por `declarative_base()`) es el "registro central" de SQLAlchemy.
Cuando defines `class Category(Base)`, SQLAlchemy:
1. Registra que existe una tabla llamada "categories"
2. Mapea los atributos de la clase a columnas de la tabla
3. Permite que `Base.metadata.create_all()` cree todas las tablas

### Tipos de columnas SQLAlchemy

| SQLAlchemy | Python | SQL |
|-----------|--------|-----|
| `Integer` | `int` | `INTEGER` |
| `String(n)` | `str` | `VARCHAR(n)` |
| `Text` | `str` | `TEXT` |
| `Boolean` | `bool` | `BOOLEAN` |
| `DateTime` | `datetime` | `DATETIME` |
| `Float` | `float` | `FLOAT` |

### Primary Key vs Foreign Key

**Primary Key (PK)**:
- Identifica de forma única cada fila de una tabla
- No puede ser NULL
- No puede repetirse
- Generalmente es `id` (autoincremental)

```python
id = Column(Integer, primary_key=True, index=True)
```

**Foreign Key (FK)**:
- Referencia a la PK de otra tabla
- Crea una relación entre tablas
- Garantiza integridad referencial (no puedes referenciar un id que no existe)

```python
category_id = Column(
    Integer,
    ForeignKey("categories.id", ondelete="SET NULL"),
    nullable=True
)
```

### Las relaciones ORM (`relationship`)

```python
# En Category:
tasks = relationship("Task", back_populates="category")

# En Task:
category = relationship("Category", back_populates="tasks")
```

`relationship()` crea un atributo virtual (no es una columna) que SQLAlchemy
llena automáticamente con los objetos relacionados.

```python
# Acceder a las tareas de una categoría:
mi_categoria = db.query(Category).filter(Category.id == 1).first()
print(mi_categoria.tasks)  # [<Task id=1>, <Task id=2>, ...]

# Acceder a la categoría de una tarea:
mi_tarea = db.query(Task).filter(Task.id == 1).first()
print(mi_tarea.category)   # <Category id=1 name='Trabajo'>
print(mi_tarea.category.name)  # 'Trabajo'
```

### ¿Qué es `ondelete="SET NULL"`?

Define qué pasa con las tareas cuando se elimina su categoría:

```python
ForeignKey("categories.id", ondelete="SET NULL")
```

Opciones disponibles:
- `CASCADE`: elimina también las tareas (borra en cascada)
- `SET NULL`: pone `category_id = NULL` en las tareas (lo que usamos)
- `RESTRICT`: lanza un error si intentas eliminar una categoría con tareas
- `NO ACTION`: comportamiento por defecto (similar a RESTRICT)

Elegimos `SET NULL` porque las tareas no deben desaparecer si alguien borra la categoría.

---

## 7. schemas.py — Validación con Pydantic

### Prerequisitos para entender este archivo:
- Type hints en Python (`int`, `str`, `Optional`, `List`)
- Clases y herencia en Python
- ¿Qué es la validación de datos?
- ¿Qué es la serialización / deserialización?

### ¿Qué es la validación de datos?

La validación verifica que los datos cumplen ciertas reglas antes de procesarlos.

Sin validación:
```python
# ¿Qué pasa si el usuario envía esto?
{ "title": "", "priority": 999 }
# Título vacío, prioridad inválida → se guardaría basura en la BD
```

Con Pydantic:
```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    priority: int = Field(default=1, ge=1, le=3)
```

Si el usuario envía `priority: 999`, Pydantic automáticamente devuelve:
```json
{
    "detail": [
        {
            "type": "less_than_equal",
            "loc": ["body", "priority"],
            "msg": "Input should be less than or equal to 3",
            "input": 999
        }
    ]
}
```

Y el código del endpoint NUNCA se ejecuta con datos inválidos. 🛡️

### ¿Por qué tener schemas separados de los models?

Es el principio de **separación de responsabilidades aplicado a los datos**:

```
models.py (SQLAlchemy)     schemas.py (Pydantic)
─────────────────────     ─────────────────────
Representa la BD           Representa los datos HTTP
Sabe de tablas, SQL        Sabe de JSON, validación
Define relaciones ORM      Define shapes de API
Category, Task             CategoryCreate, TaskResponse
```

Ejemplo concreto: ¿Qué pasaría si usamos el modelo SQLAlchemy directamente?
- Expondríamos campos internos (timestamps del servidor, relaciones completas)
- No tendríamos validación automática
- No podríamos diferenciar entre "lo que se recibe" y "lo que se devuelve"

### El patrón Base → Create → Update → Response

```python
class TaskBase(BaseModel):      # Campos comunes
    title: str
    description: Optional[str]
    priority: int

class TaskCreate(TaskBase):     # Para crear (hereda Base, agrega nada)
    pass

class TaskUpdate(BaseModel):    # Para actualizar (todos opcionales)
    title: Optional[str] = None
    priority: Optional[int] = None
    completed: Optional[bool] = None

class TaskResponse(TaskBase):   # Para respuestas (hereda Base, agrega id, etc.)
    id: int
    completed: bool
    created_at: Optional[datetime]
    category: Optional[CategoryResponse]
```

Beneficio: **el cliente no puede enviar el `id`** (lo asigna la BD), pero **sí lo recibe** en la respuesta.

### `model_config = {"from_attributes": True}`

```python
class TaskResponse(TaskBase):
    id: int
    ...
    model_config = {"from_attributes": True}
```

Sin esto, Pydantic esperaría un diccionario `{"id": 1, "title": "..."}`.
Con esto, Pydantic puede leer de un objeto SQLAlchemy `task.id`, `task.title`, etc.

Esto es el puente entre el mundo ORM (objetos) y Pydantic (schemas).

### `Field()` para validaciones avanzadas

```python
from pydantic import Field

title: str = Field(
    ...,            # ... = obligatorio (no tiene valor por defecto)
    min_length=1,   # validación: longitud mínima
    max_length=100, # validación: longitud máxima
    description="Título de la tarea",  # aparece en /docs
    examples=["Estudiar FastAPI"]      # aparece en /docs como ejemplo
)

priority: int = Field(
    default=1,  # valor por defecto (hace el campo opcional)
    ge=1,       # ge = greater or equal (>=)
    le=3        # le = less or equal (<=)
)
```

---

## 8. crud.py — La capa de datos

### Prerequisitos para entender este archivo:
- Funciones en Python
- Type hints en Python
- SQL básico (SELECT, INSERT, UPDATE, DELETE, WHERE)
- ORM básico (SQLAlchemy sessions y queries)

### Las operaciones CRUD y sus equivalentes SQL

| Operación CRUD | Función Python | SQL equivalente |
|---------------|----------------|-----------------|
| Create | `crud.create_task()` | `INSERT INTO tasks ...` |
| Read (lista) | `crud.get_tasks()` | `SELECT * FROM tasks` |
| Read (uno) | `crud.get_task()` | `SELECT * FROM tasks WHERE id=?` |
| Update | `crud.update_task()` | `UPDATE tasks SET ... WHERE id=?` |
| Delete | `crud.delete_task()` | `DELETE FROM tasks WHERE id=?` |

### El ciclo de vida de un objeto en SQLAlchemy

```
Transient         Pending           Persistent        Detached
   │                │                   │                │
   │   db.add()     │    db.commit()     │    db.close()  │
   └────────────────┘────────────────────┘────────────────┘

Transient:   solo existe en Python, SQLAlchemy no lo conoce
Pending:     db.add() lo registró, pero NO está en la BD todavía
Persistent:  db.commit() lo guardó en la BD, SQLAlchemy lo rastrea
Detached:    la sesión se cerró, el objeto ya no está conectado a la BD
```

### La importancia de `db.refresh()`

```python
db_task = models.Task(title="Nueva tarea")
db.add(db_task)
db.commit()
# db_task.id es None aquí porque Python no sabe el ID que asignó la BD

db.refresh(db_task)
# Ahora db_task.id tiene el valor correcto que la BD asignó
# También db_task.created_at tiene la fecha real
```

Sin `db.refresh()`, ciertos campos generados por la BD quedarían vacíos.

### Actualización parcial con `exclude_unset=True`

Este es uno de los conceptos más importantes de este proyecto:

```python
# Usuario envía: { "completed": true }
task_update = TaskUpdate(completed=True)

# Sin exclude_unset:
task_update.model_dump()
# → {"title": None, "description": None, "completed": True, "priority": None, "category_id": None}
# ¡Sobreescribiría title con None aunque el usuario no lo envió!

# Con exclude_unset:
task_update.model_dump(exclude_unset=True)
# → {"completed": True}
# Solo los campos que el usuario explícitamente envió
```

Este es el mecanismo que hace que PATCH funcione correctamente (actualización parcial).

### Filtros dinámicos en SQLAlchemy

```python
query = db.query(models.Task)          # base query: SELECT * FROM tasks

if completed is not None:
    query = query.filter(models.Task.completed == completed)  # WHERE completed = ?

if priority is not None:
    query = query.filter(models.Task.priority == priority)    # AND priority = ?

total = query.count()                  # SELECT COUNT(*) FROM tasks WHERE ...
tasks = query.offset(skip).limit(limit).all()  # + LIMIT + OFFSET
```

Este patrón de construir queries dinámicamente es muy poderoso.
En vez de tener N funciones para N combinaciones de filtros, tienes una sola función flexible.

---

## 9. main.py — Los endpoints de la API

### Prerequisitos para entender este archivo:
- HTTP y sus métodos (GET, POST, PATCH, DELETE)
- Decoradores en Python (`@algo`)
- Type hints en Python
- ¿Qué es una función y sus parámetros?

### ¿Qué es un decorador en Python?

Un decorador es una función que "envuelve" a otra función y modifica su comportamiento.

```python
@app.get("/tasks")
def read_tasks():
    return []
```

Equivale a:
```python
def read_tasks():
    return []

read_tasks = app.get("/tasks")(read_tasks)
```

`@app.get("/tasks")` le dice a FastAPI:
- Registra la URL `/tasks` para el método GET
- Cuando llegue una petición GET a /tasks, ejecuta `read_tasks()`

### Los decoradores de ruta en FastAPI

```python
@app.get("/tasks")       # GET /tasks
@app.post("/tasks")      # POST /tasks
@app.patch("/tasks/{id}")  # PATCH /tasks/{id}
@app.delete("/tasks/{id}") # DELETE /tasks/{id}
@app.put("/tasks/{id}")    # PUT /tasks/{id}
```

### Path Parameters vs Query Parameters

**Path Parameters**: variables dentro de la URL (entre `{}`)
```python
@app.get("/tasks/{task_id}")
def read_task(task_id: int):  # FastAPI extrae el int de la URL
    ...
# URL: GET /tasks/5  →  task_id = 5
```

**Query Parameters**: variables en la query string (después de `?`)
```python
@app.get("/tasks")
def read_tasks(
    completed: bool = None,
    priority: int = None
):
    ...
# URL: GET /tasks?completed=false&priority=2
#      completed = False, priority = 2
```

**Request Body**: datos enviados en el cuerpo del request (POST, PATCH, PUT)
```python
@app.post("/tasks")
def create_task(task: schemas.TaskCreate):  # FastAPI lee el JSON del body
    ...
# Body: { "title": "Nueva tarea", "priority": 2 }
```

FastAPI sabe qué es qué por el tipo:
- Si el tipo es un modelo Pydantic (`BaseModel`) → es el body
- Si el tipo es un tipo simple (`int`, `str`, `bool`) y está en la URL → es path parameter
- Si el tipo es un tipo simple y NO está en la URL → es query parameter

### `response_model`: el contrato de la respuesta

```python
@app.get("/tasks", response_model=schemas.TaskListResponse)
def read_tasks(...):
    ...
```

`response_model` le dice a FastAPI:
1. **Filtrar** la respuesta: solo incluye los campos del schema (no expone campos internos)
2. **Validar** la respuesta: verifica que el formato es correcto (en modo debug)
3. **Documentar** automáticamente: en /docs muestra el esquema de la respuesta

Si tu función devuelve un objeto con más campos de los declarados en `response_model`,
FastAPI automáticamente los filtra. Tu BD no filtra nada, FastAPI lo hace por ti.

### `status_code`: el código HTTP de la respuesta exitosa

```python
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(...):
    ...
```

Por defecto, FastAPI devuelve 200 OK. Pero para creación, el estándar es 201 Created.
Usar los códigos correctos es importante para:
- Clientes que interpretan los códigos (ej: frontend, APIs de terceros)
- Herramientas de monitoreo
- Documentación correcta

### `HTTPException`: devolver errores HTTP

```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Tarea no encontrada"
)
```

FastAPI convierte esto en:
```json
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "detail": "Tarea no encontrada"
}
```

El cliente sabe que hubo un error por el código 404, y el campo `detail` explica qué pasó.

### `tags`: organización en la documentación

```python
@app.get("/tasks", tags=["Tareas"])
@app.get("/categories", tags=["Categorías"])
```

En `/docs`, los endpoints se agrupan por tags. Hace la documentación más legible.

---

## 10. Dependency Injection en FastAPI

### Prerequisitos:
- Funciones en Python
- ¿Qué es una dependencia (en software)?
- Generadores en Python

### ¿Qué es Dependency Injection?

**Dependency Injection (DI)** es un patrón donde un objeto/función recibe sus
dependencias desde afuera en lugar de crearlas internamente.

Sin DI:
```python
def read_tasks():
    db = SessionLocal()  # crea la sesión internamente
    try:
        return db.query(Task).all()
    finally:
        db.close()
```

Con DI (lo que usamos):
```python
def read_tasks(db: Session = Depends(get_db)):  # recibe la sesión desde afuera
    return db.query(Task).all()
```

### `Depends()` en FastAPI

```python
from fastapi import Depends
from core.database import get_db


@app.get("/tasks")
def read_tasks(db: Session = Depends(get_db)):
    ...
```

Cuando FastAPI ve `Depends(get_db)`:
1. Ejecuta `get_db()` antes de llamar a `read_tasks()`
2. Pasa el valor retornado (la sesión) como argumento `db`
3. Después de que `read_tasks()` termina, continúa la ejecución de `get_db()`
   (el código después del `yield`, que cierra la sesión)

### Beneficios de DI

1. **Testabilidad**: puedes reemplazar `get_db` con una versión de prueba en tests
2. **Reutilización**: `get_db` se reutiliza en todos los endpoints sin repetir código
3. **Gestión automática**: la sesión se crea y cierra automáticamente
4. **Composición**: puedes encadenar dependencias (una dependencia que usa otra dependencia)

### Ejemplo de cómo testear con DI (bonus)

```python
# En tests, sobreescribimos la dependencia:
from fastapi.testclient import TestClient
from main import app
from core.database import get_db


def override_get_db():
    # BD de prueba en memoria, no toca la BD real
    test_db = TestingSessionLocal()
    try:
        yield test_db
    finally:
        test_db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)
```

---

## 11. Códigos de estado HTTP

### Los más importantes para una API REST

| Código | Nombre | Cuándo usarlo |
|--------|--------|---------------|
| `200` | OK | Request exitoso (GET, PATCH, DELETE) |
| `201` | Created | Recurso creado exitosamente (POST) |
| `204` | No Content | Éxito pero sin cuerpo de respuesta |
| `400` | Bad Request | El cliente envió datos incorrectos |
| `401` | Unauthorized | No está autenticado |
| `403` | Forbidden | Está autenticado pero no tiene permiso |
| `404` | Not Found | El recurso no existe |
| `409` | Conflict | Conflicto (ej: nombre duplicado) |
| `422` | Unprocessable Entity | Error de validación (Pydantic) |
| `500` | Internal Server Error | Error inesperado del servidor |

### ¿Por qué los códigos importan?

El frontend / cliente puede tomar decisiones basadas en el código:
- `404` → "Muestra un mensaje de 'no encontrado'"
- `401` → "Redirige al login"
- `400` → "Muestra los errores de validación al usuario"
- `500` → "Muestra 'algo salió mal, intenta más tarde'"

---

## 12. Errores comunes y cómo resolverlos

### Error: `ModuleNotFoundError: No module named 'fastapi'`
**Causa**: No instalaste las dependencias.
**Solución**:
```bash
pip install -r requirements.txt
```
Asegúrate de tener el entorno virtual activado.

### Error: `422 Unprocessable Entity`
**Causa**: Los datos que enviaste no cumplen la validación de Pydantic.
**Solución**: Lee el mensaje de error en el body de la respuesta. Te dice exactamente qué campo falló y por qué.
```json
{
    "detail": [
        {
            "type": "missing",
            "loc": ["body", "title"],
            "msg": "Field required"
        }
    ]
}
```

### Error: `sqlalchemy.exc.OperationalError: table tasks already exists`
**Causa**: Inconsistencia entre el modelo y la BD existente.
**Solución**: Para desarrollo, elimina el archivo `tasks.db` y reinicia el servidor.
```bash
rm tasks.db
uvicorn main:app --reload
```

### Error: `DetachedInstanceError`
**Causa**: Intentas acceder a una relación después de cerrar la sesión.
**Solución**: Accede a las relaciones antes de cerrar la sesión, o usa `lazy="joined"` en el relationship.

### Error: Puerto 8000 ya está en uso
**Causa**: Otra instancia del servidor ya está corriendo.
**Solución**:
```bash
uvicorn main:app --reload --port 8001
```
O termina el proceso que usa el puerto 8000.

---

## 13. Conceptos avanzados para seguir aprendiendo

Una vez que domines este proyecto, estos son los próximos pasos naturales:

### 🔐 Autenticación y Autorización
- **JWT (JSON Web Tokens)**: tokens de autenticación sin estado
- **OAuth2**: el protocolo que usan "Iniciar sesión con Google"
- FastAPI tiene soporte nativo con `fastapi.security`

### 🗄️ Migraciones con Alembic
- `create_all()` es solo para desarrollo. En producción usas **Alembic**
- Alembic versiona los cambios en el esquema de la BD
- Permite "migrar" la BD sin perder datos

### ⚡ Async/Await
- FastAPI soporta funciones async nativamente
- Útil para operaciones I/O (llamadas a APIs externas, BD)
- Permite manejar más peticiones concurrentes

### 📦 Routers (APIRouter)
- Para proyectos grandes, separas los endpoints en múltiples archivos
- `APIRouter` es como un "mini FastAPI" para un subconjunto de rutas
- El `app` principal incluye los routers

### 🧪 Testing con pytest
- `TestClient` de FastAPI para tests de integración
- `pytest` como framework de testing
- `dependency_overrides` para mockear la BD en tests

### 🐘 PostgreSQL en producción
- Cambiar `sqlite:///./tasks.db` por `postgresql://user:pass@host/db`
- Las queries SQLAlchemy funcionan sin cambios
- Usar variables de entorno para las credenciales (`.env` + `python-dotenv`)

### 📄 Variables de entorno
- Nunca hardcodear URLs de BD o secrets en el código
- Usar `pydantic-settings` para cargar configuración desde `.env`

### 🐳 Docker
- Containerizar la app para deployment
- `Dockerfile` + `docker-compose.yml`

---

> **Mensaje final del senior:**
>
> Este proyecto tiene todo lo que necesitas para entender FastAPI a nivel profesional.
> El código está comentado para que puedas leerlo como si fuera documentación.
> Te recomiendo:
>
> 1. Ejecutar el proyecto y probarlo en /docs
> 2. Leer cada archivo de arriba a abajo, entendiendo cada comentario
> 3. Hacer cambios pequeños: agrega un campo a Task, agrega un endpoint nuevo
> 4. Romper cosas a propósito para ver los errores
> 5. Agregar autenticación como siguiente reto
>
> El mejor aprendizaje viene de la experimentación. ¡Mucho éxito! 🚀
