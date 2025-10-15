# 🔒 Auditoria de Segurança - LacosAPI
## Análise Completa de Vulnerabilidades e Soluções

---

## ⚠️ VULNERABILIDADES CRÍTICAS (Prioridade ALTA)

### 1. **SECRET_KEY Fraca e Exposta**

**Vulnerabilidade:**
- [`SECRET_KEY`](LacosAPI/.env:2) está definida como "your-secret-key-change-in-production"
- Chave previsível permite forjar tokens JWT
- Arquivo `.env` pode ser commitado acidentalmente no Git

**Impacto:** 🔴 CRÍTICO
- Atacante pode criar tokens válidos para qualquer usuário
- Bypass completo de autenticação
- Acesso total ao sistema

**Solução Simples:**
```bash
# 1. Gerar chave segura de 256 bits
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Atualizar .env (nunca commitar este arquivo!)
SECRET_KEY=SUA_CHAVE_ALEATORIA_AQUI_64_CARACTERES_MINIMO

# 3. Adicionar ao .gitignore
echo ".env" >> .gitignore
```

**Solução Completa:**
```python
# app/utils/auth.py - Adicionar validação
import secrets
import sys

CHAVE_SECRETA = os.getenv("SECRET_KEY")
if not CHAVE_SECRETA or CHAVE_SECRETA == "your-secret-key-change-in-production":
    print("ERRO: SECRET_KEY não configurada ou usando valor padrão inseguro!")
    sys.exit(1)

if len(CHAVE_SECRETA) < 32:
    print("AVISO: SECRET_KEY muito curta (mínimo 32 caracteres)")
```

---

### 2. **CORS Totalmente Aberto (allow_origins="*")**

**Vulnerabilidade:**
- [`CORSMiddleware`](LacosAPI/main.py:23) configurado com `allow_origins=["*"]`
- Qualquer site pode fazer requisições à API
- Vulnerável a ataques Cross-Site Request Forgery (CSRF)

**Impacto:** 🔴 CRÍTICO
- Site malicioso pode fazer requisições em nome do usuário autenticado
- Roubo de dados sensíveis
- Execução de ações não autorizadas

**Solução Simples:**
```python
# main.py - Restringir origins permitidas
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend local
        "https://seu-dominio.com",  # Produção
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Solução com Variável de Ambiente:**
```python
# main.py
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

### 3. **Senha Padrão do Admin Muito Fraca**

**Vulnerabilidade:**
- Admin padrão tem senha [`"admin123"`](LacosAPI/app/database/database.py:56)
- Senha aparece em código e testes
- Sem política de força de senha

**Impacto:** 🔴 CRÍTICO
- Ataque de dicionário trivial
- Comprometimento imediato da conta admin
- Acesso total ao sistema

**Solução Simples:**
```python
# app/utils/auth.py - Adicionar validação de força de senha
import re

def validar_forca_senha(senha: str) -> tuple[bool, str]:
    """Valida força da senha. Retorna (válida, mensagem_erro)"""
    if len(senha) < 12:
        return False, "Senha deve ter no mínimo 12 caracteres"
    
    if not re.search(r"[A-Z]", senha):
        return False, "Senha deve conter pelo menos uma letra maiúscula"
    
    if not re.search(r"[a-z]", senha):
        return False, "Senha deve conter pelo menos uma letra minúscula"
    
    if not re.search(r"\d", senha):
        return False, "Senha deve conter pelo menos um número"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        return False, "Senha deve conter pelo menos um caractere especial"
    
    # Verificar senhas comuns
    senhas_comuns = ["admin123", "password", "12345678", "qwerty"]
    if senha.lower() in senhas_comuns:
        return False, "Senha muito comum, escolha uma senha mais forte"
    
    return True, "Senha válida"

# Usar na criação/atualização de funcionários
def criar_funcionario_com_senha(username, senha, ...):
    valida, msg = validar_forca_senha(senha)
    if not valida:
        raise HTTPException(status_code=400, detail=msg)
    # ... continuar criação
```

