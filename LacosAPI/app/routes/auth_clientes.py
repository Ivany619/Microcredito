from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from app.schemas.autenticacao_cliente import (
    AutenticacaoCliente, AutenticacaoClienteCriar, AutenticacaoClienteAtualizar,
    LoginClienteRequest, LoginClienteResponse
)
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
import psycopg2.extras
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
security = HTTPBearer()

SECRET_KEY_CLIENTE = os.getenv("SECRET_KEY_CLIENTE", "cliente_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token_cliente(data: dict, expires_delta: timedelta = None):
    """Create JWT token for client"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY_CLIENTE, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_cliente(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated client"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY_CLIENTE, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        cliente_id: int = payload.get("cliente_id")
        if username is None or cliente_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"username": username, "cliente_id": cliente_id}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.post("/criar", response_model=AutenticacaoCliente)
def criar_autenticacao_cliente(auth: AutenticacaoClienteCriar, funcionario_atual: dict = Depends(get_current_funcionario)):
    """Create client authentication (only employees can create client accounts)"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        password_hash = hash_password(auth.password)
        
        cursor.execute(
            """INSERT INTO Autenticacao_Clientes (cliente_id, username, password_hash) 
               VALUES (%s, %s, %s) RETURNING *""",
            (auth.cliente_id, auth.username, password_hash)
        )
        resultado = cursor.fetchone()
        if resultado is None:
            raise HTTPException(status_code=500, detail="Falha ao criar autenticação do cliente")
        conn.commit()
        
        return AutenticacaoCliente(**resultado)
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "unique constraint" in str(e).lower():
            if "username" in str(e).lower():
                raise HTTPException(status_code=400, detail="Username já existe")
        elif "foreign key constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="cliente_id inválido")
        raise HTTPException(status_code=400, detail="Erro de integridade de dados")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/login", response_model=LoginClienteResponse)
def login_cliente(login_data: LoginClienteRequest):
    """Client login endpoint"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Get client authentication data
        cursor.execute(
            "SELECT * FROM Autenticacao_Clientes WHERE username = %s",
            (login_data.username,)
        )
        auth_cliente = cursor.fetchone()
        
        if not auth_cliente:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
        # Check if account is blocked
        if auth_cliente['bloqueado']:
            raise HTTPException(status_code=401, detail="Conta bloqueada. Contacte o suporte.")
        
        # Verify password
        if not verify_password(login_data.password, auth_cliente['password_hash']):
            # Increment login attempts
            cursor.execute(
                """UPDATE Autenticacao_Clientes 
                   SET tentativas_login = tentativas_login + 1,
                       bloqueado = CASE WHEN tentativas_login + 1 >= 5 THEN TRUE ELSE FALSE END,
                       data_bloqueio = CASE WHEN tentativas_login + 1 >= 5 THEN CURRENT_TIMESTAMP ELSE data_bloqueio END
                   WHERE autenticacao_id = %s""",
                (auth_cliente['autenticacao_id'],)
            )
            conn.commit()
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
        # Reset login attempts and update last login
        cursor.execute(
            """UPDATE Autenticacao_Clientes 
               SET tentativas_login = 0, ultimo_login = CURRENT_TIMESTAMP
               WHERE autenticacao_id = %s""",
            (auth_cliente['autenticacao_id'],)
        )
        conn.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token_cliente(
            data={"sub": auth_cliente['username'], "cliente_id": auth_cliente['cliente_id']},
            expires_delta=access_token_expires
        )
        
        return LoginClienteResponse(
            access_token=access_token,
            token_type="bearer",
            cliente_id=auth_cliente['cliente_id'],
            username=auth_cliente['username']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/listar", response_model=List[AutenticacaoCliente])
def listar_autenticacoes_clientes(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    """List all client authentications (only employees can access)"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM Autenticacao_Clientes ORDER BY autenticacao_id DESC LIMIT %s OFFSET %s", (limite, pular))
        auths = cursor.fetchall()
        return [AutenticacaoCliente(**auth) for auth in auths]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar autenticações: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.put("/atualizar/{autenticacao_id}", response_model=AutenticacaoCliente)
def atualizar_autenticacao_cliente(autenticacao_id: int, auth: AutenticacaoClienteAtualizar, funcionario_atual: dict = Depends(get_current_funcionario)):
    """Update client authentication (only employees can update)"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        campos = []
        valores = []
        
        if auth.password is not None:
            campos.append("password_hash = %s")
            valores.append(hash_password(auth.password))
        
        if auth.tentativas_login is not None:
            campos.append("tentativas_login = %s")
            valores.append(auth.tentativas_login)
        
        if auth.bloqueado is not None:
            campos.append("bloqueado = %s")
            valores.append(auth.bloqueado)
            if not auth.bloqueado:  # If unblocking, reset attempts
                campos.append("tentativas_login = %s")
                valores.append(0)
                campos.append("data_bloqueio = %s")
                valores.append(None)
        
        if auth.data_bloqueio is not None:
            campos.append("data_bloqueio = %s")
            valores.append(auth.data_bloqueio)
        
        if not campos:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        valores.append(autenticacao_id)
        
        consulta = f"""
            UPDATE Autenticacao_Clientes
            SET {', '.join(campos)}
            WHERE autenticacao_id = %s
            RETURNING *
        """
        
        cursor.execute(consulta, valores)
        auth_atualizada = cursor.fetchone()
        conn.commit()
        
        if auth_atualizada is None:
            raise HTTPException(status_code=404, detail="Autenticação não encontrada")
        
        return AutenticacaoCliente(**auth_atualizada)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar autenticação: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{autenticacao_id}")
def remover_autenticacao_cliente(autenticacao_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    """Remove client authentication (only employees can remove)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM Autenticacao_Clientes WHERE autenticacao_id = %s", (autenticacao_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Autenticação não encontrada")
        
        return {"mensagem": "Autenticação removida com sucesso"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao remover autenticação: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/perfil")
def obter_perfil_cliente(cliente_atual: dict = Depends(get_current_cliente)):
    """Get current client profile"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            """SELECT c.*, ac.username, ac.ultimo_login 
               FROM clientes c 
               JOIN Autenticacao_Clientes ac ON c.cliente_id = ac.cliente_id 
               WHERE c.cliente_id = %s""",
            (cliente_atual['cliente_id'],)
        )
        cliente = cursor.fetchone()
        
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        return dict(cliente)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter perfil: {str(e)}")
    finally:
        cursor.close()
        conn.close()