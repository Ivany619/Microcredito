from pydantic import BaseModel
from typing import Optional

class Testemunha(BaseModel):
    testemunha_id: Optional[int] = None
    cliente_id: int
    nome: str
    telefone: str
    tipo_relacao: str
