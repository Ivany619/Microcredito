from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.localizacao import Localizacao
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
import psycopg2.extras

router = APIRouter()

@router.post("/criar", response_model=Localizacao)
def criar_localizacao(localizacao: Localizacao, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "INSERT INTO localizacao (cliente_id, bairro, numero_da_casa, quarteirao, cidade, distrito, provincia) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING localizacao_id",
            (localizacao.cliente_id, localizacao.bairro, localizacao.numero_da_casa, localizacao.quarteirao, localizacao.cidade, localizacao.distrito, localizacao.provincia)
        )
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Falha ao criar localização")
        localizacao_id = result['localizacao_id']
        conn.commit()
        
        return Localizacao(
            localizacao_id=localizacao_id,
            cliente_id=localizacao.cliente_id,
            bairro=localizacao.bairro,
            numero_da_casa=localizacao.numero_da_casa,
            quarteirao=localizacao.quarteirao,
            cidade=localizacao.cidade,
            distrito=localizacao.distrito,
            provincia=localizacao.provincia
        )
    finally:
        cursor.close()
        conn.close()

@router.get("/listar", response_model=List[Localizacao])
def listar_localizacoes(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM localizacao LIMIT %s OFFSET %s", (limite, pular))
        localizacoes = cursor.fetchall()
        return [Localizacao(**localizacao) for localizacao in localizacoes]
    finally:
        cursor.close()
        conn.close()

@router.get("/obter/{localizacao_id}", response_model=Localizacao)
def obter_localizacao(localizacao_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM localizacao WHERE localizacao_id = %s", (localizacao_id,))
        localizacao = cursor.fetchone()
        
        if localizacao is None:
            raise HTTPException(status_code=404, detail="Localização não encontrada")
        
        return Localizacao(**localizacao)
    finally:
        cursor.close()
        conn.close()

@router.put("/atualizar/{localizacao_id}", response_model=Localizacao)
def atualizar_localizacao(localizacao_id: int, localizacao: Localizacao, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "UPDATE localizacao SET cliente_id = %s, bairro = %s, numero_da_casa = %s, quarteirao = %s, cidade = %s, distrito = %s, provincia = %s WHERE localizacao_id = %s RETURNING *",
            (localizacao.cliente_id, localizacao.bairro, localizacao.numero_da_casa, localizacao.quarteirao, localizacao.cidade, localizacao.distrito, localizacao.provincia, localizacao_id)
        )
        localizacao_atualizada = cursor.fetchone()
        conn.commit()
        
        if localizacao_atualizada is None:
            raise HTTPException(status_code=404, detail="Localização não encontrada")
        
        return Localizacao(**localizacao_atualizada)
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{localizacao_id}")
def remover_localizacao(localizacao_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM localizacao WHERE localizacao_id = %s", (localizacao_id,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Localização não encontrada")

        return {"mensagem": "Localização removida com sucesso"}
    finally:
        cursor.close()
        conn.close()

@router.get("/cliente/{cliente_id}", response_model=List[Localizacao])
def obter_localizacoes_por_cliente(cliente_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute("SELECT * FROM localizacao WHERE cliente_id = %s", (cliente_id,))
        localizacoes = cursor.fetchall()
        return [Localizacao(**localizacao) for localizacao in localizacoes]
    finally:
        cursor.close()
        conn.close()