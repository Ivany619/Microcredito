from pydantic import BaseModel, validator
from typing import Optional

# Define allowed document types based on database constraint
TIPOS_DOCUMENTO_PERMITIDOS = [
    'BI', 'Passaporte', 'Carta de Conducao', 'NUIT', 'Contrato Microcredito',
    'Livrete', 'DIRE', 'Certidao de Nascimento', 'Certificado de Habilitacoes',
    'Comprovativo de Residencia', 'Talao de Deposito', 'Outro'
]

class DocumentoCreate(BaseModel):
    cliente_id: int
    tipo_documento: str
    numero_documento: str
    
    @validator('tipo_documento')
    def validate_tipo_documento(cls, v):
        if v not in TIPOS_DOCUMENTO_PERMITIDOS:
            raise ValueError(f'tipo_documento deve ser um dos seguintes: {", ".join(TIPOS_DOCUMENTO_PERMITIDOS)}')
        return v

class Documento(BaseModel):
    documento_id: Optional[int] = None
    cliente_id: int
    tipo_documento: str
    numero_documento: str
    arquivo: Optional[bytes] = None
    
    @validator('tipo_documento')
    def validate_tipo_documento(cls, v):
        if v not in TIPOS_DOCUMENTO_PERMITIDOS:
            raise ValueError(f'tipo_documento deve ser um dos seguintes: {", ".join(TIPOS_DOCUMENTO_PERMITIDOS)}')
        return v

class DocumentoResponse(BaseModel):
    documento_id: int
    cliente_id: int
    tipo_documento: str
    numero_documento: str
