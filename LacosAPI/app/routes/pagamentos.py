from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.pagamento import Pagamento
from app.schemas.penalizacao import Penalizacao
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
from app.utils.notifications import notificar_pagamento_confirmado, notificar_atraso_pagamento, notificar_admin_pagamento
import psycopg2.extras
from datetime import datetime, date, timezone
from decimal import Decimal

router = APIRouter()

@router.post("/criar", response_model=Pagamento)
def criar_pagamento(pagamento: Pagamento, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Verificar se o empréstimo existe e se pertence ao cliente especificado
        cursor.execute("SELECT cliente_id, data_vencimento, valor FROM emprestimos WHERE emprestimo_id = %s", (pagamento.emprestimo_id,))
        emprestimo_result = cursor.fetchone()
        if emprestimo_result is None:
            raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
        
        # Verificar se o cliente_id do pagamento corresponde ao cliente_id do empréstimo
        if emprestimo_result['cliente_id'] != pagamento.cliente_id:
            raise HTTPException(status_code=400, detail="Cliente não corresponde ao empréstimo especificado")
        
        # Inserir pagamento
        cursor.execute(
            "INSERT INTO pagamentos (emprestimo_id, cliente_id, valor_pago, data_pagamento, metodo_pagamento, referencia_pagamento) VALUES (%s, %s, %s, %s, %s, %s) RETURNING pagamento_id",
            (pagamento.emprestimo_id, pagamento.cliente_id, pagamento.valor_pago, pagamento.data_pagamento, pagamento.metodo_pagamento, pagamento.referencia_pagamento)
        )
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Falha ao criar pagamento")
        pagamento_id = result['pagamento_id']
        conn.commit()
        
        # Verificar penalizações pendentes (usar alias e acesso por chave em RealDictRow)
        cursor.execute(
            "SELECT COUNT(*) AS total FROM penalizacoes WHERE cliente_id = %s AND status != 'aplicada'",
            (pagamento.cliente_id,)
        )
        result = cursor.fetchone()
        count_penalizacoes_pendentes = int(result['total']) if result and 'total' in result else 0
        
        # Verificar se há atraso e calcular dias de atraso com base na data do pagamento
        data_pagamento = pagamento.data_pagamento.date() if hasattr(pagamento.data_pagamento, 'date') else pagamento.data_pagamento
        data_vencimento = emprestimo_result['data_vencimento'].date() if hasattr(emprestimo_result['data_vencimento'], 'date') else emprestimo_result['data_vencimento']
        dias_atraso = (data_pagamento - data_vencimento).days if data_pagamento > data_vencimento else 0
        
        # Calcular total já pago (usar alias e acesso por chave)
        cursor.execute(
            "SELECT COALESCE(SUM(valor_pago), 0) AS total_pago FROM pagamentos WHERE emprestimo_id = %s",
            (pagamento.emprestimo_id,)
        )
        result = cursor.fetchone()
        total_pago = float(result['total_pago']) if result and 'total_pago' in result else 0.0

        # Valor total devido inclui 20% do valor do empréstimo (parte do banco)
        valor_total_devido = float(emprestimo_result['valor']) * 1.20

        # Valor em aberto após este pagamento
        valor_em_aberto = max(valor_total_devido - (float(total_pago) + float(pagamento.valor_pago)), 0.0)
        
        # Gerar notificações automáticas
        try:
            # Obter dados do cliente para notificação admin
            cursor.execute("SELECT nome, telefone FROM clientes WHERE cliente_id = %s", (pagamento.cliente_id,))
            cliente = cursor.fetchone()
            if cliente:
                cliente_nome = cliente['nome']
                cliente_telefone = cliente['telefone']
                # Gerar notificação administrativa
                notificar_admin_pagamento(cliente_nome, cliente_telefone, float(pagamento.valor_pago), pagamento.metodo_pagamento, pagamento_id, pagamento.emprestimo_id)

            if dias_atraso > 0:
                # Notificação de atraso se pagamento foi feito após vencimento para cliente e admin
                notificar_atraso_pagamento(pagamento.cliente_id, valor_em_aberto, dias_atraso, cliente_nome, cliente_telefone)

            # Sempre gerar notificação de confirmação de pagamento para cliente e admin
            notificar_pagamento_confirmado(pagamento.cliente_id, float(pagamento.valor_pago), pagamento.metodo_pagamento, cliente_nome, cliente_telefone)
        except Exception as e:
            print(f"Aviso: Falha ao criar notificações de pagamento: {e}")
            # Não falhar o pagamento por causa das notificações

        # Penalização é calculada apenas a nível de lógica de backend (sem persistência em tabela)
        # A notificação de atraso já é emitida acima quando aplicável.

        # Verificar se o pagamento cobre o valor do empréstimo + 20% de lucro
        if float(pagamento.valor_pago) < valor_total_devido:
            print(f"[ALERTA] Pagamento insuficiente para cobrir o empréstimo + 20% de lucro. Valor pago: {pagamento.valor_pago}, Valor devido: {valor_total_devido}")

        # Atualizar status do empréstimo para "Pago" se o valor pago cobrir o valor devido (principal + 20%)
        if float(total_pago) + float(pagamento.valor_pago) >= float(valor_total_devido):
            cursor.execute("UPDATE emprestimos SET status = 'Pago' WHERE emprestimo_id = %s", (pagamento.emprestimo_id,))
            conn.commit()

        return Pagamento(
            pagamento_id=pagamento_id,
            emprestimo_id=pagamento.emprestimo_id,
            cliente_id=pagamento.cliente_id,
            valor_pago=pagamento.valor_pago,
            data_pagamento=pagamento.data_pagamento,
            metodo_pagamento=pagamento.metodo_pagamento,
            referencia_pagamento=pagamento.referencia_pagamento
        )
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="emprestimo_id ou cliente_id inválido")
        else:
            raise HTTPException(status_code=400, detail="Erro de integridade de dados")
    except Exception as e:
        conn.rollback()
        print(f"DEBUG: Payment creation failed with error: {str(e)}")
        print(f"DEBUG: Error type: {type(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/listar", response_model=List[Pagamento])
