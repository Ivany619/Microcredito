from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.penalizacao import Penalizacao, PenalizacaoDetalhe
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
from app.utils.notifications import notificar_penalizacao_aplicada, notificar_admin_penalizacao
import psycopg2.extras
from datetime import datetime, timezone
from decimal import Decimal

router = APIRouter()

@router.post("/criar", response_model=PenalizacaoDetalhe)
def criar_penalizacao(emprestimo_id: int, data_referencia: datetime, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT * FROM emprestimos
            WHERE emprestimo_id = %s
            AND status = 'Ativo'
        """, (emprestimo_id,))
        emprestimo = cursor.fetchone()
        
        if emprestimo is None:
            raise HTTPException(status_code=404, detail="Empréstimo não encontrado ou já está pago/inadimplente")
        
        # Ensure both datetimes have the same timezone awareness
        if emprestimo['data_vencimento'].tzinfo is None:
            # If database datetime is naive, make data_referencia naive too
            data_ref_naive = data_referencia.replace(tzinfo=None)
            dias_atraso = (data_ref_naive - emprestimo['data_vencimento']).days if data_ref_naive > emprestimo['data_vencimento'] else 0
        else:
            # If database datetime is aware, make data_referencia aware too
            if data_referencia.tzinfo is None:
                data_ref_aware = data_referencia.replace(tzinfo=emprestimo['data_vencimento'].tzinfo)
            else:
                data_ref_aware = data_referencia
            dias_atraso = (data_ref_aware - emprestimo['data_vencimento']).days if data_ref_aware > emprestimo['data_vencimento'] else 0
        penalizacao_dias_atraso = emprestimo['valor'] * Decimal('0.05') * dias_atraso
        if dias_atraso <= 0:
            raise HTTPException(status_code=400, detail="Sem atraso, não é aplicada penalização")
        total_penalizacao = penalizacao_dias_atraso

        # Dados adicionais para resposta detalhada
        cursor.execute("SELECT nome FROM clientes WHERE cliente_id = %s", (emprestimo['cliente_id'],))
        cli = cursor.fetchone()
        nome_cliente = cli['nome'] if cli and 'nome' in cli else None
        valor_emprestimo = emprestimo['valor']
        
        penalizacao = Penalizacao(
            emprestimo_id=emprestimo_id,
            cliente_id=emprestimo['cliente_id'],
            tipo='Mora',  # Usar tipo definido no schema
            dias_atraso=dias_atraso,
            valor=total_penalizacao,
            status='aplicada',
            data_aplicacao=data_referencia
        )
        
        cursor.execute(
            "INSERT INTO penalizacoes (emprestimo_id, cliente_id, tipo, dias_atraso, valor, status, data_aplicacao) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING penalizacao_id",
            (penalizacao.emprestimo_id, penalizacao.cliente_id, penalizacao.tipo, penalizacao.dias_atraso, penalizacao.valor, penalizacao.status, penalizacao.data_aplicacao)
        )
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Falha ao criar penalização")
        penalizacao_id = result['penalizacao_id']
        conn.commit()

        # Gerar notificação automática de penalização aplicada para cliente e admin
        cursor.execute("SELECT nome, telefone FROM clientes WHERE cliente_id = %s", (penalizacao.cliente_id,))
        cliente = cursor.fetchone()
        if cliente:
            notificar_penalizacao_aplicada(penalizacao.cliente_id, float(penalizacao.valor), cliente['nome'], cliente['telefone'], penalizacao.dias_atraso)

        return PenalizacaoDetalhe(
            penalizacao_id=penalizacao_id,
            emprestimo_id=penalizacao.emprestimo_id,
            cliente_id=penalizacao.cliente_id,
            tipo=penalizacao.tipo,
            dias_atraso=penalizacao.dias_atraso,
            valor=penalizacao.valor,
            status=penalizacao.status,
            data_aplicacao=penalizacao.data_aplicacao,
            nome_cliente=nome_cliente,
            data_emprestimo=emprestimo['data_emprestimo'],
            valor_emprestimo=valor_emprestimo,
            percentagem_aplicada=Decimal(dias_atraso) * Decimal(5),
            total_penalizacoes=penalizacao.valor,
            total_com_lucro=(Decimal(valor_emprestimo) * Decimal('1.20')) + Decimal(penalizacao.valor)
        )
    finally:
        cursor.close()
        conn.close()

@router.get("/listar", response_model=List[PenalizacaoDetalhe])
def listar_penalizacoes(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT p.*, c.nome AS nome_cliente, e.data_emprestimo, e.valor AS valor_emprestimo
            FROM penalizacoes p
            JOIN clientes c ON p.cliente_id = c.cliente_id
            JOIN emprestimos e ON p.emprestimo_id = e.emprestimo_id
            ORDER BY p.data_aplicacao DESC
            LIMIT %s OFFSET %s
        """, (limite, pular))
        rows = cursor.fetchall()
        itens = []
        for r in rows:
            percent = (r['dias_atraso'] or 0) * 5
            total_com_lucro = Decimal(r['valor_emprestimo']) * Decimal('1.20') + Decimal(r['valor'])
            itens.append(PenalizacaoDetalhe(
                penalizacao_id=r['penalizacao_id'],
                emprestimo_id=r['emprestimo_id'],
                cliente_id=r['cliente_id'],
                tipo=r['tipo'] if r['tipo'] in ['Juro', 'Mora', 'Outro'] else 'Mora',
                dias_atraso=r['dias_atraso'],
                valor=r['valor'],
                status=r['status'],
                data_aplicacao=r['data_aplicacao'],
                nome_cliente=r['nome_cliente'],
                data_emprestimo=r['data_emprestimo'],
                valor_emprestimo=r['valor_emprestimo'],
                percentagem_aplicada=Decimal(percent),
                total_penalizacoes=r['valor'],
                total_com_lucro=total_com_lucro
            ))
        return itens
    finally:
        cursor.close()
        conn.close()