**Solução Imediata:**
```bash
# Trocar senha do admin imediatamente após instalação
# Via SQL ou endpoint de atualização
```

---

### 4. **Sem Rate Limiting (Brute Force Possível)**

**Vulnerabilidade:**
- Nenhum endpoint tem limitação de taxa de requisições
- [`autenticar_funcionario`](LacosAPI/app/utils/auth.py:28) não limita tentativas
- Campo `tentativas_login` existe mas não é usado

**Impacto:** 🔴 CRÍTICO
- Ataque de força bruta em `/api/auth/token`
- DoS (Denial of Service) em qualquer endpoint
- Tentativas ilimitadas de adivinhar senhas

**Solução Simples (com slowapi):**
```bash
# Instalar
pip install slowapi
```

```python
# main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# app/routes/auth.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/token")
@limiter.limit("5/minute")  # Máximo 5 tentativas por minuto
async def login_para_token_acesso(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    # ... código existente
```

**Solução Manual (implementar contador de tentativas):**
```python
# app/utils/auth.py
def autenticar_funcionario(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM funcionarios WHERE username = %s", (username,))
        funcionario = cursor.fetchone()
        
        if not funcionario:
            return False
        
        # Verificar se está bloqueado
        if funcionario['bloqueado']:
            tempo_bloqueio = datetime.now(timezone.utc) - funcionario['data_bloqueio']
            if tempo_bloqueio.total_seconds() < 900:  # 15 minutos
                raise HTTPException(
                    status_code=429,
                    detail=f"Conta bloqueada. Tente novamente em {15 - int(tempo_bloqueio.total_seconds() / 60)} minutos"
                )
            else:
                # Desbloquear após 15 minutos
                cursor.execute(
                    "UPDATE funcionarios SET bloqueado = FALSE, tentativas_login = 0 WHERE username = %s",
                    (username,)
                )
                conn.commit()
        
        if not verificar_palavra_passe(password, funcionario['senha']):
            # Incrementar tentativas
            tentativas = funcionario['tentativas_login'] + 1
            if tentativas >= 5:
                cursor.execute(
                    "UPDATE funcionarios SET bloqueado = TRUE, data_bloqueio = CURRENT_TIMESTAMP, tentativas_login = %s WHERE username = %s",
                    (tentativas, username)
                )
                conn.commit()
                raise HTTPException(
                    status_code=429,
                    detail="Muitas tentativas falhadas. Conta bloqueada por 15 minutos"
                )
            else:
                cursor.execute(
                    "UPDATE funcionarios SET tentativas_login = %s WHERE username = %s",
                    (tentativas, username)
                )
                conn.commit()
            return False
        
        # Login bem-sucedido - resetar tentativas
        cursor.execute(
            "UPDATE funcionarios SET ultimo_login = CURRENT_TIMESTAMP, tentativas_login = 0 WHERE username = %s",
            (username,)
        )
        conn.commit()
        
        return funcionario
    finally:
        cursor.close()
        conn.close()
```

---

### 5. **Credenciais de Banco de Dados Expostas**

**Vulnerabilidade:**
- [`DATABASE_URL`](LacosAPI/.env:1) com senha em texto plano
- Senha padrão hardcoded: `"1234"`
- Arquivo `.env` pode vazar

**Impacto:** 🔴 CRÍTICO
- Acesso direto ao banco de dados
- Roubo de todos os dados
- Modificação/destruição de dados

**Solução Simples:**
```bash
# 1. Nunca commitar .env
echo ".env" >> .gitignore

# 2. Usar senha forte no PostgreSQL
sudo -u postgres psql
ALTER USER postgres WITH PASSWORD 'SenhaForte@2024!MinhaEmpresa';

# 3. Atualizar .env
DATABASE_URL=postgresql://postgres:SenhaForte@2024!MinhaEmpresa@localhost:5432/MasterLacosMicrocredito

# 4. Restringir acesso ao .env
chmod 600 .env
```

