from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Penhor(BaseModel):
    penhor_id: Optional[int] = None
    cliente_id: int
    descricao_item: str
    valor_estimado: Decimal
    data_penhora: datetime
