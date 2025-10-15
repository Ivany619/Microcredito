from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.outros_ganhos import OutrosGanhos
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
import psycopg2.extras

router = APIRouter()

@router.post("/criar", response_model=OutrosGanhos)
def criar_outros_ganhos(outros_ganhos: OutrosGanhos, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "INSERT INTO outros_ganhos (cliente_id, descricao, valor) VALUES (%s, %s, %s) RETURNING ganho_id",
            (outros_ganhos.cliente_id, outros_ganhos.descricao, outros_ganhos.valor)
        )
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Falha ao criar outros ganhos")
        ganho_id = result['ganho_id']
        conn.commit()
        
        return OutrosGanhos(
            ganho_id=ganho_id,
            cliente_id=outros_ganhos.cliente_id,
            descricao=outros_ganhos.descricao,
            valor=outros_ganhos.valor
        )
    finally:
        cursor.close()
        conn.close()

@router.get("/listar", response_model=List[OutrosGanhos])
def listar_outros_ganhos(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM outros_ganhos LIMIT %s OFFSET %s", (limite, pular))
        outros_ganhos = cursor.fetchall()
        return [OutrosGanhos(**ganho) for ganho in outros_ganhos]
    finally:
        cursor.close()
        conn.close()

@router.get("/obter/{ganho_id}", response_model=OutrosGanhos)
def obter_outros_ganhos(ganho_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM outros_ganhos WHERE ganho_id = %s", (ganho_id,))
        ganho = cursor.fetchone()
        
        if ganho is None:
            raise HTTPException(status_code=404, detail="Outros ganhos não encontrado")
        
        return OutrosGanhos(**ganho)
    finally:
        cursor.close()
        conn.close()

@router.put("/atualizar/{ganho_id}", response_model=OutrosGanhos)
def atualizar_outros_ganhos(ganho_id: int, outros_ganhos: OutrosGanhos, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "UPDATE outros_ganhos SET cliente_id = %s, descricao = %s, valor = %s WHERE ganho_id = %s RETURNING *",
            (outros_ganhos.cliente_id, outros_ganhos.descricao, outros_ganhos.valor, ganho_id)
        )
        ganho_atualizado = cursor.fetchone()
        conn.commit()
        
        if ganho_atualizado is None:
            raise HTTPException(status_code=404, detail="Outros ganhos não encontrado")
        
        return OutrosGanhos(**ganho_atualizado)
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{ganho_id}")
def remover_outros_ganhos(ganho_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM outros_ganhos WHERE ganho_id = %s", (ganho_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Outros ganhos não encontrado")
        
        return {"mensagem": "Outros ganhos removido com sucesso"}
    finally:
        cursor.close()
        conn.close()

@router.get("/cliente/{cliente_id}", response_model=List[OutrosGanhos])
def obter_outros_ganhos_por_cliente(cliente_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM outros_ganhos WHERE cliente_id = %s", (cliente_id,))
        outros_ganhos = cursor.fetchall()
        return [OutrosGanhos(**ganho) for ganho in outros_ganhos]
    finally:
        cursor.close()
        conn.close()
