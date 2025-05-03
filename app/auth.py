from fastapi import APIRouter, HTTPException, Depends, status, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
from app.database import SessionLocal
from app.models_usuario import Usuario
from app.utils import create_access_token, verify_token
from app.config import settings
from typing import List
from app.schema import (
    SolicitarAcessoRequest,
    MessageResponse,
    AvaliarAcessoRequest,
    StatusAcessoResponse,
    AdminAuthRequest,
    SolicitacaoPendente
)

router = APIRouter()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/solicitar-acesso",
    response_model=MessageResponse,
    summary="Permite que um novo usuário solicite acesso ao sistema",
    tags=["Acesso"]
)
def solicitar_acesso(
    data: SolicitarAcessoRequest = Body(
        ...,
        example={"username": "joao", "password": "1234"}
    ),
    db: Session = Depends(get_db)
):
    """
    Permite que um novo usuário solicite acesso ao sistema.

    - O status da solicitação ficará como **pendente** até a avaliação por um administrador.
    - Cada usuário pode realizar apenas uma solicitação.
    - A autenticação final só será possível após aprovação.
    """
    existing = db.query(Usuario).filter_by(username=data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Usuário já solicitou acesso.")
    novo = Usuario(username=data.username, senha=data.password, status="pendente")
    db.add(novo)
    db.commit()
    return {"mensagem": "Solicitação de acesso registrada. Aguarde avaliação."}


@router.post(
    "/avaliar-acesso",
    response_model=MessageResponse,
    summary="Avaliação de solicitações de acesso por um usuário administrador",
    tags=["Acesso"]
)
def avaliar_acesso(
    data: AvaliarAcessoRequest = Body(
        ...,
        example={
            "admin_username": "admin",
            "admin_password": "admin123",
            "username": "joao",
            "status_aprovacao": "aprovado"
        }
    ),
    db: Session = Depends(get_db)
):
    """
    Avaliação de solicitações de acesso por um **usuário administrador**.

    - O administrador deve informar `admin_username` e `admin_password`.
    - Pode aprovar ou rejeitar solicitações pendentes de novos usuários.
    """
    # validação do admin
    if data.admin_username != ADMIN_USERNAME or data.admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Acesso negado ao avaliador.")

    usuario = db.query(Usuario).filter_by(username=data.username).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    usuario.status = data.status_aprovacao
    if data.status_aprovacao == "aprovado":
        token = create_access_token(data={"sub": usuario.username})
        usuario.ultimo_token = token
        usuario.data_token = datetime.now(timezone.utc)
    db.commit()

    return {"mensagem": f"Usuário {data.username} foi {data.status_aprovacao}."}


@router.post(
    "/status-acesso",
    response_model=StatusAcessoResponse,
    summary="Permite ao solicitante verificar status da solicitação de acesso",
    tags=["Acesso"]
)
def status_acesso(
    form: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Permite ao solicitante verificar se teve seu acesso **aprovado ou rejeitado**.

    - Se aprovado, um `access_token` é retornado automaticamente (incluindo renovação caso expirado).
    - Se rejeitado, recebe uma mensagem de recusa.
    - Se pendente, recebe mensagem de aguardo.

    **Body JSON:**  
    - `username`: nome de usuário usado na solicitação  
    - `password`: senha informada na solicitação
    """
    usuario = db.query(Usuario).filter_by(username=form.username).first()
    if not usuario or usuario.senha != form.password:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    if usuario.status == "pendente":
        return {"status": "pendente", "mensagem": "Sua solicitação ainda não foi avaliada."}

    if usuario.status == "rejeitado":
        return {"status": "rejeitado", "mensagem": "Sua solicitação foi recusada."}

    # aprovado
    # Converte data_token para UTC-aware se for naive
    if usuario.data_token and usuario.data_token.tzinfo is None:
        usuario.data_token = usuario.data_token.replace(tzinfo=timezone.utc)
    # valida se precisa renovar token
    expires = usuario.data_token + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    if not usuario.ultimo_token or expires < datetime.now(timezone.utc):
        token = create_access_token(data={"sub": usuario.username})
        usuario.ultimo_token = token
        usuario.data_token = datetime.now(timezone.utc)
        db.commit()

    return {
        "status": "aprovado",
        "user_id": usuario.id,
        "access_token": usuario.ultimo_token,
        "token_type": "bearer"
    }


@router.post(
    "/solicitacoes-pendentes",
    response_model=List[SolicitacaoPendente],
    summary="Lista todos os usuários que solicitaram acesso e aguardam avaliação",
    tags=["Acesso"]
)
def listar_solicitacoes_pendentes(
    data: AdminAuthRequest = Body(
        ...,
        example={"admin_username": "admin", "admin_password": "admin123"}
    ),
    db: Session = Depends(get_db)
):
    """
    Lista todos os usuários que solicitaram acesso e aguardam avaliação.

    - **Somente o administrador** pode visualizar esta lista.
    - Ideal para uso antes de chamar `/avaliar-acesso`.

    **Body JSON:**
    - `admin_username`: usuário administrador  
    - `admin_password`: senha do administrador

    **Exemplo:**
    ```json
    {
      "admin_username": "admin",
      "admin_password": "admin123"
    }
    ```
    """
    if data.admin_username != ADMIN_USERNAME or data.admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Acesso negado ao avaliador.")

    pendentes = db.query(Usuario).filter_by(status="pendente").all()
    return [{"username": u.username, "status": u.status} for u in pendentes]