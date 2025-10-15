from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class AutenticacaoClienteBase(BaseModel):
    cliente_id: int
    username: str
    password_hash: str
    tentativas_login: int = 0
    bloqueado: bool = False
    data_bloqueio: Optional[datetime] = None

class AutenticacaoClienteCriar(BaseModel):
    cliente_id: int
    username: str
    password: str 

    @validator('username')
    def validar_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username deve ter pelo menos 3 caracteres')
        return v

    @validator('password')
    def validar_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password deve ter pelo menos 6 caracteres')
        return v

class AutenticacaoClienteAtualizar(BaseModel):
    password: Optional[str] = None  
    tentativas_login: Optional[int] = None
    bloqueado: Optional[bool] = None
    data_bloqueio: Optional[datetime] = None

    @validator('password')
    def validar_password(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError('Password deve ter pelo menos 6 caracteres')
        return v

class AutenticacaoCliente(AutenticacaoClienteBase):
    autenticacao_id: int
    data_criacao: datetime
    ultimo_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class LoginClienteRequest(BaseModel):
    username: str
    password: str

class LoginClienteResponse(BaseModel):
    access_token: str
    token_type: str
    cliente_id: int
    username: str