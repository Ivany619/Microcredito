from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class FuncionarioBase(BaseModel):
    username: str
    nome_completo: str
    email: str
    telefone: Optional[str] = None
    nivel_acesso: str
    ativo: Optional[bool] = True
    tentativas_login: Optional[int] = 0
    bloqueado: Optional[bool] = False
    data_bloqueio: Optional[datetime] = None

    @validator('nivel_acesso')
    def validar_nivel_acesso(cls, v):
        valores_permitidos = ['Administrador', 'Gestor', 'Operador', 'Consultor']
        if v not in valores_permitidos:
            raise ValueError(f'nivel_acesso deve ser um dos: {valores_permitidos}')
        return v

class FuncionarioCreate(FuncionarioBase):
    senha: str

class FuncionarioUpdate(FuncionarioBase):
    senha: Optional[str] = None

class Funcionario(FuncionarioBase):
    funcionario_id: Optional[int] = None
    data_cadastro: Optional[datetime] = None
    ultimo_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class FuncionarioResponse(FuncionarioBase):
    funcionario_id: int
    data_cadastro: Optional[datetime] = None
    ultimo_login: Optional[datetime] = None

    class Config:
        from_attributes = True
