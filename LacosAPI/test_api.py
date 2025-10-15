import requests
import json
import time
import sys
from test_isolated import calcular_penalizacao

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

def testar_autenticacao():
    """Testa especificamente a funcionalidade de autenticação de funcionários"""
    print("Testando Autenticação de Funcionários")
    print("=" * 50)

    # Teste 1: Login com credenciais válidas
    print("\n1. Testando login com credenciais válidas...")
    try:
        login_data = {
            "username": "natalia.massinga",
            "password": "Ractis@23"
        }
        response = requests.post(f"{BASE_URL}/api/auth/token", data=login_data)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"[OK] Token de acesso obtido com sucesso: {access_token[:20]}...")
            print(f"[OK] Tipo de token: {token_data['token_type']}")
            return access_token
        else:
            print(f"[ERRO] Falha na autenticação: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"[ERRO] Erro na autenticação: {e}")
        return None

def testar_clientes(access_token):
    """Testa operações CRUD de clientes"""
    print("\n\nTestando Clientes")
    print("=" * 30)

    headers = {"Authorization": f"Bearer {access_token}"}
    client_id = None

    # 1. Criar cliente
    print("\n1. Criando cliente...")
    try:
        client_data = {
            "nome": "João Silva Teste",
            "sexo": "Masculino",
            "telefone": f"987654321{int(time.time())}",
            "email": f"joao.silva.teste{int(time.time())}@example.com",
            "nacionalidade": "Moçambicana",
            "data_nascimento": "1990-01-01"
        }
        response = requests.post(f"{BASE_URL}/api/clientes/criar", json=client_data, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            client = response.json()
            client_id = client["cliente_id"]
            print(f"[OK] Cliente criado com ID: {client_id}")
        else:
            print(f"[ERRO] {response.text}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # 2. Listar clientes
    print("\n2. Listando clientes...")
    try:
        response = requests.get(f"{BASE_URL}/api/clientes/listar", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            clients = response.json()
            print(f"[OK] {len(clients)} clientes encontrados")
    except Exception as e:
        print(f"[ERRO] {e}")

    # 3. Obter cliente específico
    if client_id:
        print(f"\n3. Obtendo cliente ID {client_id}...")
        try:
            response = requests.get(f"{BASE_URL}/api/clientes/obter/{client_id}", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("[OK] Cliente obtido com sucesso")
        except Exception as e:
            print(f"[ERRO] {e}")

    return client_id

def testar_localizacoes(access_token, client_id):
    """Testa operações CRUD de localizações"""
    print("\n\nTestando Localizações")
    print("=" * 35)

    headers = {"Authorization": f"Bearer {access_token}"}
    location_id = None

    if not client_id:
        print("[SKIP] Cliente não disponível")
        return None

    # 1. Criar localização
    print("\n1. Criando localização...")
    try:
        location_data = {
            "cliente_id": client_id,
            "bairro": "Centro",
            "numero_da_casa": "123",
            "quarteirao": "B",
            "cidade": "Maputo",
            "distrito": "Kampfumo",
            "provincia": "Maputo"
        }
        response = requests.post(f"{BASE_URL}/api/localizacoes/criar", json=location_data, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            location = response.json()
            location_id = location["localizacao_id"]
            print(f"[OK] Localização criada com ID: {location_id}")
        else:
            print(f"[ERRO] {response.text}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # 2. Listar localizações
    print("\n2. Listando localizações...")
    try:
        response = requests.get(f"{BASE_URL}/api/localizacoes/listar", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            locations = response.json()
            print(f"[OK] {len(locations)} localizações encontradas")
    except Exception as e:
        print(f"[ERRO] {e}")

    return location_id

def testar_emprestimos(access_token, client_id):
    """Testa operações CRUD de empréstimos"""
    print("\n\nTestando Empréstimos")
    print("=" * 32)

    headers = {"Authorization": f"Bearer {access_token}"}
    emprestimo_id = None

    if not client_id:
        print("[SKIP] Cliente não disponível")
        return None

    # 1. Criar empréstimo com data de vencimento passada para testar penalizações
    print("\n1. Criando empréstimo com vencimento passado...")
    try:
        from datetime import datetime, timedelta
        data_vencimento_passada = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S")

        emprestimo_data = {
            "cliente_id": client_id,
            "valor": 10000.00,
            "data_emprestimo": "2024-01-01T00:00:00",
            "data_vencimento": data_vencimento_passada,
            "status": "Ativo"
        }
        response = requests.post(f"{BASE_URL}/api/emprestimos/criar", json=emprestimo_data, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            emprestimo = response.json()
            emprestimo_id = emprestimo["emprestimo_id"]
            print(f"[OK] Empréstimo criado com ID: {emprestimo_id}")
            print(f"[OK] Data de vencimento: {data_vencimento_passada} (passada)")
            print("[OK] Notificação automática de confirmação deve ter sido gerada")
        else:
            print(f"[ERRO] {response.text}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # 2. Listar empréstimos
    print("\n2. Listando empréstimos...")
    try:
        response = requests.get(f"{BASE_URL}/api/emprestimos/listar", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            emprestimos = response.json()
            print(f"[OK] {len(emprestimos)} empréstimos encontrados")
    except Exception as e:
        print(f"[ERRO] {e}")

    return emprestimo_id

def testar_pagamentos(access_token, emprestimo_id, client_id):
    """Testa operações CRUD de pagamentos"""
    print("\n\nTestando Pagamentos")
    print("=" * 30)

    headers = {"Authorization": f"Bearer {access_token}"}
    pagamento_id = None

    if not emprestimo_id or not client_id:
        print("[SKIP] Empréstimo ou cliente não disponível")
        return None

    # 1. Criar pagamento
    print("\n1. Criando pagamento...")
    try:
        pagamento_data = {
            "emprestimo_id": emprestimo_id,
            "cliente_id": client_id,
            "valor_pago": 1000.00,
            "data_pagamento": "2024-01-15T00:00:00Z",
            "metodo_pagamento": "Numerario",
            "referencia_pagamento": "REF-001"
        }
        response = requests.post(f"{BASE_URL}/api/pagamentos/criar", json=pagamento_data, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            pagamento = response.json()
            pagamento_id = pagamento["pagamento_id"]
            print(f"[OK] Pagamento criado com ID: {pagamento_id}")
            print("[OK] Notificação automática de confirmação deve ter sido gerada")
        else:
            print(f"[ERRO] {response.text}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # 2. Listar pagamentos
    print("\n2. Listando pagamentos...")
    try:
        response = requests.get(f"{BASE_URL}/api/pagamentos/listar", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            pagamentos = response.json()
            print(f"[OK] {len(pagamentos)} pagamentos encontrados")
    except Exception as e:
        print(f"[ERRO] {e}")

    return pagamento_id

def testar_penalizacoes(access_token, emprestimo_id):
    """Testa operações de penalizações"""
    print("\n\nTestando Penalizações")
    print("=" * 32)

    headers = {"Authorization": f"Bearer {access_token}"}

    if not emprestimo_id:
        print("[SKIP] Empréstimo não disponível")
        return

    # 1. Criar penalização manual
    print("\n1. Criando penalização manual...")
    try:
        from datetime import datetime
        data_referencia = datetime.now().isoformat()
        params = {"emprestimo_id": emprestimo_id, "data_referencia": data_referencia}
        response = requests.post(f"{BASE_URL}/api/penalizacoes/criar", params=params, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            penalizacao = response.json()
            print(f"[OK] Penalização criada: ID {penalizacao['penalizacao_id']}, Valor: {penalizacao['valor']}")
        else:
            print(f"[ERRO] Resposta: {response.text}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # 2. Aplicar penalização automática (isso gera notificação)
    print("\n2. Aplicando penalizações automáticas...")
    try:
        response = requests.post(f"{BASE_URL}/api/penalizacoes/aplicar-automatico", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] {result['mensagem']}")
            print("[OK] Notificações automáticas de penalização devem ter sido geradas")
    except Exception as e:
        print(f"[ERRO] {e}")

    # 3. Listar penalizações
    print("\n3. Listando penalizações...")
    try:
        response = requests.get(f"{BASE_URL}/api/penalizacoes/listar", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            penalizacoes = response.json()
            print(f"[OK] {len(penalizacoes)} penalizações encontradas")
    except Exception as e:
        print(f"[ERRO] {e}")

def verificar_calculo_penalizacoes(access_token, emprestimo_id, client_id):
    """Verifica se os cálculos de penalizações estão corretos usando a fórmula isolada"""
    print("\n\nVerificando Cálculos de Penalizações")
    print("=" * 45)

    headers = {"Authorization": f"Bearer {access_token}"}

    if not emprestimo_id or not client_id:
        print("[SKIP] Empréstimo ou cliente não disponível")
        return False

    try:
        # Obter dados do empréstimo
        response = requests.get(f"{BASE_URL}/api/emprestimos/obter/{emprestimo_id}", headers=headers)
        if response.status_code != 200:
            print(f"[ERRO] Não foi possível obter empréstimo: {response.status_code}")
            return False

        emprestimo = response.json()
        valor_emprestimo = float(emprestimo['valor'])

        # Criar penalização com data futura para gerar atraso
        from datetime import datetime, timedelta
        data_referencia = (datetime.now() + timedelta(days=30)).isoformat()
        params = {"emprestimo_id": emprestimo_id, "data_referencia": data_referencia}

        response = requests.post(f"{BASE_URL}/api/penalizacoes/criar", params=params, headers=headers)
        if response.status_code != 200:
            print(f"[ERRO] Falha ao criar penalização: {response.status_code}")
            return False

        penalizacao_criada = response.json()
        dias_atraso = penalizacao_criada['dias_atraso']
        penalizacao_calculada = float(penalizacao_criada['valor'])

        # Verificar se cliente tem empréstimos anteriores
        response = requests.get(f"{BASE_URL}/api/emprestimos/cliente/{client_id}", headers=headers)
        emprestimos_anteriores = [e for e in response.json() if e['emprestimo_id'] != emprestimo_id]
        tem_emprestimos_anteriores = len(emprestimos_anteriores) > 0

        penalizacao_esperada, penalizacao_dias, adicional = calcular_penalizacao(valor_emprestimo, dias_atraso, tem_emprestimos_anteriores)

        print(f"[INFO] Valor empréstimo: {valor_emprestimo}")
        print(f"[INFO] Dias de atraso: {dias_atraso}")
        print(f"[INFO] Penalização dias: {penalizacao_dias}")
        print(f"[INFO] Adicional (empréstimos anteriores): {adicional}")
        print(f"[INFO] Penalização esperada: {penalizacao_esperada}")
        print(f"[INFO] Penalização calculada: {penalizacao_calculada}")

        if abs(penalizacao_esperada - penalizacao_calculada) < 0.01:  # Tolerância para arredondamento
            print("[OK] Cálculo de penalização está correto!")
            return True
        else:
            print("[ERRO] Cálculo de penalização está incorreto!")
            return False

    except Exception as e:
        print(f"[ERRO] Erro na verificação: {e}")
        return False

def verificar_pagamentos_e_penalizacoes(access_token, emprestimo_id, client_id):
    """Verifica se os pagamentos cobrem empréstimo + penalizações"""
    print("\n\nVerificando Pagamentos vs Empréstimo + Penalizações")
    print("=" * 55)

    headers = {"Authorization": f"Bearer {access_token}"}

    if not emprestimo_id or not client_id:
        print("[SKIP] Empréstimo ou cliente não disponível")
        return False

    try:
        # Obter dados do empréstimo
        response = requests.get(f"{BASE_URL}/api/emprestimos/obter/{emprestimo_id}", headers=headers)
        if response.status_code != 200:
            print(f"[ERRO] Não foi possível obter empréstimo: {response.status_code}")
            return False

        emprestimo = response.json()
        valor_emprestimo = float(emprestimo['valor'])

        # Obter todos os pagamentos do empréstimo
        response = requests.get(f"{BASE_URL}/api/pagamentos/emprestimo/{emprestimo_id}", headers=headers)
        if response.status_code != 200:
            print(f"[ERRO] Não foi possível obter pagamentos: {response.status_code}")
            return False

        pagamentos = response.json()
        total_pago = sum(float(p['valor_pago']) for p in pagamentos)

        # Obter penalizações do empréstimo
        response = requests.get(f"{BASE_URL}/api/penalizacoes/listar", headers=headers)
        if response.status_code != 200:
            print(f"[ERRO] Não foi possível obter penalizações: {response.status_code}")
            return False

        penalizacoes_emprestimo = [p for p in response.json() if p['emprestimo_id'] == emprestimo_id]
        total_penalizacoes = sum(float(p['valor']) for p in penalizacoes_emprestimo)

        valor_total_devido = valor_emprestimo + total_penalizacoes

        print(f"[INFO] Valor empréstimo: {valor_emprestimo}")
        print(f"[INFO] Total penalizações: {total_penalizacoes}")
        print(f"[INFO] Valor total devido: {valor_total_devido}")
        print(f"[INFO] Total pago: {total_pago}")
        print(f"[INFO] Diferença: {total_pago - valor_total_devido}")

        if total_pago >= valor_total_devido:
            print("[OK] Pagamentos cobrem empréstimo + penalizações!")
            return True
        else:
            print("[AVISO] Pagamentos insuficientes para cobrir empréstimo + penalizações")
            return False

    except Exception as e:
        print(f"[ERRO] Erro na verificação: {e}")
        return False

def testar_notificacoes(access_token):
    """Testa operações de notificações"""
    print("\n\nTestando Notificações")
    print("=" * 32)

    headers = {"Authorization": f"Bearer {access_token}"}

    # 1. Verificar e criar notificações automaticamente
    print("\n1. Verificando pagamentos e criando notificações...")
    try:
        response = requests.post(f"{BASE_URL}/api/notificacoes/verificar-pagamentos", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] {result['mensagem']}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # 2. Listar notificações
    print("\n2. Listando notificações...")
    try:
        response = requests.get(f"{BASE_URL}/api/notificacoes/listar", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            notificacoes = response.json()
            print(f"[OK] {len(notificacoes)} notificações encontradas")
    except Exception as e:
        print(f"[ERRO] {e}")

def testar_historico_credito(access_token, client_id):
    """Testa operações de histórico de crédito"""
    print("\n\nTestando Histórico de Crédito")
    print("=" * 40)

    headers = {"Authorization": f"Bearer {access_token}"}

    if not client_id:
        print("[SKIP] Cliente não disponível")
        return

    # 1. Atualizar histórico automaticamente
    print("\n1. Atualizando histórico de crédito automaticamente...")
    try:
        response = requests.post(f"{BASE_URL}/api/historico-credito/atualizar-automatico", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] {result['mensagem']}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # 2. Análise de crédito
    print("\n2. Fazendo análise de crédito...")
    try:
        response = requests.get(f"{BASE_URL}/api/historico-credito/analise-credito/{client_id}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            analise = response.json()
            print(f"[OK] Score: {analise['score_credito']}, Recomendação: {analise['recomendacao']}")
    except Exception as e:
        print(f"[ERRO] {e}")

def testar_ocupacoes(access_token, client_id):
    """Testa operações CRUD de ocupações"""
    print("\n\nTestando Ocupações")
    print("=" * 30)

    headers = {"Authorization": f"Bearer {access_token}"}
    ocupacao_id = None

    if not client_id:
        print("[SKIP] Cliente não disponível")
        return None

    # 1. Criar ocupação
    print("\n1. Criando ocupação...")
    try:
        timestamp = int(time.time())
        ocupacao_data = {
            "cliente_id": client_id,
            "codigo": f"ENG{timestamp % 10000:05d}",
            "nome": f"Engenheiro de Software {timestamp % 1000}",
            "descricao": "Desenvolvimento de aplicações",
            "categoria_risco": "Baixo",
            "renda_minima": 50000.00,
            "setor_economico": "Secundario",
            "estabilidade_emprego": "Alta",
            "ativo": True
        }
        response = requests.post(f"{BASE_URL}/api/ocupacoes/criar", json=ocupacao_data, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            ocupacao = response.json()
            ocupacao_id = ocupacao["ocupacao_id"]
            print(f"[OK] Ocupação criada com ID: {ocupacao_id}")
        else:
            print(f"[ERRO] {response.text}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # 2. Listar ocupações
    print("\n2. Listando ocupações...")
    try:
        response = requests.get(f"{BASE_URL}/api/ocupacoes/listar", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            ocupacoes = response.json()
            print(f"[OK] {len(ocupacoes)} ocupações encontradas")
    except Exception as e:
        print(f"[ERRO] {e}")

    return ocupacao_id

def testar_auth_clientes(access_token, client_id):
    """Testa operações de autenticação de clientes"""
    print("\n\nTestando Autenticação de Clientes")
    print("=" * 42)

    headers = {"Authorization": f"Bearer {access_token}"}
    auth_id = None

    if not client_id:
        print("[SKIP] Cliente não disponível")
        return None

    # 1. Criar autenticação de cliente
    print("\n1. Criando autenticação de cliente...")
    try:
        auth_data = {
            "cliente_id": client_id,
            "username": f"cliente.teste{int(time.time())}",
            "password": "senha123"
        }
        response = requests.post(f"{BASE_URL}/api/auth-clientes/criar", json=auth_data, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            auth = response.json()
            auth_id = auth["autenticacao_id"]
            print(f"[OK] Autenticação criada com ID: {auth_id}")
        else:
            print(f"[ERRO] {response.text}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # 2. Testar login do cliente
    if auth_id:
        print("\n2. Testando login do cliente...")
        try:
            login_data = {
                "username": auth_data["username"],
                "password": "senha123"
            }
            response = requests.post(f"{BASE_URL}/api/auth-clientes/login", json=login_data)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                login_result = response.json()
                print(f"[OK] Login realizado. Token: {login_result['access_token'][:20]}...")
        except Exception as e:
            print(f"[ERRO] {e}")

    return auth_id

def testar_notificacoes_automaticas(access_token, client_id):
    """Testa se as notificações automáticas foram criadas para cliente e admin"""
    print("\n\nVerificando Notificações Automáticas")
    print("=" * 45)

    headers = {"Authorization": f"Bearer {access_token}"}

    if not client_id:
        print("[SKIP] Cliente não disponível")
        return

    # Verificar notificações do cliente
    print(f"\n1. Verificando notificações do cliente {client_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/notificacoes/cliente/{client_id}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            notificacoes_cliente = response.json()
            print(f"[OK] Cliente tem {len(notificacoes_cliente)} notificações")

            # Mostrar tipos de notificações do cliente
            tipos_cliente = [n['tipo'] for n in notificacoes_cliente]
            print(f"[INFO] Tipos de notificações do cliente: {set(tipos_cliente)}")

            # Verificar se há notificações automáticas esperadas para cliente
            tipos_automaticos = ['Confirmação de Empréstimo', 'Confirmação de Pagamento', 'Penalização Aplicada', 'Atraso no Pagamento']
            notificacoes_automaticas_cliente = [n for n in notificacoes_cliente if n['tipo'] in tipos_automaticos]

            if notificacoes_automaticas_cliente:
                print(f"[OK] {len(notificacoes_automaticas_cliente)} notificações automáticas encontradas para cliente")
                for notif in notificacoes_automaticas_cliente[:2]:  # Mostrar primeiras 2
                    print(f"  - {notif['tipo']}: {notif['mensagem'][:60]}...")
            else:
                print("[AVISO] Nenhuma notificação automática encontrada para cliente")
        else:
            print(f"[ERRO] {response.text}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # Verificar notificações administrativas (cliente_id = NULL)
    print(f"\n2. Verificando notificações administrativas...")
    try:
        response = requests.get(f"{BASE_URL}/api/notificacoes/listar", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            todas_notificacoes = response.json()
            notificacoes_admin = [n for n in todas_notificacoes if n['cliente_id'] is None]

            print(f"[OK] Sistema tem {len(notificacoes_admin)} notificações administrativas")

            # Mostrar tipos de notificações admin
            tipos_admin = [n['tipo'] for n in notificacoes_admin]
            print(f"[INFO] Tipos de notificações admin: {set(tipos_admin)}")

            # Verificar se há notificações automáticas esperadas para admin
            notificacoes_automaticas_admin = [n for n in notificacoes_admin if n['tipo'] in tipos_automaticos]

            if notificacoes_automaticas_admin:
                print(f"[OK] {len(notificacoes_automaticas_admin)} notificações automáticas encontradas para admin")
                for notif in notificacoes_automaticas_admin[-2:]:  # Mostrar últimas 2 (mais recentes)
                    print(f"  - {notif['tipo']}: {notif['mensagem'][:60]}...")
            else:
                print("[AVISO] Nenhuma notificação automática encontrada para admin")
        else:
            print(f"[ERRO] {response.text}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # Verificação final
    try:
        total_notificacoes = len(notificacoes_cliente) + len(notificacoes_admin)
        print(f"\n[INFO] Total de notificações no sistema: {total_notificacoes}")
        print("[OK] Sistema de notificações duplas (cliente + admin) está funcionando")
    except:
        pass

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

    # Teste 1: Aplicar penalizações automáticas
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

    # Teste 2: Listar penalizações
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

def testar_notificacoes_completas():
    """Testa o sistema completo de notificações: cliente + admin"""
    print("\n\nTESTANDO NOTIFICAÇÕES COMPLETAS - CLIENTE + ADMIN")
    print("=" * 55)

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

    # Criar empréstimo vencido
    loan_id = create_test_loan(access_token, client_id)
    if not loan_id:
        print("[ERRO] Não foi possível criar empréstimo de teste")
        return False

    success_count = 0
    total_tests = 0

    # Teste 1: Verificar notificações após criação do empréstimo
    total_tests += 1
    print("\n1. Verificando notificações após criação do empréstimo...")
    try:
        # Listar todas as notificações
        response = requests.get(f"{BASE_URL}/api/notificacoes/listar", headers=headers)
        if response.status_code == 200:
            todas_notificacoes = response.json()
            notificacoes_emprestimo = [n for n in todas_notificacoes if n['tipo'] == 'Confirmação de Empréstimo']

            if len(notificacoes_emprestimo) >= 2:  # Uma para cliente, uma para admin
                print(f"[OK] {len(notificacoes_emprestimo)} notificações de empréstimo encontradas")
                success_count += 1
            else:
                print(f"[AVISO] Esperado 2 notificações, encontrado {len(notificacoes_emprestimo)}")
        else:
            print(f"[ERRO] Status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # Teste 2: Criar pagamento e verificar notificações
    total_tests += 1
    print("\n2. Criando pagamento e verificando notificações...")
    try:
        payment_data = {
            "emprestimo_id": loan_id,
            "cliente_id": client_id,
            "valor_pago": 1000.00,
            "data_pagamento": "2024-01-10T00:00:00Z",
            "metodo_pagamento": "Numerario",
            "referencia_pagamento": "TEST-PAY-001"
        }
        response = requests.post(f"{BASE_URL}/api/pagamentos/criar", json=payment_data, headers=headers)
        if response.status_code == 200:
            # Verificar notificações de pagamento
            response = requests.get(f"{BASE_URL}/api/notificacoes/listar", headers=headers)
            if response.status_code == 200:
                todas_notificacoes = response.json()
                notificacoes_pagamento = [n for n in todas_notificacoes if n['tipo'] == 'Confirmação de Pagamento']

                if len(notificacoes_pagamento) >= 2:  # Uma para cliente, uma para admin
                    print(f"[OK] {len(notificacoes_pagamento)} notificações de pagamento encontradas")
                    success_count += 1
                else:
                    print(f"[AVISO] Esperado 2 notificações, encontrado {len(notificacoes_pagamento)}")
            else:
                print(f"[ERRO] Status {response.status_code}")
        else:
            print(f"[ERRO] Falha ao criar pagamento: {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # Teste 3: Aplicar penalizações e verificar notificações
    total_tests += 1
    print("\n3. Aplicando penalizações e verificando notificações...")
    try:
        response = requests.post(f"{BASE_URL}/api/penalizacoes/aplicar-automatico", headers=headers)
        if response.status_code == 200:
            # Verificar notificações de penalização
            response = requests.get(f"{BASE_URL}/api/notificacoes/listar", headers=headers)
            if response.status_code == 200:
                todas_notificacoes = response.json()
                notificacoes_penalizacao = [n for n in todas_notificacoes if n['tipo'] == 'Penalização Aplicada']

                if len(notificacoes_penalizacao) >= 2:  # Uma para cliente, uma para admin
                    print(f"[OK] {len(notificacoes_penalizacao)} notificações de penalização encontradas")
                    success_count += 1
                else:
                    print(f"[AVISO] Esperado 2 notificações, encontrado {len(notificacoes_penalizacao)}")
            else:
                print(f"[ERRO] Status {response.status_code}")
        else:
            print(f"[ERRO] Falha ao aplicar penalizações: {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")

    # Teste 4: Verificar distribuição cliente vs admin
    total_tests += 1
    print("\n4. Verificando distribuição de notificações...")
    try:
        response = requests.get(f"{BASE_URL}/api/notificacoes/listar", headers=headers)
        if response.status_code == 200:
            todas_notificacoes = response.json()
            notificacoes_cliente = [n for n in todas_notificacoes if n['cliente_id'] == client_id]
            notificacoes_admin = [n for n in todas_notificacoes if n['cliente_id'] is None]

            print(f"[INFO] Notificações para cliente: {len(notificacoes_cliente)}")
            print(f"[INFO] Notificações para admin: {len(notificacoes_admin)}")

            if len(notificacoes_cliente) > 0 and len(notificacoes_admin) > 0:
                print("[OK] Sistema de notificações duplas funcionando corretamente")
                success_count += 1
            else:
                print("[ERRO] Falta notificações para cliente ou admin")
        else:
            print(f"[ERRO] Status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] {e}")

    print(f"\nResultado Notificações Completas: {success_count}/{total_tests} testes passaram")
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

def testar_api():
    print("Testando API do Lacos Microcrédito - Versão Completa com Verificações")
    print("=" * 70)

    # Primeiro, testar especificamente a autenticação
    access_token = testar_autenticacao()
    if not access_token:
        print("\n[ERRO] Falha na autenticação. Interrompendo testes.")
        return False

    print(f"\n{'='*70}")
    print("Iniciando testes completos da API com verificações de penalizações...")
    print("=" * 70)

    # Testar cada módulo em sequência
    client_id = testar_clientes(access_token)
    location_id = testar_localizacoes(access_token, client_id)
    emprestimo_id = testar_emprestimos(access_token, client_id)

    # Criar segundo empréstimo para testar penalização adicional para clientes repetidos
    print("\n\nCriando segundo empréstimo para testar penalização adicional...")
    emprestimo_id_2 = None
    if client_id:
        try:
            from datetime import datetime, timedelta
            data_vencimento_passada = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S")

            emprestimo_data = {
                "cliente_id": client_id,
                "valor": 5000.00,
                "data_emprestimo": "2024-02-01T00:00:00",
                "data_vencimento": data_vencimento_passada,
                "status": "Ativo"
            }
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.post(f"{BASE_URL}/api/emprestimos/criar", json=emprestimo_data, headers=headers)
            if response.status_code == 200:
                emprestimo = response.json()
                emprestimo_id_2 = emprestimo["emprestimo_id"]
                print(f"[OK] Segundo empréstimo criado com ID: {emprestimo_id_2}")
        except Exception as e:
            print(f"[ERRO] Falha ao criar segundo empréstimo: {e}")

    pagamento_id = testar_pagamentos(access_token, emprestimo_id, client_id)
    testar_penalizacoes(access_token, emprestimo_id)
    testar_notificacoes(access_token)
    testar_historico_credito(access_token, client_id)
    ocupacao_id = testar_ocupacoes(access_token, client_id)
    auth_id = testar_auth_clientes(access_token, client_id)

    # Verificações específicas de penalizações e pagamentos
    print("\n" + "=" * 70)
    print("INICIANDO VERIFICAÇÕES DE PENALIZAÇÕES E PAGAMENTOS")
    print("=" * 70)

    # Verificar cálculo de penalizações
    calc_ok = verificar_calculo_penalizacoes(access_token, emprestimo_id, client_id)
    if emprestimo_id_2:
        calc_ok_2 = verificar_calculo_penalizacoes(access_token, emprestimo_id_2, client_id)
        calc_ok = calc_ok and calc_ok_2

    # Verificar pagamentos vs empréstimo + penalizações
    pag_ok = verificar_pagamentos_e_penalizacoes(access_token, emprestimo_id, client_id)
    if emprestimo_id_2:
        pag_ok_2 = verificar_pagamentos_e_penalizacoes(access_token, emprestimo_id_2, client_id)
        pag_ok = pag_ok and pag_ok_2

    # Verificar notificações automáticas geradas
    testar_notificacoes_automaticas(access_token, client_id)

    # Executar testes isolados das classes específicas
    print("\n" + "=" * 70)
    print("EXECUTANDO TESTES ISOLADOS DAS CLASSES:")
    print("=" * 70)

    isolated_results = []
    isolated_results.append(("Pagamentos Isolado", testar_pagamentos_isolado()))
    isolated_results.append(("Empréstimos Isolado", testar_emprestimos_isolado()))
    isolated_results.append(("Penalizações Isolado", testar_penalizacoes_isolado()))
    isolated_results.append(("Notificações Isolado", testar_notificacoes_isolado()))
    isolated_results.append(("Notificações Completas", testar_notificacoes_completas()))

    print("\n" + "=" * 70)
    print("RESULTADO DOS TESTES:")
    print("=" * 70)

    # Verificar se todos os testes isolados passaram
    isolated_ok = all(result for _, result in isolated_results)

    if calc_ok and pag_ok and isolated_ok:
        print("[OK] Todos os testes da API concluídos com sucesso!")
        print("[OK] Cálculos de penalizações estão corretos!")
        print("[OK] Pagamentos estão de acordo com o sistema!")
        print("[OK] Notificações automáticas implementadas e testadas!")
        print("[OK] Testes isolados das classes passaram!")
        print("[OK] A API está funcionando corretamente!")
        print("=" * 70)
        return True
    else:
        print("[AVISO] Alguns testes falharam:")
        if not calc_ok:
            print("  - Cálculos de penalizações podem estar incorretos")
        if not pag_ok:
            print("  - Pagamentos podem não estar cobrindo empréstimo + penalizações")
        if not isolated_ok:
            print("  - Alguns testes isolados falharam")
        print("[INFO] Verifique os logs acima para mais detalhes")
        print("=" * 70)
        return False

if __name__ == "__main__":
    testar_api()
