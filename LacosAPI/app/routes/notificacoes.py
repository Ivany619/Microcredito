from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.notificacao import Notificacao, NotificacaoCriar, NotificacaoAtualizar
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
import psycopg2.extras
from datetime import datetime, timedelta, timezone
from decimal import Decimal

router = APIRouter()

@router.post("/criar", response_model=Notificacao)
def criar_notificacao(notificacao: NotificacaoCriar, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "INSERT INTO notificacoes (cliente_id, tipo, mensagem, status) VALUES (%s, %s, %s, %s) RETURNING *",
            (notificacao.cliente_id, notificacao.tipo, notificacao.mensagem, notificacao.status)
        )
        resultado = cursor.fetchone()
        if resultado is None:
            raise HTTPException(status_code=500, detail="Falha ao criar notificação")
        conn.commit()
        
        return Notificacao(**resultado)
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="cliente_id inválido")
        raise HTTPException(status_code=400, detail="Erro de integridade de dados")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/listar", response_model=List[Notificacao])
def listar_notificacoes(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM notificacoes ORDER BY data_envio DESC LIMIT %s OFFSET %s", (limite, pular))
        notificacoes = cursor.fetchall()
        return [Notificacao(**notificacao) for notificacao in notificacoes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar notificações: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/cliente/{cliente_id}", response_model=List[Notificacao])
def listar_notificacoes_por_cliente(cliente_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM notificacoes WHERE cliente_id = %s ORDER BY data_envio DESC", (cliente_id,))
        notificacoes = cursor.fetchall()
        return [Notificacao(**notificacao) for notificacao in notificacoes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar notificações: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.put("/atualizar/{notificacao_id}", response_model=Notificacao)
def atualizar_notificacao(notificacao_id: int, notificacao: NotificacaoAtualizar, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "UPDATE notificacoes SET status = %s WHERE notificacao_id = %s RETURNING *",
            (notificacao.status, notificacao_id)
        )
        notificacao_atualizada = cursor.fetchone()
        conn.commit()
        
        if notificacao_atualizada is None:
            raise HTTPException(status_code=404, detail="Notificação não encontrada")
        
        return Notificacao(**notificacao_atualizada)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar notificação: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{notificacao_id}")
def remover_notificacao(notificacao_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM notificacoes WHERE notificacao_id = %s", (notificacao_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Notificação não encontrada")
        
        return {"mensagem": "Notificação removida com sucesso"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao remover notificação: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/verificar-pagamentos")
def verificar_e_criar_notificacoes(funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT e.emprestimo_id, e.cliente_id, e.valor, e.data_vencimento,
                   COALESCE(SUM(p.valor_pago), 0) as total_pago,
                   c.nome as nome_cliente
            FROM emprestimos e
            JOIN clientes c ON e.cliente_id = c.cliente_id
            LEFT JOIN pagamentos p ON e.emprestimo_id = p.emprestimo_id
            WHERE e.status = 'Ativo'
            GROUP BY e.emprestimo_id, e.cliente_id, e.valor, e.data_vencimento, c.nome
        """)
        
        emprestimos = cursor.fetchall()
        notificacoes_criadas = []
        
        for emprestimo in emprestimos:
            emprestimo_id = emprestimo['emprestimo_id']
            cliente_id = emprestimo['cliente_id']
            valor_emprestimo = emprestimo['valor']
            total_pago = emprestimo['total_pago']
            data_vencimento = emprestimo['data_vencimento']
            nome_cliente = emprestimo['nome_cliente']
            
            dias_ate_vencimento = (data_vencimento - datetime.now(timezone.utc)).days
            
            cursor.execute("""
                SELECT COUNT(*) as count FROM notificacoes 
                WHERE cliente_id = %s 
                AND tipo IN ('Lembrete de Pagamento', 'Atraso no Pagamento')
                AND DATE(data_envio) = CURRENT_DATE
            """, (cliente_id,))
            
            notificacao_hoje = cursor.fetchone()['count']
            
            if notificacao_hoje == 0:
                if dias_ate_vencimento < 0:
                    tipo = "Atraso no Pagamento"
                    mensagem = f"O empréstimo de {valor_emprestimo} está vencido há {abs(dias_ate_vencimento)} dias. Valor em aberto: {valor_emprestimo - total_pago}"
                elif dias_ate_vencimento <= 5:
                    tipo = "Lembrete de Pagamento"
                    mensagem = f"Lembrete: O empréstimo de {valor_emprestimo} vence em {dias_ate_vencimento} dias. Valor em aberto: {valor_emprestimo - total_pago}"
                elif dias_ate_vencimento <= 10:
                    tipo = "Lembrete de Pagamento"
                    mensagem = f"Lembrete: O empréstimo de {valor_emprestimo} vence em {dias_ate_vencimento} dias. Valor em aberto: {valor_emprestimo - total_pago}"
                else:
                    continue
                
                cursor.execute("""
                    INSERT INTO notificacoes (cliente_id, tipo, mensagem, status)
                    VALUES (%s, %s, %s, %s) RETURNING notificacao_id
                """, (cliente_id, tipo, mensagem, "Pendente"))
                
                resultado = cursor.fetchone()
                notificacoes_criadas.append({
                    'notificacao_id': resultado['notificacao_id'],
                    'cliente_id': cliente_id,
                    'tipo': tipo,
                    'mensagem': mensagem
                })
        
        conn.commit()

        return {
            "mensagem": f"{len(notificacoes_criadas)} notificações criadas automaticamente",
            "notificacoes": notificacoes_criadas
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar notificações: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/pendentes", response_model=List[Notificacao])
def listar_notificacoes_pendentes(funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM notificacoes WHERE status = 'Pendente' ORDER BY data_envio DESC")
        notificacoes = cursor.fetchall()
        return [Notificacao(**notificacao) for notificacao in notificacoes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar notificações: {str(e)}")
    finally:
        cursor.close()
        conn.close()
