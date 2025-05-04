from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from app.database import Base
import enum
class StatusUsuario(enum.Enum):
    pendente = "pendente"
    aprovado = "aprovado"
    rejeitado = "rejeitado"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    senha = Column(String(60), nullable=False)  # Hash do bcrypt (60 chars)
    status = Column(Enum(StatusUsuario), default=StatusUsuario.pendente)  # Usando Enum
    ultimo_token = Column(String(256), nullable=True, index=True)
    data_token = Column(DateTime, nullable=True, default=datetime.utcnow)