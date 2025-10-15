import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def get_auth_token():
    """Obtém token de autenticação para os testes"""
    login_data = {
        "username": "natalia.massinga",
        "password": "Ractis@23"
    }
    response = requests.post(f"{BASE_URL}/api/auth/token", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"[ERRO] Falha na autenticação: {response.status_code}")
        return None

def create_test_client(access_token):
    """Cria um cliente de teste para os testes isolados"""
    headers = {"Authorization": f"Bearer {access_token}"}
    client_data = {
        "nome": "Cliente Teste Isolado",
        "sexo": "Masculino",
        "telefone": f"987654321{int(time.time())}",
        "email": f"cliente.isolado{int(time.time())}@example.com",
        "nacionalidade": "Moçambicana",
        "data_nascimento": "1990-01-01"
    }
    response = requests.post(f"{BASE_URL}/api/clientes/criar", json=client_data, headers=headers)
    if response.status_code == 200:
        return response.json()["cliente_id"]
    return None

def create_test_loan(access_token, client_id):
    """Cria um empréstimo de teste"""
    headers = {"Authorization": f"Bearer {access_token}"}
    from datetime import datetime, timedelta
    data_vencimento = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S")

    loan_data = {
        "cliente_id": client_id,
        "valor": 5000.00,
        "data_emprestimo": "2024-01-01T00:00:00",
        "data_vencimento": data_vencimento,
        "status": "Ativo"
    }
    response = requests.post(f"{BASE_URL}/api/emprestimos/criar", json=loan_data, headers=headers)
    if response.status_code == 200:
        return response.json()["emprestimo_id"]
    return None
def calcular_penalizacao(valor_emprestimo, dias_atraso, tem_emprestimos_anteriores):
    """Calcula o valor total de penalização baseado no valor do empréstimo e dias de atraso (5% por dia)"""
    penalizacao_dias = valor_emprestimo * 0.05 * dias_atraso
    adicional = 0.0  # Sem penalização adicional por empréstimos anteriores
    total = penalizacao_dias + adicional
    return total, penalizacao_dias, adicional