**Solução Produção (usando AWS Secrets Manager ou similar):**
```python
# app/database/database.py
import boto3
import json

def get_db_credentials():
    """Buscar credenciais do AWS Secrets Manager"""
    if os.getenv("ENVIRONMENT") == "production":
        client = boto3.client('secretsmanager', region_name='us-east-1')
        secret = client.get_secret_value(SecretId='lacosapi/db')
        return json.loads(secret['SecretString'])
    else:
        # Desenvolvimento: usar .env
        return {
            "host": "localhost",
            "port": "5432",
            "database": "MasterLacosMicrocredito",
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD")
        }

creds = get_db_credentials()
DATABASE_URL = f"postgresql://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['database']}"
```

---

## ⚠️ VULNERABILIDADES ALTAS (Prioridade MÉDIA-ALTA)

### 6. **Sem Logging de Segurança / Auditoria**

**Vulnerabilidade:**
- Nenhum log de tentativas de login
- Sem rastreamento de ações sensíveis
- Impossível investigar incidentes

**Impacto:** 🟠 ALTO
- Não detecta ataques em andamento
- Sem evidências forenses
- Dificulta compliance (LGPD, etc)

**Solução Simples:**
```python
# app/utils/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_security_logging():
    """Configurar logging de segurança"""
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    
    # Handler para arquivo (rotação a cada 10MB, manter 5 backups)
    handler = RotatingFileHandler(
        "logs/security.log",
        maxBytes=10*1024*1024,
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    security_logger.addHandler(handler)
    
    return security_logger

security_log = setup_security_logging()

# Usar em app/utils/auth.py
def autenticar_funcionario(username: str, password: str):
    # ... código existente
    
    if not funcionario:
        security_log.warning(f"Tentativa de login com usuário inexistente: {username}")
        return False
    
    if not verificar_palavra_passe(password, funcionario['senha']):
        security_log.warning(f"Senha incorreta para usuário: {username}")
        return False
    
    security_log.info(f"Login bem-sucedido: {username}")
    # ... continuar
```

**Eventos para Logar:**
- ✅ Tentativas de login (sucesso e falha)
- ✅ Alterações de senha
- ✅ Criação/exclusão de usuários
- ✅ Acesso a dados sensíveis
- ✅ Erros de autenticação/autorização
- ✅ Exportação de dados
- ✅ Modificações em empréstimos/pagamentos

---

### 7. **Token JWT sem Refresh / Expiração Inadequada**

**Vulnerabilidade:**
- Token expira em 30 minutos mas sem mecanismo de refresh
- Usuário precisa fazer login novamente
- Ou token muito longo facilita uso após roubo

**Impacto:** 🟠 ALTO
- Token roubado válido por 30 minutos
- UX ruim (re-login frequente)
- Sem revogação de tokens

**Solução Simples (Refresh Token):**
```python
# app/utils/auth.py
import uuid

# Armazenar refresh tokens em memória (produção: usar Redis)
REFRESH_TOKENS = {}  # {refresh_token: username}

def criar_tokens(username: str):
    """Criar access token (15min) e refresh token (7 dias)"""
    # Access token curto
    access_token = criar_token_acesso(
        data={"sub": username},
        expires_delta=timedelta(minutes=15)
    )
    
    # Refresh token longo
    refresh_token = str(uuid.uuid4())
    REFRESH_TOKENS[refresh_token] = {
        "username": username,
        "expires": datetime.now(timezone.utc) + timedelta(days=7)
    }
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 900  # 15 minutos
    }

# app/routes/auth.py
@router.post("/token")
async def login_para_token_acesso(form_data: OAuth2PasswordRequestForm = Depends()):
    funcionario = autenticar_funcionario(form_data.username, form_data.password)
    if not funcionario:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    return criar_tokens(funcionario['username'])

@router.post("/refresh")
async def refresh_access_token(refresh_token: str):
    """Renovar access token usando refresh token"""
    token_data = REFRESH_TOKENS.get(refresh_token)
    
    if not token_data:
        raise HTTPException(status_code=401, detail="Refresh token inválido")
    
    if datetime.now(timezone.utc) > token_data["expires"]:
        del REFRESH_TOKENS[refresh_token]
        raise HTTPException(status_code=401, detail="Refresh token expirado")
    
    # Criar novo access token
    access_token = criar_token_acesso(
        data={"sub": token_data["username"]},
        expires_delta=timedelta(minutes=15)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 900
    }

@router.post("/logout")
async def logout(refresh_token: str):
    """Revogar refresh token"""
    if refresh_token in REFRESH_TOKENS:
        del REFRESH_TOKENS[refresh_token]
    return {"mensagem": "Logout realizado com sucesso"}
```

