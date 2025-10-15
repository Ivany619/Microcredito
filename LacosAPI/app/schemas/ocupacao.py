from pydantic import BaseModel, validator
from typing import Optional
from decimal import Decimal

class OcupacaoBase(BaseModel):
    cliente_id: int
    codigo: str
    nome: str
    descricao: Optional[str] = None
    categoria_risco: str
    renda_minima: Optional[Decimal] = None
    setor_economico: str
    estabilidade_emprego: str
    ativo: bool = True

    @validator('categoria_risco')
    def validar_categoria_risco(cls, v):
        valores_permitidos = ['Muito Baixo', 'Baixo', 'Medio', 'Alto', 'Muito Alto']
        if v not in valores_permitidos:
            raise ValueError(f'categoria_risco deve ser um dos: {valores_permitidos}')
        return v

    @validator('setor_economico')
    def validar_setor_economico(cls, v):
        valores_permitidos = ['Primario', 'Secundario', 'Terciario', 'Quaternario']
        if v not in valores_permitidos:
            raise ValueError(f'setor_economico deve ser um dos: {valores_permitidos}')
        return v

    @validator('estabilidade_emprego')
    def validar_estabilidade_emprego(cls, v):
        valores_permitidos = ['Alta', 'Media', 'Baixa', 'Sazonal']
        if v not in valores_permitidos:
            raise ValueError(f'estabilidade_emprego deve ser um dos: {valores_permitidos}')
        return v

class OcupacaoCriar(OcupacaoBase):
    pass

class OcupacaoAtualizar(BaseModel):
    codigo: Optional[str] = None
    nome: Optional[str] = None
    descricao: Optional[str] = None
    categoria_risco: Optional[str] = None
    renda_minima: Optional[Decimal] = None
    setor_economico: Optional[str] = None
    estabilidade_emprego: Optional[str] = None
    ativo: Optional[bool] = None

    @validator('categoria_risco')
    def validar_categoria_risco(cls, v):
        if v is not None:
            valores_permitidos = ['Muito Baixo', 'Baixo', 'Medio', 'Alto', 'Muito Alto']
            if v not in valores_permitidos:
                raise ValueError(f'categoria_risco deve ser um dos: {valores_permitidos}')
        return v

    @validator('setor_economico')
    def validar_setor_economico(cls, v):
        if v is not None:
            valores_permitidos = ['Primario', 'Secundario', 'Terciario', 'Quaternario']
            if v not in valores_permitidos:
                raise ValueError(f'setor_economico deve ser um dos: {valores_permitidos}')
        return v

    @validator('estabilidade_emprego')
    def validar_estabilidade_emprego(cls, v):
        if v is not None:
            valores_permitidos = ['Alta', 'Media', 'Baixa', 'Sazonal']
            if v not in valores_permitidos:
                raise ValueError(f'estabilidade_emprego deve ser um dos: {valores_permitidos}')
        return v

class Ocupacao(OcupacaoBase):
    ocupacao_id: int

    class Config:
        from_attributes = True