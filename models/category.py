from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey

# func: funciones SQL (como now() para obtener la fecha actual)
from sqlalchemy.sql import func

# relationship: define relaciones entre modelos (joins)
from sqlalchemy.orm import relationship

# Importamos Base desde database.py
# TODOS los modelos deben heredar de esta clase
from core.database import Base

# ============================================================
# MODELO: Category (Categoría)
# ============================================================
# Representa una categoría a la que puede pertenecer una tarea.
# Esto nos permite organizar las tareas (Ej: Trabajo, Personal)
#
# Relación: Una categoría puede tener MUCHAS tareas.
#           Una tarea pertenece a UNA categoría (o ninguna).
#           Esto es una relación "One-to-Many" (Uno a Muchos).
# ============================================================
class Category(Base):
    """
    Modelo para categorías de tareas.

    Tabla en SQLite: categories

    Relación con Task:
        Category (1) ----< Task (muchos)
        Una categoría puede tener múltiples tareas.
    """

    # __tablename__: le dice a SQLAlchemy cómo llamar la tabla en la BD
    # Por convención: nombres en minúsculas y plural
    __tablename__ = "categories"

    # ------------------------------------------------------------
    # COLUMNAS DE LA TABLA
    # ------------------------------------------------------------

    # PRIMARY KEY (Llave primaria): identifica de forma única cada fila
    # index=True: crea un índice para búsquedas más rápidas
    # autoincrement es automático en Integer + primary_key=True
    id = Column(Integer, primary_key=True, index=True)

    # Nombre de la categoría
    # String(50): texto de máximo 50 caracteres
    # unique=True: no pueden existir dos categorías con el mismo nombre
    # nullable=False: OBLIGATORIO, no puede ser NULL
    name = Column(String(50), unique=True, nullable=False)

    # Descripción opcional de la categoría
    # nullable=True: puede ser NULL (es decir, opcional)
    description = Column(String(200), nullable=True)

    # ------------------------------------------------------------
    # RELATIONSHIP (Relación ORM)
    # ------------------------------------------------------------
    # "tasks" es un atributo virtual (no es una columna real en la BD)
    # SQLAlchemy lo llena automáticamente con las tareas de esta categoría
    #
    # back_populates="category":
    #   Le dice a SQLAlchemy que el modelo Task tiene un atributo
    #   llamado "category" que apunta de vuelta a Category.
    #   Esto crea una relación bidireccional.
    #
    # Uso:
    #   mi_categoria.tasks  --> lista de Task que pertenecen a esta categoría
    tasks = relationship("Task", back_populates="category")

    def __repr__(self):
        """
        __repr__: Representación en texto del objeto.
        Útil para debugging y para imprimir objetos.
        Python llama a __repr__ cuando haces print(objeto).
        """
        return f"<Category id={self.id} name='{self.name}'>"
