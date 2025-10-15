from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.emprestimo import Emprestimo
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
from app.utils.notifications import notificar_confirmacao_emprestimo, notificar_admin_emprestimo
import psycopg2.extras
from datetime import datetime

router = APIRouter()

@router.post("/criar", response_model=Emprestimo)
def criar_emprestimo(emprestimo: Emprestimo, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "INSERT INTO emprestimos (cliente_id, valor, data_emprestimo, data_vencimento, status) VALUES (%s, %s, %s, %s, %s) RETURNING emprestimo_id",
            (emprestimo.cliente_id, emprestimo.valor, emprestimo.data_emprestimo, emprestimo.data_vencimento, emprestimo.status)
        )
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Falha ao criar empréstimo")
        emprestimo_id = result['emprestimo_id']

        # Obter dados do cliente para notificação admin
        cursor.execute("SELECT nome, telefone FROM clientes WHERE cliente_id = %s", (emprestimo.cliente_id,))
        cliente = cursor.fetchone()
        if cliente:
            cliente_nome = cliente['nome']
            cliente_telefone = cliente['telefone']
            # Gerar notificação administrativa
            notificar_admin_emprestimo(cliente_nome, cliente_telefone, float(emprestimo.valor), emprestimo_id)

        conn.commit()

        # Gerar notificação automática de confirmação para o cliente e admin
        notificar_confirmacao_emprestimo(emprestimo.cliente_id, float(emprestimo.valor), cliente_nome, cliente_telefone)

        return Emprestimo(
            emprestimo_id=emprestimo_id,
            cliente_id=emprestimo.cliente_id,
            valor=emprestimo.valor,
            data_emprestimo=emprestimo.data_emprestimo,
            data_vencimento=emprestimo.data_vencimento,
            status=emprestimo.status
        )
    finally:
        cursor.close()
        conn.close()

@router.get("/listar", response_model=List[Emprestimo])
def listar_emprestimos(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM emprestimos LIMIT %s OFFSET %s", (limite, pular))
        emprestimos = cursor.fetchall()
        return [Emprestimo(**emprestimo) for emprestimo in emprestimos]
    finally:
        cursor.close()
        conn.close()

@router.get("/obter/{emprestimo_id}", response_model=Emprestimo)
def obter_emprestimo(emprestimo_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM emprestimos WHERE emprestimo_id = %s", (emprestimo_id,))
        emprestimo = cursor.fetchone()
        
        if emprestimo is None:
            raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
        
        return Emprestimo(**emprestimo)
    finally:
        cursor.close()
        conn.close()

@router.put("/atualizar/{emprestimo_id}", response_model=Emprestimo)
def atualizar_emprestimo(emprestimo_id: int, emprestimo: Emprestimo, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "UPDATE emprestimos SET cliente_id = %s, valor = %s, data_emprestimo = %s, data_vencimento = %s, status = %s WHERE emprestimo_id = %s RETURNING *",
            (emprestimo.cliente_id, emprestimo.valor, emprestimo.data_emprestimo, emprestimo.data_vencimento, emprestimo.status, emprestimo_id)
        )
        emprestimo_atualizado = cursor.fetchone()
        conn.commit()
        
        if emprestimo_atualizado is None:
            raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
        
        return Emprestimo(**emprestimo_atualizado)
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{emprestimo_id}")
def remover_emprestimo(emprestimo_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM emprestimos WHERE emprestimo_id = %s", (emprestimo_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
        
        return {"mensagem": "Empréstimo removido com sucesso"}
    finally:
        cursor.close()
        conn.close()

@router.get("/cliente/{cliente_id}", response_model=List[Emprestimo])
def obter_emprestimos_por_cliente(cliente_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM emprestimos WHERE cliente_id = %s", (cliente_id,))
        emprestimos = cursor.fetchall()
        return [Emprestimo(**emprestimo) for emprestimo in emprestimos]
    finally:
        cursor.close()
        conn.close()
