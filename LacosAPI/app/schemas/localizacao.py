from pydantic import BaseModel
from typing import Optional

class Localizacao(BaseModel):
    localizacao_id: Optional[int] = None
    cliente_id: int
    bairro: Optional[str] = None
    numero_da_casa: Optional[str] = None
    quarteirao: Optional[str] = None
    cidade: str
    distrito: str
    provincia: str