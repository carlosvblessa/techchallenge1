from fastapi import APIRouter, Depends
from app.scraper import fetch_dados_embrapa
from app.scraper_import_export import fetch_dados_import_export
from app.auth import router as auth_router
from app.auth_token import get_current_user
from app.analytics import router as analytics_router

router = APIRouter()

# Endpoints protegidos por JWT
@router.get("/producao", summary="Extrai dados de produção")
def producao(usuario: str = Depends(get_current_user)):
    """
    Extrai os dados históricos de produção vitivinícola do Brasil diretamente do site da Embrapa.
    - Realiza scraping do arquivo mais recente disponível.
    - Persiste os dados no banco SQLite, evitando duplicações.
    - Retorna os 100 primeiros registros processados como exemplo.
    """
    return fetch_dados_embrapa("producao")

@router.get("/comercializacao", summary="Extrai dados de comercialização")
def comercializacao(usuario: str = Depends(get_current_user)):
    """
    Retorna dados de comercialização de uvas e derivados no Brasil.
    - Inclui histórico de volumes por produto e ano.
    - Retorna amostra com até 100 registros.
    """
    return fetch_dados_embrapa("comercializacao")

@router.get("/processamento", summary="Extrai dados de processamento")
def processamento(usuario: str = Depends(get_current_user)):
    """
    Consulta os dados de processamento de uvas por cultivar no Brasil.
    - Cada linha representa o volume processado por ano e variedade.
    """
    return fetch_dados_embrapa("processamento")

@router.get("/importacao", summary="Extrai dados de importação")
def importacao(usuario: str = Depends(get_current_user)):
    """
    Apresenta os dados de importação de vinhos por país e por ano.
    - Inclui quantidade e valor em dólares por país.
    - Persistência controlada por país e ano.
    """
    return fetch_dados_import_export("importacao")

@router.get("/exportacao", summary="Extrai dados de exportação")
def exportacao(usuario: str = Depends(get_current_user)):
    """
    Exibe os dados de exportação de vinhos por país, consolidados pela Embrapa.
    - Carrega o arquivo `expvinho.csv` e trata valores em quantidade e valor USD.
    """
    return fetch_dados_import_export("exportacao")

# Rotas abertas relacionadas à autenticação
router.include_router(auth_router)

# Rotas futuras de análise preditiva e estratégica
router.include_router(analytics_router, prefix="/analytics")