---

### 8. **Sem RBAC (Role-Based Access Control) Completo**

**Vulnerabilidade:**
- Campo [`nivel_acesso`](LacosAPI/app/database/database.py:44) existe mas não é verificado
- Todos os funcionários autenticados têm acesso total
- Sem separação de privilégios

**Impacto:** 🟠 ALTO
- Consultor pode excluir empréstimos
- Operador pode criar/excluir funcionários
- Violação do princípio do menor privilégio

**Solução Simples:**
```python
# app/utils/auth.py
from functools import wraps

def require_role(required_roles: List[str]):
    """Decorator para verificar nível de acesso"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, funcionario_atual: dict = None, **kwargs):
            if funcionario_atual is None:
                raise HTTPException(status_code=401, detail="Não autenticado")
            
            if funcionario_atual['nivel_acesso'] not in required_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Acesso negado. Requer: {', '.join(required_roles)}"
                )
            
            return await func(*args, funcionario_atual=funcionario_atual, **kwargs)
        return wrapper
    return decorator

# Usar nos endpoints:
# app/routes/clientes.py
@router.delete("/remover/{cliente_id}")
@require_role(["Administrador", "Gestor"])  # Apenas admin e gestor podem excluir
def remover_cliente(
    cliente_id: int,
    funcionario_atual: dict = Depends(get_current_funcionario)
):
    # ... código existente

# app/routes/funcionarios.py
@router.post("/criar")
@require_role(["Administrador"])  # Apenas admin pode criar funcionários
def criar_funcionario(
    funcionario: Funcionario,
    funcionario_atual: dict = Depends(get_current_funcionario)
):
    # ... código existente
```

**Hierarquia de Permissões:**
- **Administrador**: Acesso total
- **Gestor**: Gerenciar clientes, empréstimos, relatórios (sem criar funcionários)
- **Operador**: Criar clientes, registrar pagamentos (sem exclusões)
- **Consultor**: Apenas leitura

---

### 9. **Documentação Swagger Aberta Publicamente**

**Vulnerabilidade:**
- Swagger UI (`/docs`) acessível sem autenticação
- Revela estrutura completa da API
- Facilita reconhecimento para ataques

**Impacto:** 🟠 ALTO  
- Atacante conhece todos os endpoints
- Vê schemas de dados
- Descobre parâmetros vulneráveis

**Solução Simples:**
```python
# main.py
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

# Desabilitar docs em produção
if os.getenv("ENVIRONMENT") == "production":
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
else:
    app = FastAPI(title="Lacos Microcrédito API")

# Ou proteger com autenticação básica
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def check_docs_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "docs")
    correct_password = secrets.compare_digest(credentials.password, os.getenv("DOCS_PASSWORD", "changeme"))
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(username: str = Depends(check_docs_credentials)):
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
    )
```

---

### 10. **Sem Connection Pooling (Risco de DoS)**

**Vulnerabilidade:**
- [`get_db_connection()`](LacosAPI/app/database/database.py:12) cria nova conexão a cada requisição
- Sem limite de conexões
- Recursos não reutilizados

