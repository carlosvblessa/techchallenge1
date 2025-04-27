from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from datetime import datetime
from app.database import Base

class Producao(Base):
    __tablename__ = "producao"
    __table_args__ = (UniqueConstraint('id_original', 'ano', name='_producao_uc'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_original = Column(Integer)
    control = Column(String)
    produto = Column(String)
    ano = Column(Integer, index=True)
    producao_toneladas = Column(Float)

class Comercializacao(Base):
    __tablename__ = "comercializacao"
    __table_args__ = (UniqueConstraint('id_original', 'ano', name='_comercializacao_uc'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_original = Column(Integer)
    control = Column(String)
    produto = Column(String)
    ano = Column(Integer, index=True)
    volume_comercializado = Column(Float)

class Processamento(Base):
    __tablename__ = "processamento"
    __table_args__ = (UniqueConstraint('id_original', 'ano', name='_processamento_uc'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_original = Column(Integer)
    control = Column(String)
    cultivar = Column(String)
    ano = Column(Integer, index=True)
    volume_processado_litros = Column(Float)

class Importacao(Base):
    __tablename__ = "importacao"
    __table_args__ = (UniqueConstraint('pais', 'ano', name='_importacao_uc'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    pais = Column(String)
    ano = Column(Integer, index=True)
    quantidade = Column(Float)
    valor_usd = Column(Float)

class Exportacao(Base):
    __tablename__ = "exportacao"
    __table_args__ = (UniqueConstraint('pais', 'ano', name='_exportacao_uc'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    pais = Column(String)
    ano = Column(Integer, index=True)
    quantidade = Column(Float)
    valor_usd = Column(Float)