def testar_pagamentos_isolado():
    """Testa funcionalidades da classe pagamentos de forma isolada"""
    print("TESTANDO PAGAMENTOS - ISOLADO")
    print("=" * 40)

    access_token = get_auth_token()
    if not access_token:
        print("[ERRO] Não foi possível obter token de autenticação")
        return False

    headers = {"Authorization": f"Bearer {access_token}"}

    # Criar cliente e empréstimo para teste
    client_id = create_test_client(access_token)
    if not client_id:
        print("[ERRO] Não foi possível criar cliente de teste")
        return False

    loan_id = create_test_loan(access_token, client_id)
    if not loan_id:
        print("[ERRO] Não foi possível criar empréstimo de teste")
        return False

    success_count = 0
    total_tests = 0

    # Teste 1: Criar pagamento
    total_tests += 1
    print("\n1. Criando pagamento...")
    try:
        payment_data = {
            "emprestimo_id": loan_id,
            "cliente_id": client_id,
            "valor_pago": 1000.00,
            "data_pagamento": "2024-01-10T00:00:00Z",
            "metodo_pagamento": "Numerario",
            "referencia_pagamento": "REF-TEST-001"
        }
        response = requests.post(f"{BASE_URL}/api/pagamentos/criar", json=payment_data, headers=headers)
        if response.status_code == 200:
            payment = response.json()
            payment_id = payment["pagamento_id"]
            print(f"[OK] Pagamento criado: ID {payment_id}")
            success_count += 1
        else:
            print(f"[ERRO] Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # Teste 2: Listar pagamentos
    total_tests += 1
    print("\n2. Listando pagamentos...")
    try:
        response = requests.get(f"{BASE_URL}/api/pagamentos/listar", headers=headers)
        if response.status_code == 200:
            payments = response.json()
            print(f"[OK] {len(payments)} pagamentos encontrados")
            success_count += 1
        else:
            print(f"[ERRO] Status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # Teste 3: Obter pagamento específico
    total_tests += 1
    if 'payment_id' in locals():
        print(f"\n3. Obtendo pagamento ID {payment_id}...")
        try:
            response = requests.get(f"{BASE_URL}/api/pagamentos/obter/{payment_id}", headers=headers)
            if response.status_code == 200:
                print("[OK] Pagamento obtido com sucesso")
                success_count += 1
            else:
                print(f"[ERRO] Status {response.status_code}")
        except Exception as e:
            print(f"[ERRO] {e}")

    # Teste 4: Obter pagamentos por empréstimo
    total_tests += 1
    print(f"\n4. Obtendo pagamentos do empréstimo {loan_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/pagamentos/emprestimo/{loan_id}", headers=headers)
        if response.status_code == 200:
            loan_payments = response.json()
            print(f"[OK] {len(loan_payments)} pagamentos encontrados para o empréstimo")
            success_count += 1
        else:
            print(f"[ERRO] Status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # Teste 5: Obter pagamentos por cliente
    total_tests += 1
    print(f"\n5. Obtendo pagamentos do cliente {client_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/pagamentos/cliente/{client_id}", headers=headers)
        if response.status_code == 200:
            client_payments = response.json()
            print(f"[OK] {len(client_payments)} pagamentos encontrados para o cliente")
            success_count += 1
        else:
            print(f"[ERRO] Status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")

    print(f"\nResultado Pagamentos: {success_count}/{total_tests} testes passaram")
    return success_count == total_tests

def testar_emprestimos_isolado():
    """Testa funcionalidades da classe empréstimos de forma isolada"""
    print("\n\nTESTANDO EMPRÉSTIMOS - ISOLADO")
    print("=" * 40)

    access_token = get_auth_token()
    if not access_token:
        print("[ERRO] Não foi possível obter token de autenticação")
        return False

    headers = {"Authorization": f"Bearer {access_token}"}

    # Criar cliente para teste
    client_id = create_test_client(access_token)
    if not client_id:
        print("[ERRO] Não foi possível criar cliente de teste")
        return False

    success_count = 0
    total_tests = 0

    # Teste 1: Criar empréstimo
    total_tests += 1
    print("\n1. Criando empréstimo...")
    try:
        from datetime import datetime, timedelta
        data_vencimento = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")

        loan_data = {
            "cliente_id": client_id,
            "valor": 10000.00,
            "data_emprestimo": "2024-01-01T00:00:00",
            "data_vencimento": data_vencimento,
            "status": "Ativo"
        }
        response = requests.post(f"{BASE_URL}/api/emprestimos/criar", json=loan_data, headers=headers)
        if response.status_code == 200:
            loan = response.json()
            loan_id = loan["emprestimo_id"]
            print(f"[OK] Empréstimo criado: ID {loan_id}")
            success_count += 1
        else:
            print(f"[ERRO] Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # Teste 2: Listar empréstimos
    total_tests += 1
    print("\n2. Listando empréstimos...")
    try:
        response = requests.get(f"{BASE_URL}/api/emprestimos/listar", headers=headers)
        if response.status_code == 200:
            loans = response.json()
            print(f"[OK] {len(loans)} empréstimos encontrados")
            success_count += 1
        else:
            print(f"[ERRO] Status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # Teste 3: Obter empréstimo específico
    total_tests += 1
    if 'loan_id' in locals():
        print(f"\n3. Obtendo empréstimo ID {loan_id}...")
        try:
            response = requests.get(f"{BASE_URL}/api/emprestimos/obter/{loan_id}", headers=headers)
            if response.status_code == 200:
                print("[OK] Empréstimo obtido com sucesso")
                success_count += 1
            else:
                print(f"[ERRO] Status {response.status_code}")
        except Exception as e:
            print(f"[ERRO] {e}")

    # Teste 4: Obter empréstimos por cliente
    total_tests += 1
    print(f"\n4. Obtendo empréstimos do cliente {client_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/emprestimos/cliente/{client_id}", headers=headers)
        if response.status_code == 200:
            client_loans = response.json()
            print(f"[OK] {len(client_loans)} empréstimos encontrados para o cliente")
            success_count += 1
        else:
            print(f"[ERRO] Status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")

    print(f"\nResultado Empréstimos: {success_count}/{total_tests} testes passaram")
    return success_count == total_tests

def testar_penalizacoes_isolado():
    """Testa funcionalidades da classe penalizações de forma isolada"""
    print("\n\nTESTANDO PENALIZAÇÕES - ISOLADO")
    print("=" * 40)

    access_token = get_auth_token()
    if not access_token:
        print("[ERRO] Não foi possível obter token de autenticação")
        return False

    headers = {"Authorization": f"Bearer {access_token}"}

    # Criar cliente e empréstimo vencido para teste
    client_id = create_test_client(access_token)
    if not client_id:
        print("[ERRO] Não foi possível criar cliente de teste")
        return False

    loan_id = create_test_loan(access_token, client_id)
    if not loan_id:
        print("[ERRO] Não foi possível criar empréstimo de teste")
        return False

    success_count = 0
    total_tests = 0


    # Teste 2: Aplicar penalizações automáticas
    total_tests += 1
    print("\n1. Aplicando penalizações automáticas...")
    try:
        response = requests.post(f"{BASE_URL}/api/penalizacoes/aplicar-automatico", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] {result['mensagem']}")
            success_count += 1
        else:
            print(f"[ERRO] Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # Teste 3: Listar penalizações
    total_tests += 1
    print("\n2. Listando penalizações...")
    try:
        response = requests.get(f"{BASE_URL}/api/penalizacoes/listar", headers=headers)
        if response.status_code == 200:
            penalizacoes = response.json()
            print(f"[OK] {len(penalizacoes)} penalizações encontradas")
            success_count += 1
        else:
            print(f"[ERRO] Status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")

    print(f"\nResultado Penalizações: {success_count}/{total_tests} testes passaram")
    return success_count == total_tests

def testar_notificacoes_isolado():
    """Testa funcionalidades da classe notificações de forma isolada"""
    print("\n\nTESTANDO NOTIFICAÇÕES - ISOLADO")
    print("=" * 40)

    access_token = get_auth_token()
    if not access_token:
        print("[ERRO] Não foi possível obter token de autenticação")
        return False

    headers = {"Authorization": f"Bearer {access_token}"}

    # Criar cliente para teste
    client_id = create_test_client(access_token)
    if not client_id:
        print("[ERRO] Não foi possível criar cliente de teste")
        return False

    success_count = 0
    total_tests = 0

    # Teste 1: Verificar pagamentos e criar notificações
    total_tests += 1
    print("\n1. Verificando pagamentos e criando notificações...")
    try:
        response = requests.post(f"{BASE_URL}/api/notificacoes/verificar-pagamentos", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] {result['mensagem']}")
            success_count += 1
        else:
            print(f"[ERRO] Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # Teste 2: Listar notificações
    total_tests += 1
    print("\n2. Listando notificações...")
    try:
        response = requests.get(f"{BASE_URL}/api/notificacoes/listar", headers=headers)
        if response.status_code == 200:
            notificacoes = response.json()
            print(f"[OK] {len(notificacoes)} notificações encontradas")
            success_count += 1
        else:
            print(f"[ERRO] Status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # Teste 3: Obter notificações por cliente
    total_tests += 1
    print(f"\n3. Obtendo notificações do cliente {client_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/notificacoes/cliente/{client_id}", headers=headers)
        if response.status_code == 200:
            client_notificacoes = response.json()
            print(f"[OK] {len(client_notificacoes)} notificações encontradas para o cliente")
            success_count += 1
        else:
            print(f"[ERRO] Status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")

    print(f"\nResultado Notificações: {success_count}/{total_tests} testes passaram")
    return success_count == total_tests

def executar_testes_isolados():
    """Executa todos os testes isolados das classes especificadas"""
    print("TESTES ISOLADOS - PAGAMENTOS, EMPRÉSTIMOS, PENALIZAÇÕES, NOTIFICAÇÕES")
    print("=" * 70)

    resultados = []

    # Executar testes de cada classe
    resultados.append(("Pagamentos", testar_pagamentos_isolado()))
    resultados.append(("Empréstimos", testar_emprestimos_isolado()))
    resultados.append(("Penalizações", testar_penalizacoes_isolado()))
    resultados.append(("Notificações", testar_notificacoes_isolado()))

    # Resultado final
    print("\n" + "=" * 70)
    print("RESULTADO FINAL DOS TESTES ISOLADOS:")
    print("=" * 70)

    todos_passaram = True
    for nome, passou in resultados:
        status = "[OK]" if passou else "[FALHOU]"
        print(f"{status} {nome}")
        if not passou:
            todos_passaram = False

    if todos_passaram:
        print("\n[SUCESSO] Todos os testes isolados passaram!")
    else:
        print("\n[AVISO] Alguns testes isolados falharam.")

    return todos_passaram

if __name__ == "__main__":
    executar_testes_isolados()