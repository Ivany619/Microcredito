from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Emprestimo(BaseModel):
    emprestimo_id: Optional[int] = None
    cliente_id: int
    valor: Decimal = Field(..., max_digits=10, decimal_places=2)
    data_emprestimo: datetime
    data_vencimento: datetime
    status: str = Field('Ativo', description="Status do empréstimo (Ativo, Pago, Inadimplente)")

    @validator('status')
    def status_must_be_valid(cls, v):
        if v not in ['Ativo', 'Pago', 'Inadimplente']:
            raise ValueError('Status inválido')
        return v
