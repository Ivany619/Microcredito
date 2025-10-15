from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List
from app.schemas.documento import Documento, DocumentoCreate, DocumentoResponse, TIPOS_DOCUMENTO_PERMITIDOS
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
import psycopg2.extras
import io

router = APIRouter()

@router.post("/criar", response_model=DocumentoResponse)
def criar_documento(
    cliente_id: int = Form(...),
    tipo_documento: str = Form(...),
    numero_documento: str = Form(...),
    arquivo: UploadFile = File(...),
    funcionario_atual: dict = Depends(get_current_funcionario)
):
    if tipo_documento not in TIPOS_DOCUMENTO_PERMITIDOS:
        raise HTTPException(
            status_code=400, 
            detail=f"tipo_documento deve ser um dos seguintes: {', '.join(TIPOS_DOCUMENTO_PERMITIDOS)}"
        )
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT cliente_id FROM clientes WHERE cliente_id = %s", (cliente_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        cursor.execute("SELECT numero_documento FROM documentos WHERE numero_documento = %s", (numero_documento,))
        if cursor.fetchone() is not None:
            raise HTTPException(status_code=400, detail="Número do documento já existe")
        
        file_content = None
        if arquivo and arquivo.filename:
            file_content = arquivo.file.read()
            if not file_content:
                raise HTTPException(status_code=400, detail="Arquivo não pode estar vazio")

        cursor.execute(
            "INSERT INTO documentos (cliente_id, tipo_documento, numero_documento, arquivo) VALUES (%s, %s, %s, %s) RETURNING documento_id",
            (cliente_id, tipo_documento, numero_documento, file_content)
        )
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Falha ao criar documento")
        documento_id = result['documento_id']
        conn.commit()
        
        return DocumentoResponse(
            documento_id=documento_id,
            cliente_id=cliente_id,
            tipo_documento=tipo_documento,
            numero_documento=numero_documento
        )
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Número do documento já existe")
        elif "foreign key constraint" in str(e).lower():
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        else:
            raise HTTPException(status_code=400, detail="Erro de integridade dos dados")
    finally:
        cursor.close()
        conn.close()

@router.get("/listar", response_model=List[DocumentoResponse])
def listar_documentos(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT documento_id, cliente_id, tipo_documento, numero_documento FROM documentos ORDER BY documento_id DESC LIMIT %s OFFSET %s", (limite, pular))
        documentos = cursor.fetchall()
        return [DocumentoResponse(**documento) for documento in documentos]
    finally:
        cursor.close()
        conn.close()

@router.get("/obter/{documento_id}", response_model=DocumentoResponse)
def obter_documento(documento_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT documento_id, cliente_id, tipo_documento, numero_documento FROM documentos WHERE documento_id = %s", (documento_id,))
        documento = cursor.fetchone()
        
        if documento is None:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        return DocumentoResponse(**documento)
    finally:
        cursor.close()
        conn.close()

@router.get("/obter/{documento_id}/download")
def download_documento(documento_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT tipo_documento, numero_documento, arquivo FROM documentos WHERE documento_id = %s", (documento_id,))
        documento = cursor.fetchone()
        
        if documento is None:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        if documento['arquivo'] is None:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        filename = f"{documento['tipo_documento']}_{documento['numero_documento']}.bin"
        file_content = bytes(documento['arquivo'])
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{documento_id}")
def remover_documento(documento_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM documentos WHERE documento_id = %s", (documento_id,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        return {"mensagem": "Documento removido com sucesso"}
    finally:
        cursor.close()
        conn.close()

@router.get("/cliente/{cliente_id}", response_model=List[DocumentoResponse])
def obter_documentos_por_cliente(cliente_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute("SELECT documento_id, cliente_id, tipo_documento, numero_documento FROM documentos WHERE cliente_id = %s ORDER BY documento_id DESC", (cliente_id,))
        documentos = cursor.fetchall()
        return [DocumentoResponse(**documento) for documento in documentos]
    finally:
        cursor.close()
        conn.close()
