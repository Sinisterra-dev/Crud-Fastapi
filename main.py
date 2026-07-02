# ============================================================
# MAIN.PY - Aplicacion principal de FastAPI
# ============================================================
# Este es el punto de entrada del proyecto.
# Aqui se crea la instancia de FastAPI, se preparan las tablas
# de la base de datos y se conectan los routers disponibles.
#
# Flujo basico de una peticion HTTP:
#   Cliente (navegador, Postman, Swagger)
#       -> Uvicorn (servidor ASGI)
#       -> FastAPI (rutas, validacion y documentacion)
#       -> Funcion del endpoint
#       -> Servicio o logica correspondiente
#       -> Base de datos si el endpoint la necesita
#
# Conceptos importantes:
#   - HTTP: GET, POST, PUT, PATCH, DELETE
#   - REST: rutas que representan recursos
#   - Decoradores: @app.get, @router.post, etc.
#   - Type hints: ayudan a FastAPI y a Pydantic a validar datos
#   - Dependency Injection: Depends(...) para recursos como la BD
# ============================================================

from fastapi import FastAPI

import models.category
import models.task
from core.database import Base, engine
from practicas import router as practicas_router


# ============================================================
# CREACION DE TABLAS EN LA BASE DE DATOS
# ============================================================
# create_all() crea las tablas definidas en los modelos SQLAlchemy
# cuando todavia no existen. No borra ni sobreescribe registros.
#
# En un proyecto real de produccion se suele usar Alembic para
# migraciones, porque permite versionar cambios en las tablas.
# Para aprendizaje y desarrollo local, create_all() es suficiente.
# ============================================================
Base.metadata.create_all(bind=engine)


# ============================================================
# INSTANCIA DE FASTAPI
# ============================================================
# FastAPI genera documentacion automatica:
#   - /docs  -> Swagger UI para probar endpoints desde el navegador
#   - /redoc -> documentacion alternativa mas formal
# ============================================================
app = FastAPI(
    title="Task Manager API",
    description="""
    ## API de Gestion de Tareas - Proyecto Educativo FastAPI

    Esta API practica fundamentos de FastAPI, CRUD, rutas, validacion
    y logica de negocio.

    ### Secciones principales:
    * **General** - Estado de la API y enlaces de documentacion
    * **products** - 50 misiones practicas para entrenar logica y FastAPI
    """,
    version="1.0.0",
)


# ============================================================
# ROUTERS
# ============================================================
# Un router agrupa endpoints relacionados.
# practicas_router expone las 50 misiones del archivo practicas.py.
# Todas esas rutas empiezan con /products.
# ============================================================
app.include_router(practicas_router)


# ------------------------------------------------------------
# GET / - Endpoint raiz (health check / bienvenida)
# ------------------------------------------------------------
@app.get("/", tags=["General"], summary="Bienvenida y estado de la API")
def root():
    """
    Endpoint raiz de la API.

    Sirve como health check basico: si responde, la aplicacion
    esta corriendo y puede recibir peticiones.
    """
    return {
        "message": "Bienvenido a Task Manager API",
        "descripcion": "API educativa de CRUD con FastAPI",
        "documentacion_interactiva": "/docs",
        "documentacion_alternativa": "/redoc",
        "practicas": "/products",
    }


# ============================================================
# EJECUCION DIRECTA
# ============================================================
# Este bloque solo corre si ejecutas:
#   python main.py
#
# La forma mas comun durante desarrollo es:
#   uvicorn main:app --reload
# ============================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
