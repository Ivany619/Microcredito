from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime

class Cliente(BaseModel):
    cliente_id: Optional[int] = None
    nome: str
    sexo: str = Field(..., description="Sexo do cliente (Masculino, Feminino, Outro)")
    telefone: str
    email: Optional[str] = None
    nacionalidade: str = Field('Moçambicana', description="Nacionalidade do cliente (Moçambicana, Estrangeira)")
    data_nascimento: date
    data_cadastro: Optional[datetime] = None

    @validator('sexo')
    def sexo_must_be_valid(cls, v):
        if v not in ['Masculino', 'Feminino', 'Outro']:
            raise ValueError('Sexo inválido')
        return v

    @validator('nacionalidade')
    def nacionalidade_must_be_valid(cls, v):
        if v not in ['Moçambicana', 'Estrangeira']:
            raise ValueError('Nacionalidade inválida')
        return v