**Impacto:** 🟠 ALTO
- DoS por esgotamento de conexões
- Performance degradada
- Custos de recursos elevados

**Solução Simples (com psycopg2.pool):**
```python
# app/database/database.py
from psycopg2 import pool
import threading

# Criar pool de conexões (thread-safe)
connection_pool = None
pool_lock = threading.Lock()

def init_connection_pool(minconn=1, maxconn=20):
    """Inicializar pool de conexões"""
    global connection_pool
    with pool_lock:
        if connection_pool is None:
            connection_pool = pool.ThreadedConnectionPool(
                minconn,
                maxconn,
                DATABASE_URL
            )
    return connection_pool

def get_db_connection():
    """Obter conexão do pool"""
    if connection_pool is None:
        init_connection_pool()
    
    conn = connection_pool.getconn()
    conn.set_client_encoding('UTF8')
    return conn

def release_db_connection(conn):
    """Devolver conexão ao pool"""
    if connection_pool is not None:
        connection_pool.putconn(conn)

# Usar nos endpoints:
# app/routes/clientes.py
@router.get("/listar")
def listar_clientes(...):
    conn = get_db_connection()
    try:
        # ... código existente
    finally:
        release_db_connection(conn)  # Devolver ao pool
```

---

## ⚠️ VULNERABILIDADES MÉDIAS (Prioridade MÉDIA)

### 11. **Sem Validação de Input Completa**

**Vulnerabilidade:**
- Campos como `telefone`, `email` não são validados rigorosamente
- Sem sanitização de strings
- Possível injeção de dados malformados

**Impacto:** 🟡 MÉDIO
- Dados inconsistentes no banco
- Possível XSS armazenado
- Dificuldade em processar dados

**Solução Simples:**
```python
# app/schemas/cliente.py
from pydantic import BaseModel, EmailStr, field_validator
import re

class Cliente(BaseModel):
    nome: str
    sexo: str
    telefone: str
    email: EmailStr | None = None  # Validação automática de email
    
    @field_validator('nome')
    @classmethod
    def validar_nome(cls, v):
        if len(v) < 3:
            raise ValueError('Nome deve ter pelo menos 3 caracteres')
        if len(v) > 200:
            raise ValueError('Nome muito longo')
        # Remover caracteres perigosos
        v = re.sub(r'[<>{}]', '', v)
        return v.strip()
    
    @field_validator('telefone')
    @classmethod
    def validar_telefone(cls, v):
        # Aceitar apenas números e alguns caracteres
        cleaned = re.sub(r'[^\d\+\-\(\)\s]', '', v)
        if len(cleaned) < 9:
            raise ValueError('Telefone inválido')
        return cleaned
    
    @field_validator('sexo')
    @classmethod
    def validar_sexo(cls, v):
        allowed = ['Masculino', 'Feminino', 'Outro']
        if v not in allowed:
            raise ValueError(f'Sexo deve ser um de: {allowed}')
        return v
```

---

### 12. **Exposição de Informações Sensíveis em Erros**

**Vulnerabilidade:**
- Tracebacks completos expostos ao cliente
- Mensagens de erro revelam estrutura interna
- Exemplo: [`"Erro interno do servidor: {str(e)}"`](LacosAPI/app/routes/pagamentos.py:113)

**Impacto:** 🟡 MÉDIO
- Revela caminhos de arquivos
- Mostra estrutura do banco de dados
- Facilita ataques direcionados

**Solução Simples:**
```python
# main.py
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceptions não tratadas"""
    # Logar erro completo internamente
    logger.error(f"Erro não tratado: {request.url}")
    logger.error(traceback.format_exc())
    
    # Retornar mensagem genérica ao cliente
    if os.getenv("ENVIRONMENT") == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor. Contacte o suporte."}
        )
    else:
        # Desenvolvimento: mostrar erro completo
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "traceback": traceback.format_exc()}
        )
```

