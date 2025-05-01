from fastapi import FastAPI
from app.routes import router
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.models import Producao

# Criação das tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tech Challenge 01 - API Embrapa",
    description="Consulta pública dos dados de vitivinicultura da Embrapa",
    version="1.0.0",
    docs_url="/docs",       # Mantém o Swagger UI
    redoc_url="/redoc"      # Para desativar:  redoc_url=None
)

# Libera CORS se necessário
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
