from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from app.database import SessionLocal
from app.models_usuario import Usuario
from app.utils import create_access_token, verify_token
from app.config import settings

router = APIRouter()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/solicitar-acesso")
def solicitar_acesso(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Permite que um novo usuário solicite acesso ao sistema.

    - O status da solicitação ficará como **pendente** até a avaliação por um administrador.
    - Cada usuário pode realizar apenas uma solicitação.
    - A autenticação final só será possível após aprovação.

    **Parâmetros:**
    - `username`: nome de usuário desejado
    - `password`: senha para futura autenticação

    **Exemplo:**
    ```
    username=joao
    password=1234
    ```
    """
    existing = db.query(Usuario).filter_by(username=form.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Usuário já solicitou acesso.")
    novo = Usuario(username=form.username, senha=form.password, status="pendente")
    db.add(novo)
    db.commit()
    return {"mensagem": "Solicitação de acesso registrada. Aguarde avaliação."}

@router.post("/avaliar-acesso")
def avaliar_acesso(username: str, status_aprovacao: str, admin: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Avaliação de solicitações de acesso por um **usuário administrador**.

    - O administrador deve se autenticar com `username=admin` e `password=admin123`.
    - Pode aprovar ou rejeitar solicitações pendentes de novos usuários.

    **Parâmetros (form-data do admin):**
    - `username`: admin
    - `password`: admin123

    **Query Params:**
    - `username`: nome do solicitante a ser avaliado
    - `status_aprovacao`: `"aprovado"` ou `"rejeitado"`

    **Exemplo:**
    ```
    /avaliar-acesso?username=joao&status_aprovacao=aprovado
    ```
    """
    if admin.username != ADMIN_USERNAME or admin.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Acesso negado ao avaliador.")
    if status_aprovacao not in ["aprovado", "rejeitado"]:
        raise HTTPException(status_code=400, detail="Status deve ser 'aprovado' ou 'rejeitado'.")

    usuario = db.query(Usuario).filter_by(username=username).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    usuario.status = status_aprovacao
    if status_aprovacao == "aprovado":
        token = create_access_token(data={"sub": usuario.username})
        usuario.ultimo_token = token
        usuario.data_token = datetime.utcnow()
    db.commit()
    return {"mensagem": f"Usuário {username} foi {status_aprovacao}."}

@router.post("/status-acesso")
def status_acesso(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Permite ao solicitante verificar se teve seu acesso **aprovado ou rejeitado**.

    - Se aprovado, um `access_token` é retornado automaticamente (incluindo renovação caso expirado).
    - Se rejeitado, recebe uma mensagem de recusa.
    - Se pendente, recebe mensagem de aguardo.

    **Parâmetros:**
    - `username`: nome de usuário usado na solicitação
    - `password`: senha informada na solicitação

    **Exemplo:**
    ```
    username=joao
    password=1234
    ```
    """
    usuario = db.query(Usuario).filter_by(username=form.username).first()
    if not usuario or usuario.senha != form.password:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    if usuario.status == "pendente":
        return {"status": "pendente", "mensagem": "Sua solicitação ainda não foi avaliada."}
    elif usuario.status == "rejeitado":
        return {"status": "rejeitado", "mensagem": "Sua solicitação foi recusada."}
    elif usuario.status == "aprovado":
        if not usuario.ultimo_token or usuario.data_token + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) < datetime.utcnow():
            token = create_access_token(data={"sub": usuario.username})
            usuario.ultimo_token = token
            usuario.data_token = datetime.utcnow()
            db.commit()
        return {
            "status": "aprovado",
            "access_token": usuario.ultimo_token,
            "token_type": "bearer"
        }

@router.post("/solicitacoes-pendentes")
def listar_solicitacoes_pendentes(admin: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Lista todos os usuários que solicitaram acesso e aguardam avaliação.

    - **Somente o administrador** pode visualizar esta lista.
    - Ideal para uso antes de chamar `/avaliar-acesso`.

    **Parâmetros (form-data do admin):**
    - `username`: admin
    - `password`: admin123

    **Resposta:**
    ```json
    [
      { "username": "joao", "status": "pendente" },
      { "username": "maria", "status": "pendente" }
    ]
    ```
    """
    if admin.username != ADMIN_USERNAME or admin.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Acesso negado ao avaliador.")
    pendentes = db.query(Usuario).filter_by(status="pendente").all()
    return [{"username": u.username, "status": u.status} for u in pendentes]