def listar_pagamentos(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM pagamentos LIMIT %s OFFSET %s", (limite, pular))
        pagamentos = cursor.fetchall()
        return [Pagamento(**pagamento) for pagamento in pagamentos]
    finally:
        cursor.close()
        conn.close()

@router.get("/obter/{pagamento_id}", response_model=Pagamento)
def obter_pagamento(pagamento_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM pagamentos WHERE pagamento_id = %s", (pagamento_id,))
        pagamento = cursor.fetchone()
        
        if pagamento is None:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")
        
        return Pagamento(**pagamento)
    finally:
        cursor.close()
        conn.close()

@router.put("/atualizar/{pagamento_id}", response_model=Pagamento)
def atualizar_pagamento(pagamento_id: int, pagamento: Pagamento, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "UPDATE pagamentos SET emprestimo_id = %s, cliente_id = %s, valor_pago = %s, data_pagamento = %s, metodo_pagamento = %s, referencia_pagamento = %s WHERE pagamento_id = %s RETURNING *",
            (pagamento.emprestimo_id, pagamento.cliente_id, pagamento.valor_pago, pagamento.data_pagamento, pagamento.metodo_pagamento, pagamento.referencia_pagamento, pagamento_id)
        )
        pagamento_atualizado = cursor.fetchone()
        conn.commit()
        
        if pagamento_atualizado is None:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")
        
        return Pagamento(**pagamento_atualizado)
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{pagamento_id}")
def remover_pagamento(pagamento_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM pagamentos WHERE pagamento_id = %s", (pagamento_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")
        
        return {"mensagem": "Pagamento removido com sucesso"}
    finally:
        cursor.close()
        conn.close()

@router.get("/emprestimo/{emprestimo_id}", response_model=List[Pagamento])
def obter_pagamentos_por_emprestimo(emprestimo_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM pagamentos WHERE emprestimo_id = %s", (emprestimo_id,))
        pagamentos = cursor.fetchall()
        return [Pagamento(**pagamento) for pagamento in pagamentos]
    finally:
        cursor.close()
        conn.close()

@router.get("/cliente/{cliente_id}", response_model=List[Pagamento])
def obter_pagamentos_por_cliente(cliente_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM pagamentos WHERE cliente_id = %s", (cliente_id,))
        pagamentos = cursor.fetchall()
        return [Pagamento(**pagamento) for pagamento in pagamentos]
    finally:
        cursor.close()
        conn.close()
