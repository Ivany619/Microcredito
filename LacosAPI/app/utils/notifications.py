from app.database.database import get_db_connection
import psycopg2.extras

def criar_notificacao_automatica(cliente_id: int, tipo: str, mensagem: str):
    """
    Função utilitária para criar notificações automaticamente
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute(
            "INSERT INTO notificacoes (cliente_id, tipo, mensagem, status) VALUES (%s, %s, %s, %s)",
            (cliente_id, tipo, mensagem, "Pendente")
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao criar notificação: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def notificar_confirmacao_emprestimo(cliente_id: int, valor_emprestimo: float, cliente_nome: str = None, cliente_telefone: str = None):
    """
    Notificação de confirmação quando empréstimo é criado - para cliente e admin
    """
    # Notificação para o cliente
    mensagem_cliente = f"Seu empréstimo de {valor_emprestimo:.2f} MZN foi aprovado e está ativo."
    criar_notificacao_automatica(cliente_id, "Confirmação de Empréstimo", mensagem_cliente)

    # Notificação para admin
    if cliente_nome and cliente_telefone:
        mensagem_admin = f"Empréstimo aprovado - Cliente: {cliente_nome}, Telefone: {cliente_telefone}, Valor: {valor_emprestimo:.2f} MZN"
        criar_notificacao_automatica(None, "Confirmação de Empréstimo", mensagem_admin)
    return True

def notificar_admin_emprestimo(cliente_nome: str, cliente_telefone: str, valor_emprestimo: float, emprestimo_id: int):
    """
    Notificação específica para admin quando empréstimo é criado
    """
    mensagem_admin = f"Novo empréstimo criado - Cliente: {cliente_nome}, Telefone: {cliente_telefone}, Valor: {valor_emprestimo:.2f} MZN, ID: {emprestimo_id}"
    criar_notificacao_automatica(None, "Novo Empréstimo", mensagem_admin)
    return True

def notificar_pagamento_confirmado(cliente_id: int, valor_pago: float, metodo: str, cliente_nome: str = None, cliente_telefone: str = None):
    """
    Notificação de confirmação quando pagamento é registrado - para cliente e admin
    """
    # Notificação para o cliente
    mensagem_cliente = f"Recebemos seu pagamento de {valor_pago:.2f} MZN via {metodo}."
    criar_notificacao_automatica(cliente_id, "Confirmação de Pagamento", mensagem_cliente)

    # Notificação para admin
    if cliente_nome and cliente_telefone:
        mensagem_admin = f"Pagamento recebido - Cliente: {cliente_nome}, Telefone: {cliente_telefone}, Valor: {valor_pago:.2f} MZN, Método: {metodo}"
        criar_notificacao_automatica(None, "Confirmação de Pagamento", mensagem_admin)
    return True

def notificar_admin_pagamento(cliente_nome: str, cliente_telefone: str, valor_pago: float, metodo: str, pagamento_id: int, emprestimo_id: int):
    """
    Notificação específica para admin quando pagamento é registrado
    """
    mensagem_admin = f"Novo pagamento registrado - Cliente: {cliente_nome}, Telefone: {cliente_telefone}, Valor: {valor_pago:.2f} MZN, Método: {metodo}, Pagamento ID: {pagamento_id}, Empréstimo ID: {emprestimo_id}"
    criar_notificacao_automatica(None, "Novo Pagamento", mensagem_admin)
    return True

def notificar_penalizacao_aplicada(cliente_id: int, valor_penalizacao: float, cliente_nome: str = None, cliente_telefone: str = None, dias_atraso: int = None):
    """
    Notificação quando penalização é aplicada - para cliente e admin
    """
    # Notificação para o cliente
    mensagem_cliente = f"Foi aplicada uma penalização de {valor_penalizacao:.2f} MZN ao seu empréstimo."
    criar_notificacao_automatica(cliente_id, "Penalização Aplicada", mensagem_cliente)

    # Notificação para admin
    if cliente_nome and cliente_telefone:
        mensagem_admin = f"Penalização aplicada - Cliente: {cliente_nome}, Telefone: {cliente_telefone}, Valor: {valor_penalizacao:.2f} MZN"
        if dias_atraso:
            mensagem_admin += f", Dias de atraso: {dias_atraso}"
        criar_notificacao_automatica(None, "Penalização Aplicada", mensagem_admin)
    return True

def notificar_admin_penalizacao(cliente_nome: str, cliente_telefone: str, valor_penalizacao: float, dias_atraso: int, penalizacao_id: int, emprestimo_id: int):
    """
    Notificação específica para admin quando penalização é aplicada
    """
    mensagem_admin = f"Nova penalização aplicada - Cliente: {cliente_nome}, Telefone: {cliente_telefone}, Valor: {valor_penalizacao:.2f} MZN, Dias de atraso: {dias_atraso}, Penalização ID: {penalizacao_id}, Empréstimo ID: {emprestimo_id}"
    criar_notificacao_automatica(None, "Nova Penalização", mensagem_admin)
    return True

def notificar_lembrete_pagamento(cliente_id: int, valor_devido: float, dias_para_vencimento: int, cliente_nome: str = None, cliente_telefone: str = None):
    """
    Notificação de lembrete de pagamento - para cliente e admin
    """
    # Notificação para o cliente
    mensagem_cliente = f"Lembrete: Você tem {dias_para_vencimento} dias para efetuar o pagamento. Valor devido: {valor_devido:.2f} MZN."
    criar_notificacao_automatica(cliente_id, "Lembrete de Pagamento", mensagem_cliente)

    # Notificação para admin
    if cliente_nome and cliente_telefone:
        mensagem_admin = f"Lembrete de pagamento - Cliente: {cliente_nome}, Telefone: {cliente_telefone}, Dias para vencimento: {dias_para_vencimento}, Valor devido: {valor_devido:.2f} MZN"
        criar_notificacao_automatica(None, "Lembrete de Pagamento", mensagem_admin)
    return True

def notificar_atraso_pagamento(cliente_id: int, valor_em_aberto: float, dias_atraso: int, cliente_nome: str = None, cliente_telefone: str = None):
    """
    Notificação de atraso no pagamento - para cliente e admin
    """
    # Notificação para o cliente
    mensagem_cliente = f"Você está com {dias_atraso} dias de atraso. Valor em aberto: {valor_em_aberto:.2f} MZN."
    criar_notificacao_automatica(cliente_id, "Atraso no Pagamento", mensagem_cliente)

    # Notificação para admin
    if cliente_nome and cliente_telefone:
        mensagem_admin = f"Atraso no pagamento - Cliente: {cliente_nome}, Telefone: {cliente_telefone}, Dias de atraso: {dias_atraso}, Valor em aberto: {valor_em_aberto:.2f} MZN"
        criar_notificacao_automatica(None, "Atraso no Pagamento", mensagem_admin)
    return True
