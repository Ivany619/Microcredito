from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.penhor import Penhor
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
import psycopg2.extras

router = APIRouter()

@router.post("/criar", response_model=Penhor)
def criar_penhor(penhor: Penhor, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "INSERT INTO penhor (cliente_id, descricao_item, valor_estimado, data_penhora) VALUES (%s, %s, %s, %s) RETURNING penhor_id",
            (penhor.cliente_id, penhor.descricao_item, penhor.valor_estimado, penhor.data_penhora)
        )
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Falha ao criar penhor")
        penhor_id = result['penhor_id']
        conn.commit()
        
        return Penhor(
            penhor_id=penhor_id,
            cliente_id=penhor.cliente_id,
            descricao_item=penhor.descricao_item,
            valor_estimado=penhor.valor_estimado,
            data_penhora=penhor.data_penhora
        )
    finally:
        cursor.close()
        conn.close()

@router.get("/listar", response_model=List[Penhor])
def listar_penhor(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM penhor LIMIT %s OFFSET %s", (limite, pular))
        penhor_items = cursor.fetchall()
        return [Penhor(**penhor_item) for penhor_item in penhor_items]
    finally:
        cursor.close()
        conn.close()

@router.get("/obter/{penhor_id}", response_model=Penhor)
def obter_penhor(penhor_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM penhor WHERE penhor_id = %s", (penhor_id,))
        penhor_item = cursor.fetchone()
        
        if penhor_item is None:
            raise HTTPException(status_code=404, detail="Penhor não encontrado")
        
        return Penhor(**penhor_item)
    finally:
        cursor.close()
        conn.close()

@router.put("/atualizar/{penhor_id}", response_model=Penhor)
def atualizar_penhor(penhor_id: int, penhor: Penhor, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "UPDATE penhor SET cliente_id = %s, descricao_item = %s, valor_estimado = %s, data_penhora = %s WHERE penhor_id = %s RETURNING *",
            (penhor.cliente_id, penhor.descricao_item, penhor.valor_estimado, penhor.data_penhora, penhor_id)
        )
        penhor_atualizado = cursor.fetchone()
        conn.commit()
        
        if penhor_atualizado is None:
            raise HTTPException(status_code=404, detail="Penhor não encontrado")
        
        return Penhor(**penhor_atualizado)
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{penhor_id}")
def remover_penhor(penhor_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM penhor WHERE penhor_id = %s", (penhor_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Penhor não encontrado")
        
        return {"mensagem": "Penhor removido com sucesso"}
    finally:
        cursor.close()
        conn.close()

@router.get("/cliente/{cliente_id}", response_model=List[Penhor])
def obter_penhor_por_cliente(cliente_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM penhor WHERE cliente_id = %s", (cliente_id,))
        penhor_items = cursor.fetchall()
        return [Penhor(**penhor_item) for penhor_item in penhor_items]
    finally:
        cursor.close()
        conn.close()
