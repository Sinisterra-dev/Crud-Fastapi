# ============================================================
# DATABASE.PY - Configuración de la base de datos
# ============================================================
# Este archivo es el "puente" entre FastAPI y la base de datos.
# Aquí se define:
#   1. Con qué base de datos nos conectamos (SQLite en este caso)
#   2. Cómo creamos "sesiones" para hablar con la BD
#   3. Una clase base que heredarán todos nuestros modelos
#
# CONCEPTOS QUE DEBES DOMINAR PARA ENTENDER ESTE ARCHIVO:
#   - ¿Qué es una base de datos relacional?
#   - ¿Qué es SQL?
#   - ¿Qué es un ORM (Object Relational Mapper)?
#   - Importaciones en Python (import / from ... import)
#   - Funciones generadoras en Python (yield)
#   - Context managers (with statement)
# ============================================================

# SQLAlchemy nos provee las herramientas para trabajar con BD
from sqlalchemy import create_engine        # Crea la "conexión" a la BD
from sqlalchemy.ext.declarative import declarative_base  # Clase base para modelos
from sqlalchemy.orm import sessionmaker     # Fábrica de sesiones de BD
from dotenv import load_dotenv
import os
from .config import DATABASE_URL


# ------------------------------------------------------------
# 1. URL DE CONEXIÓN A LA BASE DE DATOS
# ------------------------------------------------------------
# SQLAlchemy usa una "connection string" (cadena de conexión)
# para saber a qué base de datos conectarse y cómo.
#
# Formato general:
#   dialecto+driver://usuario:contraseña@host:puerto/nombre_bd
#
# En nuestro caso usamos SQLite (una BD de archivo, sin servidor):
#   sqlite:///./tasks.db
#   - "sqlite:///" indica que es SQLite local
#   - "./tasks.db" es la ruta al archivo de la base de datos
#     (se creará automáticamente en la carpeta del proyecto)
#
# Para producción usarías algo como:
#   postgresql://user:password@localhost:5432/mydb
# ============================================================
DATABASE_URL = "mysql+pymysql///./tasks.db"


# ------------------------------------------------------------
# 2. ENGINE (Motor de base de datos)
# ------------------------------------------------------------
# El "engine" es el objeto principal de SQLAlchemy.
# Es quien realmente se conecta a la base de datos.
# Piénsalo como el "conductor" que maneja la conexión.
#
# create_engine(url, **kwargs):
#   - url: la cadena de conexión que definimos arriba
#   - connect_args: argumentos específicos del driver
#
# ¿Por qué connect_args={"check_same_thread": False}?
#   SQLite por defecto solo permite que UN hilo (thread) use
#   la conexión. FastAPI usa múltiples hilos para manejar
#   peticiones concurrentes, así que necesitamos desactivar
#   esa restricción. Esto es SOLO necesario con SQLite.
# ============================================================
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necesario SOLO para SQLite
)


# ------------------------------------------------------------
# 3. SESSIONLOCAL (Fábrica de sesiones)
# ------------------------------------------------------------
# Una "sesión" es una unidad de trabajo con la base de datos.
# Cada vez que necesitas hacer una operación (leer, crear,
# actualizar, eliminar), necesitas una sesión activa.
#
# sessionmaker() crea una "fábrica" (clase) que produce sesiones.
# Es como un molde para hacer sesiones.
#
# Parámetros:
#   - autocommit=False: los cambios NO se guardan automáticamente.
#     Debes llamar session.commit() explícitamente.
#     Esto te da control total sobre las transacciones.
#
#   - autoflush=False: SQLAlchemy NO enviará cambios pendientes
#     a la BD automáticamente antes de una consulta.
#     Nos da más control sobre cuándo se envían los datos.
#
#   - bind=engine: le dice a las sesiones que usen nuestro engine.
#
# TRANSACCIÓN: un grupo de operaciones que se ejecutan juntas.
# Si alguna falla, todas se revierten (ROLLBACK). Si todas
# tienen éxito, se confirman (COMMIT). Esto garantiza
# consistencia en los datos.
# ============================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ------------------------------------------------------------
# 4. BASE (Clase base para los modelos ORM)
# ------------------------------------------------------------
# declarative_base() crea una clase especial.
# Todos nuestros modelos (tablas) HEREDARÁN de esta clase.
#
# ¿Por qué heredar de Base?
#   SQLAlchemy usa esta clase para "registrar" todos los modelos
#   y saber qué tablas existen en la base de datos.
#   Sin esta herencia, SQLAlchemy no conocería tus modelos.
#
# HERENCIA EN PYTHON:
#   class MiModelo(Base):  <- MiModelo hereda de Base
#       ...
# ============================================================
Base = declarative_base()


# ------------------------------------------------------------
# 5. FUNCIÓN get_db (Dependency Injection)
# ------------------------------------------------------------
# Esta función es una "dependencia" de FastAPI.
# FastAPI tiene un sistema de "Dependency Injection" (DI) que
# permite inyectar recursos (como sesiones de BD) en tus
# endpoints automáticamente.
#
# ¿Cómo funciona?
#   1. FastAPI llama a get_db() antes de ejecutar el endpoint
#   2. Se crea una sesión nueva (db = SessionLocal())
#   3. La sesión se pasa al endpoint via el parámetro db=Depends(get_db)
#   4. El endpoint hace su trabajo con la BD
#   5. Al terminar, el bloque finally cierra la sesión
#
# ¿Qué es "yield"?
#   yield convierte esta función en un "generador".
#   El código ANTES del yield se ejecuta al inicio.
#   El código DESPUÉS del yield (en finally) se ejecuta al final.
#   Es equivalente a un context manager (with ... as ...).
#
# ¿Por qué usar try/finally?
#   Para garantizar que la sesión SIEMPRE se cierra, incluso
#   si ocurre un error. Si no cerramos las sesiones, agotamos
#   el pool de conexiones y la app se cae.
#
# PREREQUISITOS PARA ENTENDER ESTA FUNCIÓN:
#   - Generadores en Python (yield)
#   - Try/except/finally en Python
#   - Context managers en Python
#   - Dependency Injection (concepto de diseño de software)
# ============================================================
def get_db():
    """
    Generador que crea y provee una sesión de base de datos.

    Uso en un endpoint:
        from fastapi import Depends
        from database import get_db

        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            # db ya es una sesión lista para usar
            return db.query(Model).all()
    """
    db = SessionLocal()  # Creamos una nueva sesión
    try:
        yield db          # "Entregamos" la sesión al endpoint
    finally:
        db.close()        # Siempre cerramos la sesión al terminar
