from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
import os
import re
from app.database.database import get_db_connection
import psycopg2.extras

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

CHAVE_SECRETA = os.getenv("SECRET_KEY", "chave-secreta-trocar-em-producao")
if not CHAVE_SECRETA or CHAVE_SECRETA in ["chave-secreta-trocar-em-producao", "your-secret-key-change-in-production"] or len(CHAVE_SECRETA) < 32:
    print("ERRO: SECRET_KEY não configurada ou usando valor padrão inseguro!")
    import sys
    sys.exit(1)

ALGORITMO = "HS256"
TOKEN_EXPIRA_MINUTOS = 480  # 8 horas = 8 * 60 = 480 minutos

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

class TokenData:
    def __init__(self, username = None):
        self.username = username

def verificar_palavra_passe(palavra_passe, hash_guardado):
    return pwd_context.verify(palavra_passe, hash_guardado)

def get_password_hash(password):
    return pwd_context.hash(password)

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

def autenticar_funcionario(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM funcionarios WHERE username = %s", (username,))
        funcionario = cursor.fetchone()
        
        if not funcionario:
            return False
        
        if not verificar_palavra_passe(password, funcionario['senha']):
            return False
        
        cursor.execute("UPDATE funcionarios SET ultimo_login = CURRENT_TIMESTAMP WHERE username = %s", (username,))
        conn.commit()
        
        return funcionario
    finally:
        cursor.close()
        conn.close()

def criar_token_acesso(data: dict, expires_delta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    token_jwt = jwt.encode(to_encode, CHAVE_SECRETA, algorithm=ALGORITMO)
    return token_jwt

async def get_current_funcionario(token: str = Depends(oauth2_scheme)):
    credenciais_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, CHAVE_SECRETA, algorithms=[ALGORITMO])
        username: str = payload.get("sub")
        if username is None:
            raise credenciais_exception
        token_data = TokenData(username=username)
    except Exception:
        raise credenciais_exception
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM funcionarios WHERE username = %s", (username,))
        funcionario = cursor.fetchone()
        
        if funcionario is None:
            raise credenciais_exception
        return funcionario
    finally:
        cursor.close()
        conn.close()
