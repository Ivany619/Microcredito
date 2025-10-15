from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.ocupacao import Ocupacao, OcupacaoCriar, OcupacaoAtualizar
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
import psycopg2.extras

router = APIRouter()

@router.post("/criar", response_model=Ocupacao)
def criar_ocupacao(ocupacao: OcupacaoCriar, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute(
            """INSERT INTO Ocupacoes (cliente_id, codigo, nome, descricao, categoria_risco, 
               renda_minima, setor_economico, estabilidade_emprego, ativo) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
            (ocupacao.cliente_id, ocupacao.codigo, ocupacao.nome, ocupacao.descricao,
             ocupacao.categoria_risco, ocupacao.renda_minima, ocupacao.setor_economico,
             ocupacao.estabilidade_emprego, ocupacao.ativo)
        )
        resultado = cursor.fetchone()
        if resultado is None:
            raise HTTPException(status_code=500, detail="Falha ao criar ocupação")
        conn.commit()
        
        return Ocupacao(**resultado)
    except psycopg2.IntegrityError as e:
        conn.rollback()
        error_msg = str(e).lower()
        if "foreign key constraint" in error_msg:
            if "cliente_id" in error_msg:
                raise HTTPException(status_code=400, detail="Cliente não encontrado - cliente_id inválido")
        raise HTTPException(status_code=400, detail="Erro de integridade de dados")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/listar", response_model=List[Ocupacao])
def listar_ocupacoes(pular: int = 0, limite: int = 100, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM Ocupacoes ORDER BY ocupacao_id DESC LIMIT %s OFFSET %s", (limite, pular))
        ocupacoes = cursor.fetchall()
        return [Ocupacao(**ocupacao) for ocupacao in ocupacoes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar ocupações: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/obter/{ocupacao_id}", response_model=Ocupacao)
def obter_ocupacao(ocupacao_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM Ocupacoes WHERE ocupacao_id = %s", (ocupacao_id,))
        ocupacao = cursor.fetchone()
        if ocupacao is None:
            raise HTTPException(status_code=404, detail="Ocupação não encontrada")
        return Ocupacao(**ocupacao)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar ocupação: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/cliente/{cliente_id}", response_model=List[Ocupacao])
def listar_ocupacoes_por_cliente(cliente_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM Ocupacoes WHERE cliente_id = %s ORDER BY ocupacao_id DESC", (cliente_id,))
        ocupacoes = cursor.fetchall()
        return [Ocupacao(**ocupacao) for ocupacao in ocupacoes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar ocupações: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.put("/atualizar/{ocupacao_id}", response_model=Ocupacao)
def atualizar_ocupacao(ocupacao_id: int, ocupacao: OcupacaoAtualizar, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        campos = []
        valores = []
        
        if ocupacao.codigo is not None:
            campos.append("codigo = %s")
            valores.append(ocupacao.codigo)
        
        if ocupacao.nome is not None:
            campos.append("nome = %s")
            valores.append(ocupacao.nome)
        
        if ocupacao.descricao is not None:
            campos.append("descricao = %s")
            valores.append(ocupacao.descricao)
        
        if ocupacao.categoria_risco is not None:
            campos.append("categoria_risco = %s")
            valores.append(ocupacao.categoria_risco)
        
        if ocupacao.renda_minima is not None:
            campos.append("renda_minima = %s")
            valores.append(ocupacao.renda_minima)
        
        if ocupacao.setor_economico is not None:
            campos.append("setor_economico = %s")
            valores.append(ocupacao.setor_economico)
        
        if ocupacao.estabilidade_emprego is not None:
            campos.append("estabilidade_emprego = %s")
            valores.append(ocupacao.estabilidade_emprego)
        
        if ocupacao.ativo is not None:
            campos.append("ativo = %s")
            valores.append(ocupacao.ativo)
        
        if not campos:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        valores.append(ocupacao_id)
        
        consulta = f"""
            UPDATE Ocupacoes
            SET {', '.join(campos)}
            WHERE ocupacao_id = %s
            RETURNING *
        """
        
        cursor.execute(consulta, valores)
        ocupacao_atualizada = cursor.fetchone()
        conn.commit()
        
        if ocupacao_atualizada is None:
            raise HTTPException(status_code=404, detail="Ocupação não encontrada")
        
        return Ocupacao(**ocupacao_atualizada)
    except psycopg2.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Erro de integridade de dados")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar ocupação: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/remover/{ocupacao_id}")
def remover_ocupacao(ocupacao_id: int, funcionario_atual: dict = Depends(get_current_funcionario)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM Ocupacoes WHERE ocupacao_id = %s", (ocupacao_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ocupação não encontrada")
        
        return {"mensagem": "Ocupação removida com sucesso"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao remover ocupação: {str(e)}")
    finally:
        cursor.close()
        conn.close()