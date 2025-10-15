from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class HistoricoCreditoBase(BaseModel):
    cliente_id: int
    emprestimo_anterior: Optional[float] = None
    status: str
    data_ultimo_pagamento: Optional[datetime] = None

    @validator('status')
    def validar_status(cls, v):
        valores_permitidos = ['Pago', 'Inadimplente', 'Atrasado']
        if v not in valores_permitidos:
            raise ValueError(f'status deve ser um dos: {valores_permitidos}')
        return v

class HistoricoCreditoCriar(HistoricoCreditoBase):
    pass

class HistoricoCreditoAtualizar(BaseModel):
    emprestimo_anterior: Optional[float] = None
    status: Optional[str] = None
    data_ultimo_pagamento: Optional[datetime] = None

    @validator('status')
    def validar_status(cls, v):
        if v is not None:
            valores_permitidos = ['Pago', 'Inadimplente', 'Atrasado']
            if v not in valores_permitidos:
                raise ValueError(f'status deve ser um dos: {valores_permitidos}')
        return v

class HistoricoCredito(HistoricoCreditoBase):
    historico_id: int

    class Config:
        from_attributes = True
