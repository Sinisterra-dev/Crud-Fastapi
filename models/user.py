from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from core.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(500), unique=False, nullable=False)
    is_active = Column(Boolean, default= True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    rol = Column(String(50), unique=False, nullable=False)
    tasks = relationship("Task", back_populates="user")







