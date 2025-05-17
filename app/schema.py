from typing import TypeVar, Generic, List, Optional, Literal
from pydantic import BaseModel, HttpUrl, Field, ConfigDict

T = TypeVar("T")

# # —— Config Base ——
# class ConfigBase:
#     orm_mode = True

class BaseModelConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# —— Model de health check ——
class HealthResponse(BaseModelConfig):
    status: str
    db: str

# —— Bases com restrição de ano ——
class BaseItem1970_2023(BaseModelConfig):
    id: int = Field(..., ge=1)
    id_original: int = Field(..., ge=1)
    ano: int = Field(..., ge=1970, le=2023)

class BaseItem1970_2024(BaseModelConfig):
    id: int = Field(..., ge=1)
    ano: int = Field(..., ge=1970, le=2024)

# —— Bases específicas ——
class BaseVitviniculturaItem(BaseItem1970_2023):
    control: Optional[str]
    produto: str

class BaseCultivarItem(BaseItem1970_2023):
    control: Optional[str]
    cultivar: str
    volume_processado_litros: float
class BaseComercioExteriorItem(BaseItem1970_2024):
    pais: str
    quantidade: float
    valor_usd: float

# —— Itens específicos ——
class ProducaoItem(BaseVitviniculturaItem):
    producao_toneladas: float

class ComercializacaoItem(BaseVitviniculturaItem):
    volume_comercializado: float

class ProcessamentoItem(BaseCultivarItem):
    pass

class ImportacaoItem(BaseComercioExteriorItem):
    pass

class ExportacaoItem(BaseComercioExteriorItem):
    pass

class PaginatedResponse(BaseModel, Generic[T]):
    arquivo: str
    url_download: HttpUrl
    registros: List[T]

# —— Alias para facilitar ——
ProducaoResponse = PaginatedResponse[ProducaoItem]
ComercializacaoResponse = PaginatedResponse[ComercializacaoItem]
ProcessamentoResponse = PaginatedResponse[ProcessamentoItem]
ImportacaoResponse = PaginatedResponse[ImportacaoItem]
ExportacaoResponse = PaginatedResponse[ExportacaoItem]

# —— Autenticação ——
class Credentials(BaseModelConfig):
    username: str
    password: str

class SolicitarAcessoRequest(Credentials):
    pass

class AdminAuthRequest(BaseModelConfig):
    admin_username: str
    admin_password: str
class AvaliarAcessoRequest(AdminAuthRequest):
    username: str
    status_aprovacao: Literal["aprovado", "rejeitado"]
class StatusAcessoResponse(BaseModelConfig):
    status: str
    mensagem: Optional[str] = None
    user_id: Optional[int] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = None

class MessageResponse(BaseModelConfig):
    mensagem: str

class SolicitacaoPendente(BaseModelConfig):
    username: str
    status: str
