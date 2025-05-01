from pydantic import BaseModel
from typing import Literal, Optional

# Schemas Pydantic
class HealthResponse(BaseModel):
    status: str
    db: str

class ProducaoItem(BaseModel):
    id: int
    id_original: int
    control: str
    produto: str
    ano: int
    producao_toneladas: float

class ComercializacaoItem(BaseModel):
    id: int
    id_original: int
    control: str
    produto: str
    ano: int
    volume_comercializado: float

class ProcessamentoItem(BaseModel):
    id: int
    id_original: int
    control: str
    cultivar: str
    ano: int
    volume_processado_litros: float

class ImportacaoItem(BaseModel):
    id: int
    pais: str
    ano: int
    quantidade: float
    valor_usd: float

class ExportacaoItem(BaseModel):
    id: int
    pais: str
    ano: int
    quantidade: float
    valor_usd: float

class SolicitarAcessoRequest(BaseModel):
    username: str
    password: str

class MessageResponse(BaseModel):
    mensagem: str

class AvaliarAcessoRequest(BaseModel):
    admin_username: str
    admin_password: str
    username: str
    status_aprovacao: Literal["aprovado", "rejeitado"]

class StatusAcessoResponse(BaseModel):
    status: str
    mensagem: Optional[str] = None
    user_id: Optional[int] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = None

class AdminAuthRequest(BaseModel):
    admin_username: str
    admin_password: str

class SolicitacaoPendente(BaseModel):
    username: str
    status: str