---

### 13. **Sem Headers de Segurança**

**Vulnerabilidade:**
- Sem `Content-Security-Policy`
- Sem `X-Frame-Options`
- Sem `X-Content-Type-Options`
- Sem `Strict-Transport-Security` (HSTS)

**Impacto:** 🟡 MÉDIO
- Vulnerável a clickjacking
- Possível MIME sniffing
- Sem enforce de HTTPS

**Solução Simples:**
```python
# main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "seu-dominio.com", "*.seu-dominio.com"]
)
```

---

### 14. **Cache do Dashboard sem Isolamento**

**Vulnerabilidade:**
- [`_CACHE`](LacosAPI/app/routes/dashboard.py:9) é global e compartilhado
- Sem isolamento por usuário/empresa
- Possível vazamento de dados entre sessões

**Impacto:** 🟡 MÉDIO
- Usuário pode ver dados de outros
- Cache pollution
- Violação de privacidade

**Solução Simples:**
```python
# app/routes/dashboard.py
def _ckey(name: str, params: Dict[str, Any], user_id: int) -> str:
    """Incluir user_id na chave do cache"""
    return f"{user_id}|{name}|" + "|".join(f"{k}={params[k]}" for k in sorted(params))

@router.get("/resumo")
def obter_resumo_dashboard(
    funcionario_atual: dict = Depends(get_current_funcionario),
    use_cache: bool = True,
    refresh: bool = False,
):
    user_id = funcionario_atual['funcionario_id']
    ckey = _ckey("resumo", {}, user_id)  # Incluir user_id
    # ... resto do código
```

---

### 15. **Sem Proteção Contra SQL Injection (Parametrização OK, mas...)**

**Análise:**
- ✅ Código atual usa parametrização corretamente
- ❌ Mas sem prepared statements
- ❌ Queries dinâmicas poderiam ser adicionadas no futuro

**Impacto:** 🟢 BAIXO (atualmente protegido)
- SQL injection improvável com código atual
- Mas vulnerável se modificado incorretamente

**Boas Práticas (manter):**
```python
# ✅ CORRETO (sempre usar):
cursor.execute("SELECT * FROM clientes WHERE cliente_id = %s", (cliente_id,))

# ❌ NUNCA FAZER:
cursor.execute(f"SELECT * FROM clientes WHERE cliente_id = {cliente_id}")
cursor.execute("SELECT * FROM clientes WHERE nome = '" + nome + "'")

# ✅ Para queries dinâmicas, usar whitelist:
ALLOWED_SORT_FIELDS = ['nome', 'data_cadastro', 'cliente_id']
if sort_field not in ALLOWED_SORT_FIELDS:
    raise ValueError("Campo de ordenação inválido")
query = f"SELECT * FROM clientes ORDER BY {sort_field}"
```

---

## 📋 CHECKLIST DE SEGURANÇA PRIORITÁRIO

### Ações Imediatas (Fazer AGORA):
- [ ] Gerar e configurar SECRET_KEY forte (256 bits)
- [ ] Trocar senha do admin padrão
- [ ] Adicionar .env ao .gitignore (verificar se já não foi commitado)
- [ ] Restringir CORS para domínios específicos
- [ ] Trocar senha do PostgreSQL

### Ações Curto Prazo (Esta Semana):
- [ ] Implementar rate limiting (SlowAPI)
- [ ] Adicionar logging de segurança
- [ ] Implementar contador de tentativas de login
- [ ] Adicionar validação de força de senha
- [ ] Configurar headers de segurança

### Ações Médio Prazo (Este Mês):
- [ ] Implementar refresh tokens
- [ ] Adicionar RBAC completo
- [ ] Proteger documentação Swagger
- [ ] Implementar connection pooling
- [ ] Adicionar validação rigorosa de inputs

