from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.routes.auth import router as auth_router
from app.routes.clientes import router as clientes_router
from app.routes.localizacoes import router as localizacoes_router
from app.routes.documentos import router as documentos_router
from app.routes.funcionarios import router as funcionarios_router
from app.routes.emprestimos import router as emprestimos_router
from app.routes.pagamentos import router as pagamentos_router
from app.routes.penalizacoes import router as penalizacoes_router
from app.routes.outros_ganhos import router as outros_ganhos_router
from app.routes.penhor import router as penhor_router
from app.routes.testemunhas import router as testemunhas_router
from app.routes.notificacoes import router as notificacoes_router
from app.routes.historico_credito import router as historico_credito_router
from app.routes.ocupacoes import router as ocupacoes_router
from app.routes.auth_clientes import router as auth_clientes_router
from app.routes.dashboard import router as dashboard_router

app = FastAPI(title="Lacos Microcrédito API", description="API para gestão de clientes, localizações, documentos e operações financeiras")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/")
def verificar_conexao():
    return {"mensagem": "Lacos Microcrédito API"}

app.include_router(auth_router, prefix="/api/auth", tags=["autenticacao"])
app.include_router(clientes_router, prefix="/api/clientes", tags=["clientes"])
app.include_router(localizacoes_router, prefix="/api/localizacoes", tags=["localizacoes"])
app.include_router(documentos_router, prefix="/api/documentos", tags=["documentos"])
app.include_router(funcionarios_router, prefix="/api/funcionarios", tags=["funcionarios"])
app.include_router(emprestimos_router, prefix="/api/emprestimos", tags=["emprestimos"])
app.include_router(pagamentos_router, prefix="/api/pagamentos", tags=["pagamentos"])
app.include_router(penalizacoes_router, prefix="/api/penalizacoes", tags=["penalizacoes"])
app.include_router(outros_ganhos_router, prefix="/api/outros_ganhos", tags=["outros_ganhos"])
app.include_router(penhor_router, prefix="/api/penhor", tags=["penhor"])
app.include_router(testemunhas_router, prefix="/api/testemunhas", tags=["testemunhas"])
app.include_router(notificacoes_router, prefix="/api/notificacoes", tags=["notificacoes"])
app.include_router(historico_credito_router, prefix="/api/historico-credito", tags=["historico-credito"])
app.include_router(ocupacoes_router, prefix="/api/ocupacoes", tags=["ocupacoes"])
app.include_router(auth_clientes_router, prefix="/api/auth-clientes", tags=["auth-clientes"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)