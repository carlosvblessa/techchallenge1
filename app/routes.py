import datetime
from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from app.scraper import fetch_dados_embrapa
from app.scraper_import_export import fetch_dados_import_export
from app.auth import router as auth_router
from app.auth_token import get_current_user
from app.analytics import router as analytics_router
from app.database import engine
from app.schema import ProducaoItem, ProcessamentoItem, ComercializacaoItem, ImportacaoItem, ExportacaoItem, HealthResponse

router = APIRouter()

# Rotas abertas relacionadas à autenticação
router.include_router(auth_router)

# Endpoints protegidos por JWT
@router.get(
    "/producao",
    response_model=List[ProducaoItem],
    summary="Extrai dados de produção",
    tags=["Scraper"],
    responses={503: {"description": "Serviço indisponível"}}
)
def producao(usuario: str = Depends(get_current_user)):
    """
    Extrai os dados históricos de produção vitivinícola do Brasil diretamente do site da Embrapa.

    - Realiza scraping do arquivo mais recente disponível.
    - Persiste os dados no banco SQLite, evitando duplicações.
    - Retorna os 100 primeiros registros processados como exemplo.

    🔒 É necessário um token JWT válido para acessar este endpoint.
    """
    try:
        data = fetch_dados_embrapa("producao")
        
        # Se o scraper retornar um dict com erro, converte para HTTPException 503
        if isinstance(data, dict) and "erro" in data:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=data["erro"]
            )
        
        return data
    
    except HTTPException as http_err:
        # Repassa HTTPExceptions (como o 503 acima)
        raise http_err
    
    except Exception as e:
        # Qualquer outra falha gera um 503 com detalhe do erro
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    
@router.get(
    "/comercializacao",
    response_model=List[ComercializacaoItem],
    summary="Extrai dados de comercialização",
    tags=["Scraper"],
    responses={503: {"description": "Serviço indisponível"}}
)
def comercializacao(usuario: str = Depends(get_current_user)):
    """
    Retorna dados de comercialização de uvas e derivados no Brasil, conforme publicações da Embrapa.

    - Inclui histórico de volumes por produto e ano.
    - Evita duplicidade na base de dados.
    - Retorna amostra com até 100 registros.

    🔒 É necessário um token JWT válido para acessar este endpoint.
    """
    try:
        data = fetch_dados_embrapa("comercializacao")
        
        if isinstance(data, dict) and "erro" in data:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=data["erro"]
            )
            
        return data
        
    except HTTPException as http_err:
        raise http_err
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


@router.get(
    "/processamento",
    response_model=List[ProcessamentoItem],
    summary="Extrai dados de processamento",
    tags=["Scraper"],
    responses={503: {"description": "Serviço indisponível"}}
)
def processamento(usuario: str = Depends(get_current_user)):
    """
    Consulta os dados de processamento de uvas por cultivar no Brasil, extraídos da base da Embrapa.

    - O sistema coleta o arquivo `ProcessaViniferas.csv` e transforma em estrutura relacional.
    - Cada linha representa o volume processado por ano e variedade.

    🔒 É necessário um token JWT válido para acessar este endpoint.
    """
    try:
        data = fetch_dados_embrapa("processamento")
        
        if isinstance(data, dict) and "erro" in data:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=data["erro"]
            )
            
        return data
        
    except HTTPException as http_err:
        raise http_err
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


@router.get(
    "/importacao",
    response_model=List[ImportacaoItem],
    summary="Extrai dados de importação",
    tags=["Scraper"],
    responses={503: {"description": "Serviço indisponível"}}
)
def importacao(usuario: str = Depends(get_current_user)):
    """
    Apresenta os dados de importação de vinhos por país e por ano, conforme informações da Embrapa.

    - Inclui quantidade e valor em dólares por país.
    - Realiza parsing de arquivos com colunas duplicadas por ano.
    - Persistência controlada por `pais` e `ano`.

    🔒 É necessário um token JWT válido para acessar este endpoint.
    """
    try:
        data = fetch_dados_import_export("importacao")
        
        if isinstance(data, dict) and "erro" in data:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=data["erro"]
            )
            
        return data
        
    except HTTPException as http_err:
        raise http_err
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


