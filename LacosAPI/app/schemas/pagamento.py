from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Pagamento(BaseModel):
    pagamento_id: Optional[int] = None
    emprestimo_id: int
    cliente_id: int
    valor_pago: Decimal
    data_pagamento: datetime
    metodo_pagamento: str
    referencia_pagamento: Optional[str] = None
