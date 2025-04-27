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

    🔒 Este endpoint requer autenticação via token JWT.
    """
    return fetch_dados_embrapa("producao")

@router.get("/comercializacao", summary="Extrai dados de comercialização")
def comercializacao(usuario: str = Depends(get_current_user)):
    """
    Retorna dados de comercialização de uvas e derivados no Brasil, conforme publicações da Embrapa.

    - Inclui histórico de volumes por produto e ano.
    - Evita duplicidade na base de dados.
    - Retorna amostra com até 100 registros.

    🔒 É necessário um token JWT válido para acessar este endpoint.
    """
    return fetch_dados_embrapa("comercializacao")

@router.get("/processamento", summary="Extrai dados de processamento")
def processamento(usuario: str = Depends(get_current_user)):
    """
    Consulta os dados de processamento de uvas por cultivar no Brasil, extraídos da base da Embrapa.

    - O sistema coleta o arquivo `ProcessaViniferas.csv` e transforma em estrutura relacional.
    - Cada linha representa o volume processado por ano e variedade.

    🔒 Acesso restrito a usuários autenticados com token JWT.
    """
    return fetch_dados_embrapa("processamento")

@router.get("/importacao", summary="Extrai dados de importação")
def importacao(usuario: str = Depends(get_current_user)):
    """
    Apresenta os dados de importação de vinhos por país e por ano, conforme informações da Embrapa.

    - Inclui quantidade e valor em dólares por país.
    - Realiza parsing de arquivos com colunas duplicadas por ano.
    - Persistência controlada por `pais` e `ano`.

    🔒 Necessário fornecer token JWT no cabeçalho da requisição.
    """
    return fetch_dados_import_export("importacao")

@router.get("/exportacao", summary="Extrai dados de exportação")
def exportacao(usuario: str = Depends(get_current_user)):
    """
    Exibe os dados de exportação de vinhos por país, consolidados pela Embrapa ao longo dos anos.

    - O endpoint carrega o arquivo `expvinho.csv` e trata valores em `quantidade` e `USD`.
    - Cada país aparece com o respectivo volume exportado por ano.

    🔒 Este endpoint só pode ser acessado por usuários autenticados com JWT.
    """
    return fetch_dados_import_export("exportacao")

# Rotas abertas relacionadas à autenticação
router.include_router(auth_router)
router.include_router(analytics_router, prefix="/analytics")