### Ações Longo Prazo (Este Trimestre):
- [ ] Migrar credenciais para secrets manager
- [ ] Implementar WAF (Web Application Firewall)
- [ ] Configurar SIEM/monitoramento
- [ ] Pen testing externo
- [ ] Auditoria de código profissional

---

## 🛠️ SCRIPT DE CORREÇÕES RÁPIDAS

```bash
#!/bin/bash
# fix_security_quick.sh - Correções rápidas de segurança

echo "=== Correções Rápidas de Segurança - LacosAPI ==="

# 1. Gerar SECRET_KEY forte
echo "1. Gerando SECRET_KEY..."
NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "SECRET_KEY=$NEW_SECRET" >> .env.new
echo "DATABASE_URL=postgresql://postgres:TROQUE_ESTA_SENHA@localhost:5432/MasterLacosMicrocredito" >> .env.new
echo "ALLOWED_ORIGINS=http://localhost:3000" >> .env.new
echo "ENVIRONMENT=development" >> .env.new
echo "✅ .env.new criado. Revise e renomeie para .env"

# 2. Adicionar ao .gitignore
echo "2. Atualizando .gitignore..."
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
echo "logs/" >> .gitignore
echo "*.log" >> .gitignore
echo "✅ .gitignore atualizado"

# 3. Criar diretório de logs
echo "3. Criando diretório de logs..."
mkdir -p logs
chmod 700 logs
echo "✅ Diretório logs/ criado"

# 4. Instalar dependências de segurança
echo "4. Instalando bibliotecas de segurança..."
pip install slowapi==0.1.9
echo "slowapi==0.1.9" >> requirements.txt
echo "✅ SlowAPI instalado"

# 5. Configurar permissões
echo "5. Configurando permissões..."
chmod 600 .env 2>/dev/null || echo "⚠️  .env não encontrado"
chmod 600 .env.new 2>/dev/null
echo "✅ Permissões configuradas"

echo ""
echo "=== PRÓXIMOS PASSOS MANUAIS ==="
echo "1. Revisar e renomear .env.new para .env"
echo "2. Trocar senha do PostgreSQL"
echo "3. Trocar senha do admin via SQL:"
echo "   UPDATE funcionarios SET senha = crypt('SuaNovaSenhaForte123!', gen_salt('bf')) WHERE username = 'admin';"
echo "4. Aplicar patches de código (ver SECURITY_AUDIT.md)"
echo "5. Reiniciar a API"
```

---

## 📚 RECURSOS ADICIONAIS

### Ferramentas Recomendadas:
1. **Bandit** - Análise estática de segurança Python
   ```bash
   pip install bandit
   bandit -r app/
   ```

2. **Safety** - Verifica vulnerabilidades em dependências
   ```bash
   pip install safety
   safety check
   ```

3. **OWASP ZAP** - Teste de penetração automatizado
4. **Fail2Ban** - Proteção contra brute force no servidor
5. **Let's Encrypt** - Certificados SSL gratuitos

### Padrões de Segurança:
- OWASP Top 10
- NIST Cybersecurity Framework
- ISO 27001
- LGPD (Lei Geral de Proteção de Dados)

---

## 🔐 CONCLUSÃO

**Resumo do Risco Atual:**
- 🔴 5 vulnerabilidades CRÍTICAS
- 🟠 5 vulnerabilidades ALTAS
- 🟡 5 vulnerabilidades MÉDIAS

**Prioridade de Correção:**
1. SECRET_KEY e credenciais
2. CORS e rate limiting
3. Logging e RBAC
4. Validações e headers
5. Otimizações e boas práticas

**Tempo Estimado para Correções Básicas:** 2-3 dias de trabalho
**Tempo para Segurança Completa:** 2-3 semanas

A API tem uma base sólida (usa parametrização SQL, bcrypt para senhas, JWT para autenticação), mas precisa de reforços em controles de acesso, monitoramento e configurações de segurança.

**Contacto para Dúvidas:** Equipe de Segurança