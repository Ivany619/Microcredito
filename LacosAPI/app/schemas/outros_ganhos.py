from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class OutrosGanhos(BaseModel):
    ganho_id: Optional[int] = None
    cliente_id: int
    descricao: str
    valor: Decimal
