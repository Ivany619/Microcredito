from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.funcionario import Funcionario, FuncionarioCreate, FuncionarioUpdate, FuncionarioResponse
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario, get_password_hash
import psycopg2.extras
from datetime import datetime

router = APIRouter()

@router.post("/criar", response_model=FuncionarioResponse)
def criar_funcionario(funcionario: FuncionarioCreate, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        hashed_password = get_password_hash(funcionario.senha)
        
        cursor.execute(
            """INSERT INTO funcionarios 
               (username, senha, nome_completo, email, telefone, nivel_acesso, ativo, tentativas_login, bloqueado) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
               RETURNING funcionario_id, username, nome_completo, email, telefone, nivel_acesso, 
                         data_cadastro, ultimo_login, ativo, tentativas_login, bloqueado, data_bloqueio""",
            (funcionario.username, hashed_password, funcionario.nome_completo, funcionario.email,
             funcionario.telefone, funcionario.nivel_acesso, funcionario.ativo, 
             funcionario.tentativas_login, funcionario.bloqueado)
        )
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Falha ao criar funcionário")
        conn.commit()
        
        return FuncionarioResponse(**result)
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "unique constraint" in str(e).lower():
            if "username" in str(e).lower():
                raise HTTPException(status_code=400, detail="Nome de utilizador já existe")
            elif "email" in str(e).lower():
                raise HTTPException(status_code=400, detail="Email já existe")
        raise HTTPException(status_code=400, detail="Erro de integridade de dados")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/listar", response_model=List[FuncionarioResponse])
def listar_funcionarios(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT funcionario_id, username, nome_completo, email, telefone, nivel_acesso, 
                   data_cadastro, ultimo_login, ativo, tentativas_login, bloqueado, data_bloqueio 
            FROM funcionarios 
            LIMIT %s OFFSET %s
        """, (limite, pular))
        funcionarios = cursor.fetchall()
        return [FuncionarioResponse(**funcionario) for funcionario in funcionarios]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar funcionários: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/obter/{funcionario_id}", response_model=FuncionarioResponse)
def obter_funcionario(funcionario_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT funcionario_id, username, nome_completo, email, telefone, nivel_acesso, 
                   data_cadastro, ultimo_login, ativo, tentativas_login, bloqueado, data_bloqueio 
            FROM funcionarios 
            WHERE funcionario_id = %s
        """, (funcionario_id,))
        funcionario = cursor.fetchone()
        
        if funcionario is None:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        
        return FuncionarioResponse(**funcionario)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar funcionário: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.put("/atualizar/{funcionario_id}", response_model=FuncionarioResponse)
def atualizar_funcionario(funcionario_id: int, funcionario: FuncionarioUpdate, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        update_fields = []
        update_values = []
        
        if funcionario.username is not None:
            update_fields.append("username = %s")
            update_values.append(funcionario.username)
        
        if funcionario.senha is not None:
            update_fields.append("senha = %s")
            update_values.append(get_password_hash(funcionario.senha))
        
        if funcionario.nome_completo is not None:
            update_fields.append("nome_completo = %s")
            update_values.append(funcionario.nome_completo)
        
        if funcionario.email is not None:
            update_fields.append("email = %s")
            update_values.append(funcionario.email)
        
        if funcionario.telefone is not None:
            update_fields.append("telefone = %s")
            update_values.append(funcionario.telefone)
        
        if funcionario.nivel_acesso is not None:
            update_fields.append("nivel_acesso = %s")
            update_values.append(funcionario.nivel_acesso)
        
        if funcionario.ativo is not None:
            update_fields.append("ativo = %s")
            update_values.append(funcionario.ativo)
        
        if funcionario.tentativas_login is not None:
            update_fields.append("tentativas_login = %s")
            update_values.append(funcionario.tentativas_login)
        
        if funcionario.bloqueado is not None:
            update_fields.append("bloqueado = %s")
            update_values.append(funcionario.bloqueado)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        update_values.append(funcionario_id)
        
        query = f"""
            UPDATE funcionarios 
            SET {', '.join(update_fields)}
            WHERE funcionario_id = %s 
            RETURNING funcionario_id, username, nome_completo, email, telefone, nivel_acesso, 
                      data_cadastro, ultimo_login, ativo, tentativas_login, bloqueado, data_bloqueio
        """
        
        cursor.execute(query, update_values)
        funcionario_atualizado = cursor.fetchone()
        conn.commit()
        
        if funcionario_atualizado is None:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        
        return FuncionarioResponse(**funcionario_atualizado)
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "unique constraint" in str(e).lower():
            if "username" in str(e).lower():
                raise HTTPException(status_code=400, detail="Nome de utilizador já existe")
            elif "email" in str(e).lower():
                raise HTTPException(status_code=400, detail="Email já existe")
        raise HTTPException(status_code=400, detail="Erro de integridade de dados")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{funcionario_id}")
def remover_funcionario(funcionario_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if funcionario_atual['funcionario_id'] == funcionario_id:
            raise HTTPException(status_code=400, detail="Não pode eliminar a sua própria conta")
        
        cursor.execute("DELETE FROM funcionarios WHERE funcionario_id = %s", (funcionario_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        
        return {"mensagem": "Funcionário removido com sucesso"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao remover funcionário: {str(e)}")
    finally:
        cursor.close()
        conn.close()