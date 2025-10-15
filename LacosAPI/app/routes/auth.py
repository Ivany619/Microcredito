from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.auth import autenticar_funcionario, criar_token_acesso, TokenData
from app.schemas.funcionario import Funcionario
from datetime import timedelta
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

TOKEN_EXPIRA_MINUTOS = 480  # 8 horas = 8 * 60 = 480 minutos

@router.post("/token")
@limiter.limit("5/5minutes")
async def login_para_token_acesso(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    funcionario = autenticar_funcionario(form_data.username, form_data.password)
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de utilizador ou palavra-passe incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=TOKEN_EXPIRA_MINUTOS)
    access_token = criar_token_acesso(
        data={"sub": funcionario['username']}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

# Rota alternativa sem rate limiting para desenvolvimento
@router.post("/token-alt")
async def login_para_token_acesso_alternativo(form_data: OAuth2PasswordRequestForm = Depends()):
    """Rota de login alternativa sem limites de taxa - usar apenas para desenvolvimento"""
    funcionario = autenticar_funcionario(form_data.username, form_data.password)
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de utilizador ou palavra-passe incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=TOKEN_EXPIRA_MINUTOS)
    access_token = criar_token_acesso(
        data={"sub": funcionario['username']}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
