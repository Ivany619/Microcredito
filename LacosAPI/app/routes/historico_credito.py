from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.historico_credito import HistoricoCredito, HistoricoCreditoCriar, HistoricoCreditoAtualizar
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
import psycopg2.extras
from datetime import datetime, timezone

router = APIRouter()

@router.post("/criar", response_model=HistoricoCredito)
def criar_historico_credito(historico: HistoricoCreditoCriar, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            "INSERT INTO Historico_Credito (cliente_id, emprestimo_anterior, status, data_ultimo_pagamento) VALUES (%s, %s, %s, %s) RETURNING *",
            (historico.cliente_id, historico.emprestimo_anterior, historico.status, historico.data_ultimo_pagamento)
        )
        resultado = cursor.fetchone()
        if resultado is None:
            raise HTTPException(status_code=500, detail="Falha ao criar histórico de crédito")
        conn.commit()
        
        return HistoricoCredito(**resultado)
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

@router.get("/listar", response_model=List[HistoricoCredito])
def listar_historico_credito(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM Historico_Credito ORDER BY historico_id DESC LIMIT %s OFFSET %s", (limite, pular))
        historicos = cursor.fetchall()
        return [HistoricoCredito(**historico) for historico in historicos]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar histórico de crédito: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/cliente/{cliente_id}", response_model=List[HistoricoCredito])
def listar_historico_credito_por_cliente(cliente_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM Historico_Credito WHERE cliente_id = %s ORDER BY historico_id DESC", (cliente_id,))
        historicos = cursor.fetchall()
        return [HistoricoCredito(**historico) for historico in historicos]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar histórico de crédito: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.put("/atualizar/{historico_id}", response_model=HistoricoCredito)
def atualizar_historico_credito(historico_id: int, historico: HistoricoCreditoAtualizar, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        campos = []
        valores = []
        
        if historico.emprestimo_anterior is not None:
            campos.append("emprestimo_anterior = %s")
            valores.append(historico.emprestimo_anterior)
        
        if historico.status is not None:
            campos.append("status = %s")
            valores.append(historico.status)
        
        if historico.data_ultimo_pagamento is not None:
            campos.append("data_ultimo_pagamento = %s")
            valores.append(historico.data_ultimo_pagamento)
        
        if not campos:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        valores.append(historico_id)
        
        consulta = f"""
            UPDATE Historico_Credito
            SET {', '.join(campos)}
            WHERE historico_id = %s
            RETURNING *
        """
        
        cursor.execute(consulta, valores)
        historico_atualizado = cursor.fetchone()
        conn.commit()
        
        if historico_atualizado is None:
            raise HTTPException(status_code=404, detail="Histórico de crédito não encontrado")
        
        return HistoricoCredito(**historico_atualizado)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar histórico de crédito: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{historico_id}")
def remover_historico_credito(historico_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM Historico_Credito WHERE historico_id = %s", (historico_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Histórico de crédito não encontrado")
        
        return {"mensagem": "Histórico de crédito removido com sucesso"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao remover histórico de crédito: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/atualizar-automatico")
def atualizar_historico_credito_automatico(funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT DISTINCT c.cliente_id, c.nome
            FROM clientes c
            JOIN emprestimos e ON c.cliente_id = e.cliente_id
        """)
        
        clientes = cursor.fetchall()
        historicos_atualizados = []
        
        for cliente in clientes:
            cliente_id = cliente['cliente_id']
            
            cursor.execute("""
                SELECT e.emprestimo_id, e.valor, e.status, e.data_emprestimo,
                       MAX(p.data_pagamento) as ultima_data_pagamento,
                       COALESCE(SUM(p.valor_pago), 0) as total_pago
                FROM emprestimos e
                LEFT JOIN pagamentos p ON e.emprestimo_id = p.emprestimo_id
                WHERE e.cliente_id = %s
                GROUP BY e.emprestimo_id, e.valor, e.status, e.data_emprestimo
                ORDER BY e.data_emprestimo DESC
                LIMIT 1
            """, (cliente_id,))
            
            emprestimo = cursor.fetchone()
            
            if emprestimo:
                if emprestimo['status'] == 'Pago':
                    status = 'Pago'
                elif emprestimo['status'] == 'Inadimplente':
                    status = 'Inadimplente'
                else:
                    if emprestimo['ultima_data_pagamento']:
                        # Ensure both dates are timezone-aware
                        now = datetime.now(timezone.utc)
                        ultima_data = emprestimo['ultima_data_pagamento']
                        if ultima_data.tzinfo is None:
                            ultima_data = ultima_data.replace(tzinfo=timezone.utc)
                        
                        dias_sem_pagamento = (now - ultima_data).days
                        if dias_sem_pagamento > 30:
                            status = 'Atrasado'
                        else:
                            status = 'Pago'
                    else:
                        status = 'Pago'
                
                cursor.execute("""
                    SELECT historico_id FROM Historico_Credito
                    WHERE cliente_id = %s
                """, (cliente_id,))
                
                historico_existente = cursor.fetchone()
                
                if historico_existente:
                    cursor.execute("""
                        UPDATE Historico_Credito
                        SET emprestimo_anterior = %s, status = %s, data_ultimo_pagamento = %s
                        WHERE cliente_id = %s
                        RETURNING historico_id
                    """, (emprestimo['valor'], status, emprestimo['ultima_data_pagamento'], cliente_id))
                    
                    resultado = cursor.fetchone()
                    historicos_atualizados.append({
                        'historico_id': resultado['historico_id'],
                        'cliente_id': cliente_id,
                        'status': status,
                        'emprestimo_anterior': float(emprestimo['valor'])
                    })
                else:
                    cursor.execute("""
                        INSERT INTO Historico_Credito (cliente_id, emprestimo_anterior, status, data_ultimo_pagamento)
                        VALUES (%s, %s, %s, %s) RETURNING historico_id
                    """, (cliente_id, emprestimo['valor'], status, emprestimo['ultima_data_pagamento']))
                    
                    resultado = cursor.fetchone()
                    historicos_atualizados.append({
                        'historico_id': resultado['historico_id'],
                        'cliente_id': cliente_id,
                        'status': status,
                        'emprestimo_anterior': float(emprestimo['valor'])
                    })
        
        conn.commit()
        
        return {
            "mensagem": f"{len(historicos_atualizados)} históricos de crédito atualizados automaticamente",
            "historicos": historicos_atualizados
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar histórico de crédito: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/analise-credito/{cliente_id}")
def analise_credito_cliente(cliente_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Get client basic info
        cursor.execute("""
            SELECT c.nome, c.telefone, c.email
            FROM clientes c
            WHERE c.cliente_id = %s
        """, (cliente_id,))
        
        cliente = cursor.fetchone()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        # Get client occupation info
        cursor.execute("""
            SELECT o.nome as ocupacao_nome, o.categoria_risco, o.renda_minima,
                   o.setor_economico, o.estabilidade_emprego
            FROM Ocupacoes o
            WHERE o.cliente_id = %s AND o.ativo = TRUE
            ORDER BY o.ocupacao_id DESC
            LIMIT 1
        """, (cliente_id,))
        
        ocupacao = cursor.fetchone()
        
        # Get loans with payments
        cursor.execute("""
            SELECT e.emprestimo_id, e.valor, e.status, e.data_emprestimo, e.data_vencimento,
                   COALESCE(SUM(p.valor_pago), 0) as total_pago,
                   COUNT(p.pagamento_id) as total_pagamentos
            FROM emprestimos e
            LEFT JOIN pagamentos p ON e.emprestimo_id = p.emprestimo_id
            WHERE e.cliente_id = %s
            GROUP BY e.emprestimo_id, e.valor, e.status, e.data_emprestimo, e.data_vencimento
            ORDER BY e.data_emprestimo DESC
        """, (cliente_id,))
        
        emprestimos = cursor.fetchall()
        
        # Get penalties
        cursor.execute("""
            SELECT pen.tipo, pen.valor, pen.data_aplicacao, e.emprestimo_id
            FROM penalizacoes pen
            JOIN emprestimos e ON pen.emprestimo_id = e.emprestimo_id
            WHERE e.cliente_id = %s
            ORDER BY pen.data_aplicacao DESC
        """, (cliente_id,))
        
        penalizacoes = cursor.fetchall()
        
        # Get credit history
        cursor.execute("""
            SELECT * FROM Historico_Credito
            WHERE cliente_id = %s
            ORDER BY historico_id DESC
        """, (cliente_id,))
        
        historico_credito = cursor.fetchall()
        
        # Calculate metrics
        total_emprestimos = len(emprestimos)
        total_valor_emprestado = sum(e['valor'] for e in emprestimos)
        total_pago = sum(e['total_pago'] for e in emprestimos)
        emprestimos_pagos = len([e for e in emprestimos if e['status'] == 'Pago'])
        emprestimos_ativos = len([e for e in emprestimos if e['status'] == 'Ativo'])
        emprestimos_inadimplentes = len([e for e in emprestimos if e['status'] == 'Inadimplente'])
        
        total_penalizacoes = len(penalizacoes)
        valor_total_penalizacoes = sum(p['valor'] for p in penalizacoes)
        
        # Calculate credit score
        score = 100
        
        # Penalties impact
        score -= total_penalizacoes * 5
        score -= min(30, valor_total_penalizacoes / 100)  # Reduce by penalty amount (max 30 points)
        
        # Loan status impact
        score -= emprestimos_inadimplentes * 25
        score += emprestimos_pagos * 15
        
        # Occupation risk impact
        if ocupacao:
            risk_penalties = {
                'Muito Alto': 20,
                'Alto': 15,
                'Médio': 5,
                'Baixo': 0,
                'Muito Baixo': 5  # Bonus for very low risk
            }
            score -= risk_penalties.get(ocupacao['categoria_risco'], 0)
            
            # Employment stability impact
            stability_bonus = {
                'Alta': 10,
                'Média': 5,
                'Baixa': -5,
                'Sazonal': -10
            }
            score += stability_bonus.get(ocupacao['estabilidade_emprego'], 0)
        
        # Note: Salary analysis removed as salary is no longer in personal data
        
        # Payment consistency bonus
        if emprestimos:
            avg_payments_per_loan = sum(e['total_pagamentos'] for e in emprestimos) / len(emprestimos)
            if avg_payments_per_loan > 3:
                score += 10
        
        score = max(0, min(100, score))
        
        # Determine recommendation
        if score >= 80:
            recomendacao = "Aprovado - Excelente"
        elif score >= 70:
            recomendacao = "Aprovado - Bom"
        elif score >= 50:
            recomendacao = "Análise manual necessária"
        elif score >= 30:
            recomendacao = "Reprovado - Alto risco"
        else:
            recomendacao = "Reprovado - Risco muito alto"
        
        return {
            "cliente": {
                "nome": cliente['nome'],
                "telefone": cliente['telefone'],
                "email": cliente['email']
            },
            "ocupacao": dict(ocupacao) if ocupacao else None,
            "emprestimos": {
                "total": total_emprestimos,
                "valor_total_emprestado": float(total_valor_emprestado),
                "valor_total_pago": float(total_pago),
                "emprestimos_pagos": emprestimos_pagos,
                "emprestimos_ativos": emprestimos_ativos,
                "emprestimos_inadimplentes": emprestimos_inadimplentes,
                "detalhes": [dict(e) for e in emprestimos]
            },
            "penalizacoes": {
                "total": total_penalizacoes,
                "valor_total": float(valor_total_penalizacoes),
                "detalhes": [dict(p) for p in penalizacoes]
            },
            "historico_credito": [dict(h) for h in historico_credito],
            "score_credito": score,
            "recomendacao": recomendacao
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar crédito: {str(e)}")
    finally:
        cursor.close()
        conn.close()
