# 📋 Task Manager API — Proyecto Educativo de FastAPI

> **Proyecto académico** diseñado para aprender FastAPI desde cero,
> con todos los conceptos comentados y explicados en el código.

---
##Se dará inicio a auth

## 🗂️ Tabla de Contenidos

1. [¿Qué es este proyecto?](#-qué-es-este-proyecto)
2. [Estructura del proyecto](#-estructura-del-proyecto)
3. [Cómo funciona todo junto](#-cómo-funciona-todo-junto)
4. [Requisitos previos](#-requisitos-previos)
5. [Instalación y configuración](#-instalación-y-configuración)
6. [Cómo activar el servidor](#-cómo-activar-el-servidor)
7. [Endpoints disponibles](#-endpoints-disponibles)
8. [Probar la API](#-probar-la-api)
9. [Tecnologías y por qué se usan](#-tecnologías-y-por-qué-se-usan)
10. [Guía de aprendizaje profunda](#-guía-de-aprendizaje-profunda)

---

## 🎯 ¿Qué es este proyecto?

Es un **CRUD completo** de gestión de tareas (como un mini Todoist o Trello simplificado). Permite:

- Crear, leer, actualizar y eliminar **categorías** (Trabajo, Personal, Estudio, etc.)
- Crear, leer, actualizar y eliminar **tareas**, cada una con:
  - Título y descripción
  - Estado (completada / pendiente)
  - Prioridad (Baja / Media / Alta)
  - Categoría (opcional)
  - Timestamps automáticos (creación y última modificación)

### ¿Por qué un Task Manager?

Es el MVP (Minimum Viable Product) perfecto para aprender porque:
- Tiene **2 entidades relacionadas** (Categories y Tasks) → aprendes relaciones en BD
- Tiene **todos los verbos HTTP** (GET, POST, PATCH, DELETE)
- Es lo suficientemente simple para entender, y lo suficientemente completo para ser útil
- Es extensible: puedes agregar usuarios, autenticación, tags, etc.

---

## 📁 Estructura del proyecto

```
Crud-Fastapi/
│
├── main.py           ← Punto de entrada. Define TODOS los endpoints HTTP.
│                       Es el "director de orquesta" que conecta todo.
│
├── database.py       ← Configuración de la base de datos.
│                       Crea el engine, las sesiones y la clase Base.
│                       Conecta: FastAPI ↔ SQLAlchemy ↔ SQLite
│
├── models.py         ← Modelos ORM. Clases Python que representan tablas en la BD.
│                       Category y Task son clases que heredan de Base (database.py)
│
├── schemas.py        ← Schemas Pydantic. Definen la forma de los datos
│                       que entran y salen de la API (validación + serialización)
│
├── crud.py           ← Lógica de base de datos. Funciones para
│                       Create, Read, Update y Delete usando SQLAlchemy.
│
├── requirements.txt  ← Lista de dependencias Python del proyecto
│
├── README.md         ← Este archivo
└── GUIA_FASTAPI.md   ← Guía educativa profunda de cada concepto
```

---

## 🔗 Cómo funciona todo junto

```
PETICIÓN HTTP (cliente: Postman, navegador, frontend)
        │
        ▼
┌─────────────────┐
│   Uvicorn       │  ← Servidor ASGI que recibe y responde peticiones HTTP
│  (servidor)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    FastAPI      │  ← Framework que enruta la petición al endpoint correcto
│   (main.py)     │    y valida automáticamente los datos con Pydantic
└────────┬────────┘
         │ usa schemas de
         ▼
┌─────────────────┐
│    Pydantic     │  ← Valida los datos de entrada y serializa la respuesta
│  (schemas.py)   │    (convierte JSON ↔ objetos Python con tipos)
└────────┬────────┘
         │ llama funciones de
         ▼
┌─────────────────┐
│   CRUD Layer    │  ← Contiene toda la lógica de base de datos
│   (crud.py)     │    Funciones: get_tasks(), create_task(), etc.
└────────┬────────┘
         │ usa modelos de
         ▼
┌─────────────────┐
│   SQLAlchemy    │  ← ORM que convierte operaciones Python a SQL
│   (models.py)   │    Task (clase Python) ↔ tasks (tabla en SQLite)
└────────┬────────┘
         │ configurado en
         ▼
┌─────────────────┐
│   database.py   │  ← Engine, sesiones y clase Base
└────────┬────────┘
         │ escribe/lee en
         ▼
┌─────────────────┐
│    tasks.db     │  ← Archivo SQLite (la base de datos real)
│  (archivo .db)  │    Se crea automáticamente al iniciar la app
└─────────────────┘
```

### Flujo de una petición `POST /tasks`:

```
1. Cliente envía:  POST /tasks  con body { "title": "Estudiar", "priority": 2 }
2. Uvicorn recibe la petición y la pasa a FastAPI
3. FastAPI encuentra la función `create_task()` en main.py
4. Pydantic valida el body contra TaskCreate schema
   - ¿Tiene title? ✓
   - ¿priority está entre 1-3? ✓
5. FastAPI llama a create_task(task, db)
6. create_task() llama a crud.create_task(db, task)
7. crud crea models.Task(**task.model_dump())
8. SQLAlchemy ejecuta: INSERT INTO tasks (title, priority) VALUES (...)
9. SQLite guarda el registro y devuelve el ID generado
10. SQLAlchemy refresca el objeto con id, created_at, etc.
11. Pydantic serializa el objeto Task a JSON (usando TaskResponse)
12. FastAPI envía la respuesta 201 Created con el JSON al cliente
```

---

## ✅ Requisitos previos

### Software necesario:
- **Python 3.10 o superior** — [Descargar aquí](https://python.org/downloads)
  - Para verificar tu versión: `python --version` o `python3 --version`
- **pip** — Viene incluido con Python (gestor de paquetes)

### Conocimientos recomendados (no obligatorios para empezar):
- Python básico (variables, funciones, clases)
- Conceptos básicos de HTTP (qué es una API, qué es un endpoint)
- Noción de qué es una base de datos

> 📚 Si no tienes estos conocimientos, el archivo `GUIA_FASTAPI.md`
> explica todos los conceptos desde cero.

---

## 🚀 Instalación y configuración

### Paso 1: Clonar el repositorio (si no lo tienes)
```bash
git clone https://github.com/Sinisterra-dev/Crud-Fastapi.git
cd Crud-Fastapi
```

### Paso 2: Crear un entorno virtual

Un **entorno virtual** es un ambiente Python aislado para tu proyecto.
Evita conflictos de versiones entre proyectos diferentes.

```bash
# Crear el entorno virtual
python -m venv venv

# Activarlo en macOS/Linux:
source venv/bin/activate

# Activarlo en Windows (cmd):
venv\Scripts\activate.bat

# Activarlo en Windows (PowerShell):
venv\Scripts\Activate.ps1
```

Cuando está activo, verás `(venv)` al inicio de tu terminal.

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instala:
- `fastapi` — El framework web
- `uvicorn[standard]` — El servidor ASGI
- `sqlalchemy` — El ORM
- `pydantic` — Validación de datos (ya incluido con FastAPI)

---

## ▶️ Cómo activar el servidor

### Opción 1 (Recomendada para desarrollo): con `--reload`
```bash
uvicorn main:app --reload
```

- `main` → el archivo `main.py`
- `app` → la variable `app = FastAPI()` dentro de `main.py`
- `--reload` → reinicia el servidor automáticamente cuando editas un archivo

### Opción 2: sin recarga automática
```bash
uvicorn main:app
```

### Opción 3: ejecutando Python directamente
```bash
python main.py
```

### Salida esperada en la terminal:
```
INFO:     Will watch for changes in these directories: ['/ruta/del/proyecto']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Acceder a la API:
| URL | Descripción |
|-----|-------------|
| `http://localhost:8000` | Endpoint raíz (health check) |
| `http://localhost:8000/docs` | 📖 **Documentación interactiva (Swagger UI)** |
| `http://localhost:8000/redoc` | 📖 Documentación alternativa (ReDoc) |

> 💡 **Tip**: Empieza por `http://localhost:8000/docs`. Puedes probar todos
> los endpoints directamente desde el navegador sin necesidad de Postman.

---

## 🛣️ Endpoints disponibles

### Categorías (`/categories`)

| Método | URL | Descripción | Código éxito |
|--------|-----|-------------|--------------|
| `GET` | `/categories` | Listar todas las categorías | `200 OK` |
| `POST` | `/categories` | Crear una nueva categoría | `201 Created` |
| `GET` | `/categories/{id}` | Obtener una categoría por ID | `200 OK` |
| `PATCH` | `/categories/{id}` | Actualizar una categoría | `200 OK` |
| `DELETE` | `/categories/{id}` | Eliminar una categoría | `200 OK` |
| `GET` | `/categories/{id}/tasks` | Ver tareas de una categoría | `200 OK` |

### Tareas (`/tasks`)

| Método | URL | Descripción | Código éxito |
|--------|-----|-------------|--------------|
| `GET` | `/tasks` | Listar tareas (con filtros) | `200 OK` |
| `POST` | `/tasks` | Crear una nueva tarea | `201 Created` |
| `GET` | `/tasks/{id}` | Obtener una tarea por ID | `200 OK` |
| `PATCH` | `/tasks/{id}` | Actualizar una tarea | `200 OK` |
| `DELETE` | `/tasks/{id}` | Eliminar una tarea | `200 OK` |

### Filtros disponibles en `GET /tasks`:

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `skip` | int | Registros a saltar | `?skip=10` |
| `limit` | int | Máximo de registros | `?limit=5` |
| `completed` | bool | Filtrar por estado | `?completed=false` |
| `priority` | int (1-3) | Filtrar por prioridad | `?priority=3` |

---

## 🧪 Probar la API

### Opción A: Swagger UI (más visual)
1. Inicia el servidor: `uvicorn main:app --reload`
2. Abre `http://localhost:8000/docs`
3. Haz clic en cualquier endpoint y luego en "Try it out"

### Opción B: curl (terminal)

```bash
# Crear una categoría
curl -X POST "http://localhost:8000/categories" \
     -H "Content-Type: application/json" \
     -d '{"name": "Trabajo", "description": "Tareas laborales"}'

# Listar categorías
curl http://localhost:8000/categories

# Crear una tarea
curl -X POST "http://localhost:8000/tasks" \
     -H "Content-Type: application/json" \
     -d '{"title": "Estudiar FastAPI", "priority": 2, "category_id": 1}'

# Ver tareas pendientes de alta prioridad
curl "http://localhost:8000/tasks?completed=false&priority=3"

# Marcar tarea como completada
curl -X PATCH "http://localhost:8000/tasks/1" \
     -H "Content-Type: application/json" \
     -d '{"completed": true}'

# Eliminar una tarea
curl -X DELETE "http://localhost:8000/tasks/1"
```

### Opción C: Python con requests

```python
import requests

BASE = "http://localhost:8000"

# Crear categoría
cat = requests.post(f"{BASE}/categories", json={"name": "Estudio"}).json()
print(cat)  # {"id": 1, "name": "Estudio", ...}

# Crear tarea
task = requests.post(f"{BASE}/tasks", json={
    "title": "Leer documentación FastAPI",
    "priority": 3,
    "category_id": cat["id"]
}).json()
print(task)

# Listar tareas pendientes
pendientes = requests.get(f"{BASE}/tasks", params={"completed": False}).json()
print(pendientes)
```

---

## 🧱 Tecnologías y por qué se usan

### FastAPI
- **¿Qué es?** Framework web moderno para construir APIs con Python
- **¿Por qué?** Más rápido que Django REST Framework, más simple que Flask para APIs, documentación automática, validación integrada con Pydantic
- **Documentación**: https://fastapi.tiangolo.com

### Uvicorn
- **¿Qué es?** Servidor ASGI (Asynchronous Server Gateway Interface)
- **¿Por qué?** FastAPI es una aplicación ASGI (asíncrona), necesita un servidor compatible. Uvicorn es el más rápido y el recomendado por FastAPI
- **ASGI vs WSGI**: WSGI (Flask, Django clásico) es síncrono. ASGI permite manejar múltiples peticiones simultáneas sin bloquear el hilo

### SQLAlchemy
- **¿Qué es?** ORM (Object Relational Mapper) — la librería de BD más popular en Python
- **¿Por qué?** Nos permite trabajar con la BD usando objetos Python en lugar de SQL crudo. Más seguro (previene SQL injection), más mantenible, agnóstico de la BD (funciona con SQLite, PostgreSQL, MySQL, etc.)

### SQLite
- **¿Qué es?** Base de datos de archivo (no requiere servidor separado)
- **¿Por qué?** Para desarrollo es perfecta: no necesitas instalar nada, el archivo se crea automáticamente. En producción usarías PostgreSQL o MySQL

### Pydantic
- **¿Qué es?** Librería de validación de datos basada en type hints de Python
- **¿Por qué?** FastAPI lo usa internamente para validar requests y serializar responses. Con Pydantic defines la "forma" de tus datos y obtienes validación automática

---

## 📖 Guía de aprendizaje profunda

Para una explicación detallada de cada concepto, incluyendo qué debes
dominar para entender cada parte del código, consulta:

👉 **[GUIA_FASTAPI.md](GUIA_FASTAPI.md)**

La guía cubre:
- Fundamentos de HTTP y REST
- Por qué existe FastAPI y cómo funciona internamente
- Dependency Injection explicado a fondo
- SQLAlchemy: models, sessions, queries, relationships
- Pydantic: validation, serialization, schemas
- Cada archivo del proyecto con su explicación línea por línea
- Errores comunes y cómo resolverlos
- Próximos pasos para seguir aprendiendo
