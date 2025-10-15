from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class NotificacaoBase(BaseModel):
    cliente_id: Optional[int] = None
    tipo: str
    mensagem: str
    status: Optional[str] = "Pendente"

    @validator('tipo')
    def validar_tipo(cls, v):
        valores_permitidos = ['Lembrete de Pagamento', 'Atraso no Pagamento', 'Confirmação de Pagamento', 'Confirmação de Empréstimo', 'Penalização Aplicada', 'Outro', 'ADMIN_EMPRESTIMO', 'ADMIN_PAGAMENTO', 'ADMIN_PENALIZACAO']
        if v not in valores_permitidos:
            raise ValueError(f'tipo deve ser um dos: {valores_permitidos}')
        return v

    @validator('status')
    def validar_status(cls, v):
        valores_permitidos = ['Enviado', 'Lido', 'Pendente']
        if v not in valores_permitidos:
            raise ValueError(f'status deve ser um dos: {valores_permitidos}')
        return v

class NotificacaoCriar(NotificacaoBase):
    pass

class NotificacaoAtualizar(BaseModel):
    status: str

    @validator('status')
    def validar_status(cls, v):
        valores_permitidos = ['Enviado', 'Lido', 'Pendente']
        if v not in valores_permitidos:
            raise ValueError(f'status deve ser um dos: {valores_permitidos}')
        return v

class Notificacao(NotificacaoBase):
    notificacao_id: int
    data_envio: datetime
    cliente_id: Optional[int] = None  # Override to make it optional

    class Config:
        from_attributes = True
