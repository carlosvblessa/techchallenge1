from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    senha = Column(String)
    status = Column(String, default="pendente")  # pendente, aprovado, rejeitado
    ultimo_token = Column(String, nullable=True)
    data_token = Column(DateTime, nullable=True, default=datetime.utcnow)