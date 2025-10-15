
from fastapi import APIRouter, Depends, HTTPException, Query
from app.database.database import get_db_connection
from app.utils.auth import get_current_funcionario
import psycopg2.extras
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Dict, Any, List
import os
import time

# Cache simples em memória para aliviar consultas pesadas
CACHE_TTL = int(os.getenv("DASHBOARD_CACHE_TTL", "300"))  # segundos (default 5min)
_CACHE: Dict[str, Dict[str, Any]] = {}  # key -> {"data":..., "ts": float}


def _ckey(name: str, params: Dict[str, Any]) -> str:
    return name + "|" + "|".join(f"{k}={params[k]}" for k in sorted(params))


def _cget(key: str):
    entry = _CACHE.get(key)
    if not entry:
        return None
    if time.time() - entry["ts"] > CACHE_TTL:
        _CACHE.pop(key, None)
        return None
    return entry["data"]


def _cset(key: str, data: Any):
    _CACHE[key] = {"data": data, "ts": time.time()}


def _to_float(x) -> float:
    try:
        if isinstance(x, Decimal):
            return float(x)
        return float(x)
    except Exception:
        return 0.0


def _to_iso(dt) -> str:
    try:
        return dt.isoformat()
    except Exception:
        return str(dt)


router = APIRouter()


@router.post("/rebuild-cache")
def rebuild_cache(funcionario_atual: dict = Depends(get_current_funcionario)):
    """
    Limpa o cache e prepara para nova reconstrução automática.
    """
    _CACHE.clear()
    return {"mensagem": "Cache limpo", "ttl_segundos": CACHE_TTL}


