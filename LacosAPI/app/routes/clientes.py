from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.cliente import Cliente
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
import psycopg2.extras
from datetime import date

router = APIRouter()

@router.post("/criar", response_model=Cliente)
def criar_cliente(cliente: Cliente, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "INSERT INTO clientes (nome, sexo, telefone, email, nacionalidade, data_nascimento) VALUES (%s, %s, %s, %s, %s, %s) RETURNING cliente_id",
            (cliente.nome, cliente.sexo, cliente.telefone, cliente.email, cliente.nacionalidade, cliente.data_nascimento)
        )
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Falha ao criar cliente")
        cliente_id = result['cliente_id']
        conn.commit()
        
        return Cliente(
            cliente_id=cliente_id,
            nome=cliente.nome,
            sexo=cliente.sexo,
            telefone=cliente.telefone,
            email=cliente.email,
            nacionalidade=cliente.nacionalidade,
            data_nascimento=cliente.data_nascimento
        )
    finally:
        cursor.close()
        conn.close()

@router.get("/listar", response_model=List[Cliente])
def listar_clientes(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM clientes LIMIT %s OFFSET %s", (limite, pular))
        clientes = cursor.fetchall()
        return [Cliente(**cliente) for cliente in clientes]
    finally:
        cursor.close()
        conn.close()

@router.get("/obter/{cliente_id}", response_model=Cliente)
def obter_cliente(cliente_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM clientes WHERE cliente_id = %s", (cliente_id,))
        cliente = cursor.fetchone()
        
        if cliente is None:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        return Cliente(**cliente)
    finally:
        cursor.close()
        conn.close()

@router.put("/atualizar/{cliente_id}", response_model=Cliente)
def atualizar_cliente(cliente_id: int, cliente: Cliente, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "UPDATE clientes SET nome = %s, sexo = %s, telefone = %s, email = %s, nacionalidade = %s, data_nascimento = %s WHERE cliente_id = %s RETURNING *",
            (cliente.nome, cliente.sexo, cliente.telefone, cliente.email, cliente.nacionalidade, cliente.data_nascimento, cliente_id)
        )
        cliente_atualizado = cursor.fetchone()
        conn.commit()
        
        if cliente_atualizado is None:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        return Cliente(**cliente_atualizado)
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{cliente_id}")
def remover_cliente(cliente_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM clientes WHERE cliente_id = %s", (cliente_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        return {"mensagem": "Cliente removido com sucesso"}
    finally:
        cursor.close()
        conn.close()