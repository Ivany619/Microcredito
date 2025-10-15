from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Penalizacao(BaseModel):
    penalizacao_id: Optional[int] = None
    emprestimo_id: int
    cliente_id: int
    tipo: str = Field(..., description="Tipo de penalização (Juro, Mora, Outro)")
    dias_atraso: Optional[int] = 0
    valor: Decimal = Field(..., max_digits=10, decimal_places=2)
    status: str = Field(..., description="Status da penalização (pendente, simulado, aplicada, cancelada)")
    data_aplicacao: datetime
    observacoes: Optional[str] = None

    @validator('tipo')
    def tipo_must_be_valid(cls, v):
        if v not in ['Juro', 'Mora', 'Outro']:
            raise ValueError('Tipo de penalização inválido')
        return v

    @validator('status')
    def status_must_be_valid(cls, v):
        if v not in ['pendente', 'simulado', 'aplicada', 'cancelada']:
            raise ValueError('Status de penalização inválido')
        return v

class PenalizacaoDetalhe(Penalizacao):
    # Campos adicionais apenas para respostas (não persistidos na tabela)
    nome_cliente: Optional[str] = None
    data_emprestimo: Optional[datetime] = None
    valor_emprestimo: Optional[Decimal] = None
    percentagem_aplicada: Optional[Decimal] = None  # Ex.: 75 para 15 dias de atraso
    total_penalizacoes: Optional[Decimal] = None    # Somatório das penalizações calculadas
    total_com_lucro: Optional[Decimal] = None       # total_penalizacoes + (valor_emprestimo * 1.20)
