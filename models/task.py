from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey

# func: funciones SQL (como now() para obtener la fecha actual)
from sqlalchemy.sql import func

# relationship: define relaciones entre modelos (joins)
from sqlalchemy.orm import relationship

# Importamos Base desde database.py
# TODOS los modelos deben heredar de esta clase
from core.database import Base

# ============================================================
# MODELO: Task (Tarea)
# ============================================================
# Representa una tarea en el sistema de gestión de tareas.
# Esta es la entidad principal de nuestro CRUD.
#
# Columnas:
#   - id: identificador único
#   - title: título de la tarea (obligatorio)
#   - description: descripción detallada (opcional)
#   - completed: si la tarea está completada o no
#   - priority: prioridad (1=baja, 2=media, 3=alta)
#   - category_id: FK que relaciona con Category
#   - created_at: cuándo se creó (automático)
#   - updated_at: cuándo fue la última modificación (automático)
# ============================================================
class Task(Base):
    """
    Modelo principal: representa una tarea en el sistema.

    Tabla en SQLite: tasks

    Relación con Category:
        Task (muchos) >---- Category (1)
        Cada tarea puede pertenecer a una categoría.
    """

    __tablename__ = "tasks"

    # ID único autoincremental - PRIMARY KEY
    id = Column(Integer, primary_key=True, index=True)

    # Título de la tarea
    # String(100): máximo 100 caracteres
    # index=True: se crea un índice porque buscaremos por título frecuentemente
    # nullable=False: el título es OBLIGATORIO
    title = Column(String(100), index=True, nullable=False)

    # Descripción detallada de la tarea (opcional)
    # Text: para textos largos (sin límite fijo, a diferencia de String)
    # nullable=True: es opcional, puede no tener descripción
    description = Column(Text, nullable=True)

    # Estado de la tarea: completada (True) o pendiente (False)
    # default=False: por defecto, las tareas nuevas están pendientes
    completed = Column(Boolean, default=False, nullable=False)

    # Prioridad de la tarea
    # 1 = Baja, 2 = Media, 3 = Alta
    # default=1: por defecto, las tareas son de baja prioridad
    priority = Column(Integer, default=1, nullable=False)

    # FOREIGN KEY (Llave foránea): referencia a la tabla categories
    # "categories.id" significa: columna "id" de la tabla "categories"
    # nullable=True: la tarea puede no tener categoría (es opcional)
    # ondelete="SET NULL": si se elimina la categoría, category_id queda NULL
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True
    )

    # Fecha y hora de creación
    # server_default=func.now(): la BD asigna automáticamente la fecha actual
    # Diferencia con default=: server_default lo hace el servidor de BD,
    # default= lo hace Python antes de enviar a la BD
    created_at = Column(DateTime, server_default=func.now())

    # Fecha y hora de última actualización
    # onupdate=func.now(): SQLAlchemy actualiza este campo automáticamente
    # cada vez que el registro se modifica
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # ------------------------------------------------------------
    # RELATIONSHIP con Category
    # ------------------------------------------------------------
    # "category" es el atributo virtual que da acceso al objeto Category
    # back_populates="tasks": conecta con el relationship en Category
    #
    # Uso:
    #   mi_tarea.category  --> el objeto Category de esa tarea
    #   mi_tarea.category.name  --> el nombre de la categoría
    category = relationship("Category", back_populates="tasks")

    def __repr__(self):
        return (
            f"<Task id={self.id} title='{self.title}' "
            f"completed={self.completed} priority={self.priority}>"
        )
