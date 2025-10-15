from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.testemunha import Testemunha
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
import psycopg2.extras

router = APIRouter()

@router.post("/criar", response_model=Testemunha)
def criar_testemunha(testemunha: Testemunha, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "INSERT INTO testemunhas (cliente_id, nome, telefone, tipo_relacao) VALUES (%s, %s, %s, %s) RETURNING testemunha_id",
            (testemunha.cliente_id, testemunha.nome, testemunha.telefone, testemunha.tipo_relacao)
        )
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Falha ao criar testemunha")
        testemunha_id = result['testemunha_id']
        conn.commit()
        
        return Testemunha(
            testemunha_id=testemunha_id,
            cliente_id=testemunha.cliente_id,
            nome=testemunha.nome,
            telefone=testemunha.telefone,
            tipo_relacao=testemunha.tipo_relacao
        )
    finally:
        cursor.close()
        conn.close()

@router.get("/listar", response_model=List[Testemunha])
def listar_testemunhas(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM testemunhas LIMIT %s OFFSET %s", (limite, pular))
        testemunhas = cursor.fetchall()
        return [Testemunha(**testemunha) for testemunha in testemunhas]
    finally:
        cursor.close()
        conn.close()

@router.get("/obter/{testemunha_id}", response_model=Testemunha)
def obter_testemunha(testemunha_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM testemunhas WHERE testemunha_id = %s", (testemunha_id,))
        testemunha = cursor.fetchone()
        
        if testemunha is None:
            raise HTTPException(status_code=404, detail="Testemunha não encontrada")
        
        return Testemunha(**testemunha)
    finally:
        cursor.close()
        conn.close()

@router.put("/atualizar/{testemunha_id}", response_model=Testemunha)
def atualizar_testemunha(testemunha_id: int, testemunha: Testemunha, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "UPDATE testemunhas SET cliente_id = %s, nome = %s, telefone = %s, tipo_relacao = %s WHERE testemunha_id = %s RETURNING *",
            (testemunha.cliente_id, testemunha.nome, testemunha.telefone, testemunha.tipo_relacao, testemunha_id)
        )
        testemunha_atualizada = cursor.fetchone()
        conn.commit()
        
        if testemunha_atualizada is None:
            raise HTTPException(status_code=404, detail="Testemunha não encontrada")
        
        return Testemunha(**testemunha_atualizada)
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{testemunha_id}")
def remover_testemunha(testemunha_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM testemunhas WHERE testemunha_id = %s", (testemunha_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Testemunha não encontrada")
        
        return {"mensagem": "Testemunha removida com sucesso"}
    finally:
        cursor.close()
        conn.close()

@router.get("/cliente/{cliente_id}", response_model=List[Testemunha])
def obter_testemunhas_por_cliente(cliente_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM testemunhas WHERE cliente_id = %s", (cliente_id,))
        testemunhas = cursor.fetchall()
        return [Testemunha(**testemunha) for testemunha in testemunhas]
    finally:
        cursor.close()
        conn.close()
