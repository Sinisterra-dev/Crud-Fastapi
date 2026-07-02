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




# ============================================================
# ====== ENDPOINTS DE TAREAS ======
# ============================================================
# Patrón similar al de categorías, pero con más funcionalidades:
# - Filtros por estado y prioridad
# - Respuesta con metadatos (total de tareas)
# - Relación con categorías
# ============================================================




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