@router.get(
    "/exportacao",
    response_model=List[ExportacaoItem],    
    summary="Extrai dados de exportação",
    tags=["Scraper"],
    responses={503: {"description": "Serviço indisponível"}}
)
def exportacao(usuario: str = Depends(get_current_user)):
    """
    Exibe os dados de exportação de vinhos por país, consolidados pela Embrapa ao longo dos anos.

    - O endpoint carrega o arquivo `expvinho.csv` e trata valores em `quantidade` e `USD`.
    - Cada país aparece com o respectivo volume exportado por ano.

    🔒 Este endpoint só pode ser acessado por usuários autenticados com JWT.
    """
    try:
        data = fetch_dados_import_export("exportacao")
        
        if isinstance(data, dict) and "erro" in data:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=data["erro"]
            )
            
        return data
        
    except HTTPException as http_err:
        raise http_err
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

# Rotas futuras de análise preditiva e estratégica
router.include_router(analytics_router, prefix="/analytics")

@router.get(
    "/",
    summary="Página inicial da API",
    tags=["Infra"],
    response_class=HTMLResponse,
    responses={
        200: {
            "description": "Página HTML de boas-vindas",
            "content": {
                "text/html": {
                    "example": """
<!DOCTYPE html>
<html lang='pt-BR'>
...
</html>"""
                }
            },
        }
    }
)
def root(request: Request):
    base = str(request.base_url).rstrip("/")
    docs_url = f"{base}/docs"
    redoc_url = f"{base}/redoc"
    year = datetime.datetime.utcnow().year
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Tech Challenge 01 - API Embrapa</title></head>
<body>
  <h1>🌼 Bem-vindo ao Tech Challenge 01 - API Embrapa!</h1>

  <h2>🔗 Endpoints Disponíveis:</h2>
  <ul>
    <li><code>GET  /</code>                         – Página inicial em HTML</li>
    <li><code>GET  /health</code>                   – Health-check da API e do Banco</li>
    <li><code>GET  /producao</code>                 – Extrai dados de produção 🔒</li>
    <li><code>GET  /comercializacao</code>          – Extrai dados de comercialização 🔒</li>
    <li><code>GET  /processamento</code>            – Extrai dados de processamento 🔒</li>
    <li><code>GET  /importacao</code>               – Extrai dados de importação 🔒</li>
    <li><code>GET  /exportacao</code>               – Extrai dados de exportação 🔒</li>
    <li><code>POST /solicitar-acesso</code>         – Solicitar acesso ao sistema</li>
    <li><code>POST /avaliar-acesso</code>           – Admin: aprovar/rejeitar acesso</li>
    <li><code>POST /status-acesso</code>            – Verificar status da solicitação</li>
    <li><code>POST /solicitacoes-pendentes</code>   – Admin: listar solicitações pendentes</li>
  </ul>

  <h2>🚀 Endpoints Planejados (Analytics):</h2>
  <ul>
    <li><code>GET /analytics/producao/previsao</code>               – Previsão futura da produção de uvas</li>
    <li><code>GET /analytics/exportacao/tendencias</code>           – Análise de tendências de exportação por país</li>
    <li><code>GET /analytics/comercializacao/ranking-regioes</code> – Ranking de regiões por comercialização</li>
    <li><code>GET /analytics/importacao/alerta-estoque</code>       – Recomendação de estoque para vinícolas</li>
  </ul>

  <h2>📄 Documentação Interativa:</h2>
  <p>
    <a href="{docs_url}" target="_blank">Acesse o Swagger UI</a><br/>
    <a href="{redoc_url}" target="_blank">Acesse o ReDoc UI</a>
  </p>

  <div class="footer">
    &copy; {year} API Embrapa – Desenvolvido com Python + FastAPI
  </div>
</body>
</html>"""
    return HTMLResponse(content=html, status_code=200)

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check da API e do banco",
    tags=["Infra"],
    responses={
        200: {
            "description": "Status de saúde da API e do banco",
            "content": {
                "application/json": {
                    "example": {"status": "OK", "db": "up"}
                }
            },
        }
    }
)
def health():
    try:
        conn = engine.connect()
        conn.close()
        db_status = "up"
    except Exception as e:
        db_status = "down"

    return {
        "status": "OK" if db_status == "up" else "FAIL",
        "db": db_status
    }