@router.get("/resumo")
def obter_resumo_dashboard(
    funcionario_atual: dict = Depends(get_current_funcionario),
    use_cache: bool = Query(True, description="Usar cache de 5min para acelerar respostas"),
    refresh: bool = Query(False, description="Ignora o cache e recalcula imediatamente"),
):
    """
    Endpoint de resumo para o dashboard administrativo.
    Retorna KPIs principais do mês corrente e totais gerais, com cache opcional.
    """
    ckey = _ckey("resumo", {})
    if use_cache and not refresh:
        cached = _cget(ckey)
        if cached is not None:
            return cached

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        # Totais de clientes
        cursor.execute("SELECT COUNT(*) AS total FROM clientes")
        total_clientes = int(cursor.fetchone()["total"])

        # Totais de empréstimos
        cursor.execute("SELECT COUNT(*) AS total FROM emprestimos")
        total_emprestimos = int(cursor.fetchone()["total"])

        cursor.execute("SELECT COUNT(*) AS total FROM emprestimos WHERE status = 'Ativo'")
        emprestimos_ativos = int(cursor.fetchone()["total"])

        cursor.execute("SELECT COUNT(*) AS total FROM emprestimos WHERE status = 'Pago'")
        emprestimos_pagos = int(cursor.fetchone()["total"])

        cursor.execute("SELECT COUNT(*) AS total FROM emprestimos WHERE status = 'Inadimplente'")
        emprestimos_inadimplentes = int(cursor.fetchone()["total"])

        # Empréstimos vencidos (atrasados) ainda ativos
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM emprestimos
            WHERE status = 'Ativo' AND DATE(data_vencimento) < CURRENT_DATE
        """)
        emprestimos_vencidos = int(cursor.fetchone()["total"])

        # Valor emprestado no mês corrente
        cursor.execute("""
            SELECT COALESCE(SUM(valor), 0) AS total
            FROM emprestimos
            WHERE date_trunc('month', data_emprestimo) = date_trunc('month', CURRENT_DATE)
        """)
        total_valor_emprestado_mes = _to_float(cursor.fetchone()["total"])

        # Total pago no mês corrente
        cursor.execute("""
            SELECT COALESCE(SUM(valor_pago), 0) AS total
            FROM pagamentos
            WHERE date_trunc('month', data_pagamento) = date_trunc('month', CURRENT_DATE)
        """)
        total_pago_mes = _to_float(cursor.fetchone()["total"])

        # Total de penalizações aplicadas no mês corrente
        cursor.execute("""
            SELECT COALESCE(SUM(valor), 0) AS total
            FROM penalizacoes
            WHERE date_trunc('month', data_aplicacao) = date_trunc('month', CURRENT_DATE)
        """)
        total_penalizacoes_mes = _to_float(cursor.fetchone()["total"])

        recebimentos_mes = _to_float(total_pago_mes + total_penalizacoes_mes)

        # Saldo em aberto (apenas empréstimos Ativos): soma do max(valor*1.20 - total_pago, 0)
        cursor.execute("""
            SELECT COALESCE(SUM(GREATEST(e.valor * 1.20 - COALESCE(p.total_pago, 0), 0)), 0) AS saldo
            FROM emprestimos e
            LEFT JOIN (
                SELECT emprestimo_id, SUM(valor_pago) AS total_pago
                FROM pagamentos
                GROUP BY emprestimo_id
            ) p ON p.emprestimo_id = e.emprestimo_id
            WHERE e.status = 'Ativo'
        """)
        saldo_em_aberto = _to_float(cursor.fetchone()["saldo"])

        # Média de dias de atraso (empréstimos ativos e vencidos)
        cursor.execute("""
            SELECT COALESCE(AVG((CURRENT_DATE - DATE(data_vencimento))), 0) AS media
            FROM emprestimos
            WHERE status = 'Ativo' AND DATE(data_vencimento) < CURRENT_DATE
        """)
        media_dias_atraso = _to_float(cursor.fetchone()["media"])

        # Taxa de inadimplência (vencidos / ativos)
        taxa_inadimplencia = _to_float((emprestimos_vencidos / emprestimos_ativos) * 100) if emprestimos_ativos > 0 else 0.0

        # Clientes novos no mês corrente
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM clientes
            WHERE date_trunc('month', data_cadastro) = date_trunc('month', CURRENT_DATE)
        """)
        clientes_novos_mes = int(cursor.fetchone()["total"])

        # Notificações pendentes
        cursor.execute("SELECT COUNT(*) AS total FROM notificacoes WHERE status = 'Pendente'")
        notificacoes_pendentes = int(cursor.fetchone()["total"])

        # Distribuição de pagamentos por método (mês corrente)
        cursor.execute("""
            SELECT metodo_pagamento, COALESCE(SUM(valor_pago),0) AS total
            FROM pagamentos
            WHERE date_trunc('month', data_pagamento) = date_trunc('month', CURRENT_DATE)
            GROUP BY metodo_pagamento
        """)
        dist_rows = cursor.fetchall()
        distribuicao_pagamentos_mes = {row["metodo_pagamento"]: _to_float(row["total"]) for row in dist_rows}

        # Período de referência textual (mês atual)
        periodo_referencia = datetime.now(timezone.utc).strftime("%Y-%m")

        result = {
            "periodo_referencia": periodo_referencia,
            "clientes": {
                "total": total_clientes,
                "novos_no_mes": clientes_novos_mes
            },
            "emprestimos": {
                "total": total_emprestimos,
                "ativos": emprestimos_ativos,
                "pagos": emprestimos_pagos,
                "inadimplentes": emprestimos_inadimplentes,
                "vencidos_ativos": emprestimos_vencidos,
                "media_dias_atraso": media_dias_atraso,
                "taxa_inadimplencia_percent": taxa_inadimplencia
            },
            "movimento_mes": {
                "valor_emprestado": total_valor_emprestado_mes,
                "total_pago": total_pago_mes,
                "total_penalizacoes": total_penalizacoes_mes,
                "recebimentos": recebimentos_mes,
                "distribuicao_pagamentos_por_metodo": distribuicao_pagamentos_mes
            },
            "financeiro": {
                "saldo_em_aberto_estimado": saldo_em_aberto
            },
            "notificacoes": {
                "pendentes": notificacoes_pendentes
            }
        }
        if use_cache:
            _cset(ckey, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular resumo do dashboard: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.get("/trends")
def obter_trends(
    months: int = Query(6, ge=1, le=36, description="Número de meses anteriores (máx 36)"),
    funcionario_atual: dict = Depends(get_current_funcionario),
    use_cache: bool = Query(True),
    refresh: bool = Query(False),
):
    """
    Séries mensais: valor emprestado, total pago, penalizações e clientes novos.
    """
    months = max(1, min(36, int(months)))
    ckey = _ckey("trends", {"months": months})
    if use_cache and not refresh:
        cached = _cget(ckey)
        if cached is not None:
            return cached

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("""
            WITH series AS (
                SELECT generate_series(
                    date_trunc('month', CURRENT_DATE) - (INTERVAL '1 month' * %s) + INTERVAL '1 month',
                    date_trunc('month', CURRENT_DATE),
                    INTERVAL '1 month'
                ) AS m
            ),
            e AS (
                SELECT date_trunc('month', data_emprestimo) AS m, SUM(valor) AS total FROM emprestimos GROUP BY 1
            ),
            p AS (
                SELECT date_trunc('month', data_pagamento) AS m, SUM(valor_pago) AS total FROM pagamentos GROUP BY 1
            ),
            x AS (
                SELECT date_trunc('month', data_aplicacao) AS m, SUM(valor) AS total FROM penalizacoes GROUP BY 1
            ),
            c AS (
                SELECT date_trunc('month', data_cadastro) AS m, COUNT(*) AS total FROM clientes GROUP BY 1
            )
            SELECT
                to_char(s.m, 'YYYY-MM') AS ym,
                COALESCE(e.total, 0) AS valor_emprestado,
                COALESCE(p.total, 0) AS total_pago,
                COALESCE(x.total, 0) AS total_penalizacoes,
                COALESCE(c.total, 0) AS clientes_novos
            FROM series s
            LEFT JOIN e ON e.m = s.m
            LEFT JOIN p ON p.m = s.m
            LEFT JOIN x ON x.m = s.m
            LEFT JOIN c ON c.m = s.m
            ORDER BY s.m
        """, (months,))
        rows = cursor.fetchall()
        data = [
            {
                "ym": r["ym"],
                "valor_emprestado": _to_float(r["valor_emprestado"]),
                "total_pago": _to_float(r["total_pago"]),
                "total_penalizacoes": _to_float(r["total_penalizacoes"]),
                "clientes_novos": int(r["clientes_novos"]),
            }
            for r in rows
        ]
        if use_cache:
            _cset(ckey, data)
        return {"months": months, "series": data}
    finally:
        cursor.close()
        conn.close()


@router.get("/aging")
def obter_aging(
    funcionario_atual: dict = Depends(get_current_funcionario),
    use_cache: bool = Query(True),
    refresh: bool = Query(False),
):
    """
    Envelhecimento da dívida (saldo em aberto) por faixas de atraso.
    Buckets: 1-30, 31-60, 61-90, 90+ dias.
    """
    ckey = _ckey("aging", {})
    if use_cache and not refresh:
        cached = _cget(ckey)
        if cached is not None:
            return cached

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("""
            WITH pagos AS (
              SELECT emprestimo_id, COALESCE(SUM(valor_pago),0) AS total_pago
              FROM pagamentos
              GROUP BY emprestimo_id
            ),
            ativos AS (
              SELECT e.emprestimo_id, e.valor, e.data_vencimento, COALESCE(p.total_pago,0) AS total_pago
              FROM emprestimos e
              LEFT JOIN pagos p ON p.emprestimo_id = e.emprestimo_id
              WHERE e.status = 'Ativo'
            ),
            calc AS (
              SELECT
                GREATEST(a.valor * 1.20 - a.total_pago, 0) AS saldo,
                (CURRENT_DATE - DATE(a.data_vencimento))::int AS dias
              FROM ativos a
              WHERE DATE(a.data_vencimento) < CURRENT_DATE
            )
            SELECT
              COALESCE(SUM(CASE WHEN dias BETWEEN 1 AND 30 THEN saldo ELSE 0 END),0) AS b0_30,
              COALESCE(SUM(CASE WHEN dias BETWEEN 31 AND 60 THEN saldo ELSE 0 END),0) AS b31_60,
              COALESCE(SUM(CASE WHEN dias BETWEEN 61 AND 90 THEN saldo ELSE 0 END),0) AS b61_90,
              COALESCE(SUM(CASE WHEN dias > 90 THEN saldo ELSE 0 END),0) AS b90_plus,
              COALESCE(COUNT(CASE WHEN dias BETWEEN 1 AND 30 THEN 1 END),0) AS c0_30,
              COALESCE(COUNT(CASE WHEN dias BETWEEN 31 AND 60 THEN 1 END),0) AS c31_60,
              COALESCE(COUNT(CASE WHEN dias BETWEEN 61 AND 90 THEN 1 END),0) AS c61_90,
              COALESCE(COUNT(CASE WHEN dias > 90 THEN 1 END),0) AS c90_plus
            FROM calc
        """)
        r = cursor.fetchone() or {}
        data = {
            "buckets": {
                "valor": {
                    "b0_30": _to_float(r.get("b0_30", 0)),
                    "b31_60": _to_float(r.get("b31_60", 0)),
                    "b61_90": _to_float(r.get("b61_90", 0)),
                    "b90_plus": _to_float(r.get("b90_plus", 0)),
                },
                "qtd_emprestimos": {
                    "b0_30": int(r.get("c0_30", 0) or 0),
                    "b31_60": int(r.get("c31_60", 0) or 0),
                    "b61_90": int(r.get("c61_90", 0) or 0),
                    "b90_plus": int(r.get("c90_plus", 0) or 0),
                }
            }
        }
        if use_cache:
            _cset(ckey, data)
        return data
    finally:
        cursor.close()
        conn.close()


@router.get("/top-clientes")
def obter_top_clientes(
    metric: str = Query("saldo", pattern="^(saldo|atraso|pagos_mes)$", description="Métrica: saldo | atraso | pagos_mes"),
    limit: int = Query(10, ge=1, le=50),
    funcionario_atual: dict = Depends(get_current_funcionario),
    use_cache: bool = Query(True),
    refresh: bool = Query(False),
):
    """
    Top clientes por:
      - saldo: maior saldo em aberto (empréstimos ativos)
      - atraso: maior número de dias de atraso (empréstimos ativos vencidos)
      - pagos_mes: maior total pago no mês corrente
    """
    metric = metric or "saldo"
    ckey = _ckey("top-clientes", {"metric": metric, "limit": limit})
    if use_cache and not refresh:
        cached = _cget(ckey)
        if cached is not None:
            return cached

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        if metric == "saldo":
            cursor.execute("""
                WITH pagos AS (
                  SELECT emprestimo_id, COALESCE(SUM(valor_pago),0) AS total_pago
                  FROM pagamentos
                  GROUP BY emprestimo_id
                ),
                ativos AS (
                  SELECT e.emprestimo_id, e.cliente_id, e.valor, COALESCE(p.total_pago,0) AS total_pago
                  FROM emprestimos e
                  LEFT JOIN pagos p ON p.emprestimo_id = e.emprestimo_id
                  WHERE e.status = 'Ativo'
                ),
                by_cliente AS (
                  SELECT cliente_id, GREATEST(SUM(valor * 1.20 - total_pago), 0) AS saldo_em_aberto
                  FROM ativos
                  GROUP BY cliente_id
                )
                SELECT c.cliente_id, c.nome, c.telefone, b.saldo_em_aberto
                FROM by_cliente b
                JOIN clientes c ON c.cliente_id = b.cliente_id
                ORDER BY b.saldo_em_aberto DESC
                LIMIT %s
            """, (limit,))
            rows = cursor.fetchall()
            data = [
                {
                    "cliente_id": r["cliente_id"],
                    "nome": r.get("nome"),
                    "telefone": r.get("telefone"),
                    "saldo_em_aberto": _to_float(r.get("saldo_em_aberto", 0)),
                } for r in rows
            ]
        elif metric == "atraso":
            cursor.execute("""
                SELECT c.cliente_id, c.nome, c.telefone,
                       MAX(GREATEST((CURRENT_DATE - DATE(e.data_vencimento))::int, 0)) AS max_dias_atraso
                FROM clientes c
                JOIN emprestimos e ON e.cliente_id = c.cliente_id
                WHERE e.status = 'Ativo' AND DATE(e.data_vencimento) < CURRENT_DATE
                GROUP BY c.cliente_id, c.nome, c.telefone
                ORDER BY max_dias_atraso DESC
                LIMIT %s
            """, (limit,))
            rows = cursor.fetchall()
            data = [
                {
                    "cliente_id": r["cliente_id"],
                    "nome": r.get("nome"),
                    "telefone": r.get("telefone"),
                    "max_dias_atraso": int(r.get("max_dias_atraso", 0) or 0),
                } for r in rows
            ]
        else:  # pagos_mes
            cursor.execute("""
                SELECT c.cliente_id, c.nome, c.telefone, COALESCE(SUM(p.valor_pago),0) AS total_pago_mes
                FROM clientes c
                JOIN pagamentos p ON p.cliente_id = c.cliente_id
                WHERE date_trunc('month', p.data_pagamento) = date_trunc('month', CURRENT_DATE)
                GROUP BY c.cliente_id, c.nome, c.telefone
                ORDER BY total_pago_mes DESC
                LIMIT %s
            """, (limit,))
            rows = cursor.fetchall()
            data = [
                {
                    "cliente_id": r["cliente_id"],
                    "nome": r.get("nome"),
                    "telefone": r.get("telefone"),
                    "total_pago_mes": _to_float(r.get("total_pago_mes", 0)),
                } for r in rows
            ]

        result = {"metric": metric, "limit": limit, "clientes": data}
        if use_cache:
            _cset(ckey, result)
        return result
    finally:
        cursor.close()
        conn.close()


@router.get("/distribuicoes")
def obter_distribuicoes(
    funcionario_atual: dict = Depends(get_current_funcionario),
    use_cache: bool = Query(True),
    refresh: bool = Query(False),
):
    """
    Distribuições de clientes:
      - sexo
      - nacionalidade
      - ocupações: categoria_risco, setor_economico, estabilidade_emprego (apenas ocupações ativas)
    """
    ckey = _ckey("distribuicoes", {})
    if use_cache and not refresh:
        cached = _cget(ckey)
        if cached is not None:
            return cached

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("SELECT sexo, COUNT(*) AS total FROM clientes GROUP BY sexo")
        sexo_rows = cursor.fetchall()
        sexo = {r["sexo"]: int(r["total"]) for r in sexo_rows if r.get("sexo")}

        cursor.execute("SELECT nacionalidade, COUNT(*) AS total FROM clientes GROUP BY nacionalidade")
        nac_rows = cursor.fetchall()
        nacionalidade = {r["nacionalidade"]: int(r["total"]) for r in nac_rows if r.get("nacionalidade")}

        # Ocupações (ativas)
        cursor.execute("""
            SELECT categoria_risco, COUNT(*) AS total
            FROM ocupacoes
            WHERE ativo = true
            GROUP BY categoria_risco
        """)
        cat_rows = cursor.fetchall()
        categoria_risco = {r["categoria_risco"]: int(r["total"]) for r in cat_rows if r.get("categoria_risco")}

        cursor.execute("""
            SELECT setor_economico, COUNT(*) AS total
            FROM ocupacoes
            WHERE ativo = true
            GROUP BY setor_economico
        """)
        set_rows = cursor.fetchall()
        setor_economico = {r["setor_economico"]: int(r["total"]) for r in set_rows if r.get("setor_economico")}

        cursor.execute("""
            SELECT estabilidade_emprego, COUNT(*) AS total
            FROM ocupacoes
            WHERE ativo = true
            GROUP BY estabilidade_emprego
        """)
        est_rows = cursor.fetchall()
        estabilidade_emprego = {r["estabilidade_emprego"]: int(r["total"]) for r in est_rows if r.get("estabilidade_emprego")}

        result = {
            "clientes": {
                "sexo": sexo,
                "nacionalidade": nacionalidade,
            },
            "ocupacoes_ativas": {
                "categoria_risco": categoria_risco,
                "setor_economico": setor_economico,
                "estabilidade_emprego": estabilidade_emprego,
            }
        }
        if use_cache:
            _cset(ckey, result)
        return result
    finally:
        cursor.close()
        conn.close()


@router.get("/notificacoes-metricas")
def obter_notificacoes_metricas(
    funcionario_atual: dict = Depends(get_current_funcionario),
    use_cache: bool = Query(True),
    refresh: bool = Query(False),
):
    """
    Métricas de notificações:
      - contagem por status (total)
      - contagem por tipo nos últimos 30 dias
    """
    ckey = _ckey("notificacoes-metricas", {})
    if use_cache and not refresh:
        cached = _cget(ckey)
        if cached is not None:
            return cached

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("SELECT status, COUNT(*) AS total FROM notificacoes GROUP BY status")
        by_status = {r["status"]: int(r["total"]) for r in cursor.fetchall() if r.get("status")}

        cursor.execute("""
            SELECT tipo, COUNT(*) AS total
            FROM notificacoes
            WHERE data_envio >= (CURRENT_DATE - INTERVAL '30 days')
            GROUP BY tipo
        """)
        by_tipo_30d = {r["tipo"]: int(r["total"]) for r in cursor.fetchall() if r.get("tipo")}

        result = {
            "by_status_total": by_status,
            "by_tipo_ultimos_30_dias": by_tipo_30d
        }
        if use_cache:
            _cset(ckey, result)
        return result
    finally:
        cursor.close()
        conn.close()


@router.get("/eficiencia-cobranca")
def obter_eficiencia_cobranca(
    months: int = Query(6, ge=1, le=36),
    funcionario_atual: dict = Depends(get_current_funcionario),
    use_cache: bool = Query(True),
    refresh: bool = Query(False),
):
    """
    Eficiência de cobrança por mês:
      - due_mes: soma (valor * 1.20) de empréstimos cujo vencimento cai no mês
      - recebido_mes: pagamentos + penalizações no mês
      - eficiencia_percent = (recebido_mes / due_mes) * 100
    """
    months = max(1, min(36, int(months)))
    ckey = _ckey("eficiencia", {"months": months})
    if use_cache and not refresh:
        cached = _cget(ckey)
        if cached is not None:
            return cached

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("""
            WITH series AS (
                SELECT generate_series(
                    date_trunc('month', CURRENT_DATE) - (INTERVAL '1 month' * %s) + INTERVAL '1 month',
                    date_trunc('month', CURRENT_DATE),
                    INTERVAL '1 month'
                ) AS m
            ),
            due AS (
                SELECT date_trunc('month', data_vencimento) AS m, SUM(valor * 1.20) AS due_mes
                FROM emprestimos
                GROUP BY 1
            ),
            pay AS (
                SELECT date_trunc('month', data_pagamento) AS m, SUM(valor_pago) AS pagos_mes
                FROM pagamentos GROUP BY 1
            ),
            pen AS (
                SELECT date_trunc('month', data_aplicacao) AS m, SUM(valor) AS penalizacoes_mes
                FROM penalizacoes GROUP BY 1
            )
            SELECT to_char(s.m, 'YYYY-MM') AS ym,
                   COALESCE(d.due_mes, 0) AS due_mes,
                   COALESCE(p.pagos_mes, 0) AS pagos_mes,
                   COALESCE(x.penalizacoes_mes, 0) AS penalizacoes_mes
            FROM series s
            LEFT JOIN due d ON d.m = s.m
            LEFT JOIN pay p ON p.m = s.m
            LEFT JOIN pen x ON x.m = s.m
            ORDER BY s.m
        """, (months,))
        out = []
        for r in cursor.fetchall():
            due = _to_float(r["due_mes"])
            recebidos = _to_float(r["pagos_mes"]) + _to_float(r["penalizacoes_mes"])
            eficiencia = _to_float((recebidos / due * 100) if due > 0 else 0.0)
            out.append({
                "ym": r["ym"],
                "due_mes": due,
                "recebidos_mes": recebidos,
                "eficiencia_percent": eficiencia
            })
        result = {"months": months, "series": out}
        if use_cache:
            _cset(ckey, result)
        return result
    finally:
        cursor.close()
        conn.close()


@router.get("/clientes/insights")
def obter_clientes_insights(
    limit: int = Query(20, ge=1, le=100),
    funcionario_atual: dict = Depends(get_current_funcionario),
    use_cache: bool = Query(True),
    refresh: bool = Query(False),
):
    """
    Insights por cliente (top por saldo em aberto):
      - total_emprestimos, ativos, pagos
      - saldo_em_aberto (em ativos)
      - ultimo_pagamento, dias_desde_ultimo_pagamento
      - maior_atraso_ativo (dias)
      - metodo_pagamento_preferido
      - notificacoes_pendentes
    """
    ckey = _ckey("clientes-insights", {"limit": limit})
    if use_cache and not refresh:
        cached = _cget(ckey)
        if cached is not None:
            return cached

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("""
            WITH emprest AS (
                SELECT cliente_id,
                       COUNT(*) AS total_emprestimos,
                       SUM(CASE WHEN status='Ativo' THEN 1 ELSE 0 END) AS ativos,
                       SUM(CASE WHEN status='Pago' THEN 1 ELSE 0 END) AS pagos
                FROM emprestimos
                GROUP BY cliente_id
            ),
            pagos AS (
                SELECT emprestimo_id, COALESCE(SUM(valor_pago),0) AS total_pago
                FROM pagamentos
                GROUP BY emprestimo_id
            ),
            ativos AS (
                SELECT e.cliente_id, e.emprestimo_id, e.valor, COALESCE(p.total_pago,0) AS total_pago, e.data_vencimento
                FROM emprestimos e
                LEFT JOIN pagos p ON p.emprestimo_id = e.emprestimo_id
                WHERE e.status='Ativo'
            ),
            saldo AS (
                SELECT cliente_id, GREATEST(SUM(valor*1.20 - total_pago), 0) AS saldo_em_aberto
                FROM ativos
                GROUP BY cliente_id
            ),
            ultimo_pag AS (
                SELECT cliente_id, MAX(data_pagamento) AS ultimo_pagamento
                FROM pagamentos
                GROUP BY cliente_id
            ),
            atraso AS (
                SELECT cliente_id, MAX(GREATEST((CURRENT_DATE - DATE(data_vencimento))::int, 0)) AS max_atraso
                FROM ativos
                WHERE DATE(data_vencimento) < CURRENT_DATE
                GROUP BY cliente_id
            ),
            metodo_pref AS (
                SELECT cliente_id, metodo_pagamento, cnt, rn FROM (
                    SELECT cliente_id, metodo_pagamento, COUNT(*) AS cnt,
                           ROW_NUMBER() OVER (PARTITION BY cliente_id ORDER BY COUNT(*) DESC) AS rn
                    FROM pagamentos
                    GROUP BY cliente_id, metodo_pagamento
                ) t WHERE rn = 1
            ),
            notif AS (
                SELECT cliente_id, COUNT(*) AS pendentes
                FROM notificacoes
                WHERE status = 'Pendente'
                GROUP BY cliente_id
            )
            SELECT c.cliente_id, c.nome, c.telefone,
                   COALESCE(em.total_emprestimos,0) AS total_emprestimos,
                   COALESCE(em.ativos,0) AS ativos,
                   COALESCE(em.pagos,0) AS pagos,
                   COALESCE(s.saldo_em_aberto,0) AS saldo_em_aberto,
                   up.ultimo_pagamento,
                   at.max_atraso AS maior_atraso_ativo,
                   mp.metodo_pagamento AS metodo_pagamento_preferido,
                   COALESCE(n.pendentes,0) AS notificacoes_pendentes
            FROM clientes c
            LEFT JOIN emprest em ON em.cliente_id = c.cliente_id
            LEFT JOIN saldo s ON s.cliente_id = c.cliente_id
            LEFT JOIN ultimo_pag up ON up.cliente_id = c.cliente_id
            LEFT JOIN atraso at ON at.cliente_id = c.cliente_id
            LEFT JOIN metodo_pref mp ON mp.cliente_id = c.cliente_id
            LEFT JOIN notif n ON n.cliente_id = c.cliente_id
            WHERE COALESCE(s.saldo_em_aberto,0) > 0
            ORDER BY s.saldo_em_aberto DESC
            LIMIT %s
        """, (limit,))
        rows = cursor.fetchall()
        data = []
        now = datetime.now(timezone.utc).date()
        for r in rows:
            ultimo_pag = r.get("ultimo_pagamento")
            dias_desde_ultimo = None
            if ultimo_pag:
                ultimo_pag_date = ultimo_pag.date() if hasattr(ultimo_pag, 'date') else ultimo_pag
                dias_desde_ultimo = (now - ultimo_pag_date).days if isinstance(ultimo_pag_date, date) else None
            
            data.append({
                "cliente_id": r["cliente_id"],
                "nome": r.get("nome"),
                "telefone": r.get("telefone"),
                "total_emprestimos": int(r.get("total_emprestimos", 0) or 0),
                "ativos": int(r.get("ativos", 0) or 0),
                "pagos": int(r.get("pagos", 0) or 0),
                "saldo_em_aberto": _to_float(r.get("saldo_em_aberto", 0)),
                "ultimo_pagamento": _to_iso(ultimo_pag) if ultimo_pag else None,
                "dias_desde_ultimo_pagamento": dias_desde_ultimo,
                "maior_atraso_ativo": int(r.get("maior_atraso_ativo", 0) or 0),
                "metodo_pagamento_preferido": r.get("metodo_pagamento_preferido"),
                "notificacoes_pendentes": int(r.get("notificacoes_pendentes", 0) or 0)
            })
        
        result = {"limit": limit, "clientes": data}
        if use_cache:
            _cset(ckey, result)
        return result
    finally:
        cursor.close()
        conn.close()