@router.get("/obter/{penalizacao_id}", response_model=PenalizacaoDetalhe)
def obter_penalizacao(penalizacao_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT p.*, c.nome AS nome_cliente, e.data_emprestimo, e.valor AS valor_emprestimo
            FROM penalizacoes p
            JOIN clientes c ON p.cliente_id = c.cliente_id
            JOIN emprestimos e ON p.emprestimo_id = e.emprestimo_id
            WHERE p.penalizacao_id = %s
        """, (penalizacao_id,))
        r = cursor.fetchone()
        
        if r is None:
            raise HTTPException(status_code=404, detail="Penalização não encontrada")
        
        percent = (r['dias_atraso'] or 0) * 5
        total_com_lucro = Decimal(r['valor_emprestimo']) * Decimal('1.20') + Decimal(r['valor'])
        return PenalizacaoDetalhe(
            penalizacao_id=r['penalizacao_id'],
            emprestimo_id=r['emprestimo_id'],
            cliente_id=r['cliente_id'],
            tipo=r['tipo'] if r['tipo'] in ['Juro', 'Mora', 'Outro'] else 'Mora',
            dias_atraso=r['dias_atraso'],
            valor=r['valor'],
            status=r['status'],
            data_aplicacao=r['data_aplicacao'],
            nome_cliente=r['nome_cliente'],
            data_emprestimo=r['data_emprestimo'],
            valor_emprestimo=r['valor_emprestimo'],
            percentagem_aplicada=Decimal(percent),
            total_penalizacoes=r['valor'],
            total_com_lucro=total_com_lucro
        )
    finally:
        cursor.close()
        conn.close()

@router.get("/resumo", response_model=dict)
def resumo_penalizacoes(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    """
    Exibe dados reais das penalizações persistidas, juntando com clientes e empréstimos:
    - total de dias de atraso
    - data do empréstimo
    - percentagem aplicada (dias_atraso × 5)
    - valor do empréstimo
    - total das penalizações (valor_emprestimo × 0.05 × dias_atraso)
    - total final = total penalizações + (valor_emprestimo × 1.20)
    Além disso, devolve uma mensagem similar ao fluxo de aplicação automática.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("""
            SELECT p.*, c.nome AS nome_cliente, e.data_emprestimo, e.valor AS valor_emprestimo
            FROM penalizacoes p
            JOIN clientes c ON p.cliente_id = c.cliente_id
            JOIN emprestimos e ON p.emprestimo_id = e.emprestimo_id
            WHERE p.status = 'aplicada'
            ORDER BY p.data_aplicacao DESC
            LIMIT %s OFFSET %s
        """, (limite, pular))
        rows = cursor.fetchall()
        detalhes = []
        for r in rows:
            percent = (r['dias_atraso'] or 0) * 5
            total_com_lucro = Decimal(r['valor_emprestimo']) * Decimal('1.20') + Decimal(r['valor'])
            detalhes.append({
                "penalizacao_id": r['penalizacao_id'],
                "emprestimo_id": r['emprestimo_id'],
                "cliente_id": r['cliente_id'],
                "nome_cliente": r['nome_cliente'],
                "data_emprestimo": r['data_emprestimo'].isoformat() if hasattr(r['data_emprestimo'], 'isoformat') else str(r['data_emprestimo']),
                "valor_emprestimo": str(r['valor_emprestimo']),
                "dias_atraso": r['dias_atraso'],
                "percentagem_aplicada": str(Decimal(percent)),
                "total_penalizacoes": str(r['valor']),
                "total_com_lucro": str(total_com_lucro),
                "tipo": r['tipo'] if r['tipo'] in ['Juro', 'Mora', 'Outro'] else 'Mora',
                "status": r['status'],
                "data_aplicacao": r['data_aplicacao'].isoformat() if hasattr(r['data_aplicacao'], 'isoformat') else str(r['data_aplicacao']),
            })
        return {
            "mensagem": "Penalizações aplicadas com sucesso",
            "detalhes": detalhes
        }
    finally:
        cursor.close()
        conn.close()

 
@router.post("/aplicar-automatico", response_model=dict)
def aplicar_penalizacoes_automaticas(funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT e.*, c.nome AS nome_cliente, c.telefone
            FROM emprestimos e
            JOIN clientes c ON e.cliente_id = c.cliente_id
            LEFT JOIN penalizacoes p ON e.emprestimo_id = p.emprestimo_id AND p.status = 'aplicada'
            WHERE e.status = 'Ativo'
            AND p.penalizacao_id IS NULL
        """)
        emprestimos_atrasados = cursor.fetchall()
        detalhes = []
        
        for emprestimo in emprestimos_atrasados:
            # Ensure both operands are the same type for subtraction
            current_date = datetime.now(timezone.utc).date()
            vencimento_date = emprestimo['data_vencimento'].date() if hasattr(emprestimo['data_vencimento'], 'date') else emprestimo['data_vencimento']
            dias_atraso = (current_date - vencimento_date).days if current_date > vencimento_date else 0
            if dias_atraso <= 0:
                continue

            penalizacao_dias_atraso = emprestimo['valor'] * Decimal('0.05') * dias_atraso
            
            cursor.execute(
                "INSERT INTO penalizacoes (emprestimo_id, cliente_id, tipo, dias_atraso, valor, status, data_aplicacao) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING penalizacao_id",
                (emprestimo['emprestimo_id'], emprestimo['cliente_id'], 'Mora', dias_atraso, penalizacao_dias_atraso, 'aplicada', datetime.now(timezone.utc))
            )
            penalizacao_result = cursor.fetchone()
            penalizacao_id = penalizacao_result['penalizacao_id'] if penalizacao_result else None
            try:
                notificar_penalizacao_aplicada(emprestimo['cliente_id'], float(penalizacao_dias_atraso), emprestimo['nome_cliente'], emprestimo['telefone'], dias_atraso)
            except Exception:
                pass
            detalhes.append({
                "emprestimo_id": emprestimo['emprestimo_id'],
                "cliente_id": emprestimo['cliente_id'],
                "nome_cliente": emprestimo.get('nome_cliente'),
                "data_emprestimo": emprestimo['data_emprestimo'].isoformat() if hasattr(emprestimo['data_emprestimo'], 'isoformat') else str(emprestimo['data_emprestimo']),
                "valor_emprestimo": str(emprestimo['valor']),
                "dias_atraso": dias_atraso,
                "percentagem_aplicada": str(Decimal(dias_atraso) * Decimal(5)),
                "total_penalizacoes": str(penalizacao_dias_atraso),
                "total_com_lucro": str((Decimal(emprestimo['valor']) * Decimal('1.20')) + penalizacao_dias_atraso)
            })
        
        conn.commit()

        return {"mensagem": "Penalizações aplicadas com sucesso", "detalhes": detalhes}
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{penalizacao_id}")
def remover_penalizacao(penalizacao_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM penalizacoes WHERE penalizacao_id = %s", (penalizacao_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Penalização não encontrada")
        
        return {"mensagem": "Penalização removida com sucesso"}
    finally:
        cursor.close()
        conn.close()
