import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.controllers import account, auth, transaction
from src.database import database
from src.exceptions import (
    AccountNotFoundError, 
    BusinessError, 
    TransactionNotFoundError,
    UnauthorizedError,
    DuplicateAccountError
)

logger = logging.getLogger(__name__)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicação...")
    await database.connect()
    logger.info("Conectado ao banco de dados")
    yield
    logger.info("Fechando conexão com banco de dados...")
    await database.disconnect()
    logger.info("Aplicação finalizada")

tags_metadata = [
    {
        "name": "auth",
        "description": "Operations for authentication."
    },
    {
       "name": "account",
        "description": "Operations to maintain accounts." 
    },
    {
        "name": "transactions",
        "description": "Operations to maintain transactions."
    },
]

app = FastAPI(
    title="Transactions API",
    version="2.0.0",
    summary="Microservice to maintain withdrawal and deposit operations from current accounts.",
    description="""
Transactions API is the microservice for recording current account transactions. 💸💰

## Account

* **Create accounts**.
* **List accounts**.
* **List account transactions by ID**.

## Transaction

* **Create transactions**.
* **List all transactions**.
* **Get transaction by ID**.

## Health

* **Check API health**.
""",
    openapi_tags=tags_metadata,
    redoc_url=None,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    content={"detail": "Muitas requisições. Tente novamente mais tarde."}
))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["auth"])
app.include_router(account.router, tags=["account"])
app.include_router(transaction.router, tags=["transactions"])

# --- EXCEPTION HANDLERS ---

@app.exception_handler(AccountNotFoundError)
async def account_not_found_error_handler(request: Request, exc: AccountNotFoundError):
    logger.warning(f"Conta não encontrada - Path: {request.url.path}")
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Account not found."})

@app.exception_handler(TransactionNotFoundError)
async def transaction_not_found_error_handler(request: Request, exc: TransactionNotFoundError):
    logger.warning(f"Transação não encontrada - Path: {request.url.path}")
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Transaction not found."})

@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    logger.warning(f"Erro de negócio - {str(exc)}")
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})

@app.exception_handler(UnauthorizedError)
async def unauthorized_error_handler(request: Request, exc: UnauthorizedError):
    logger.warning(f"Acesso não autorizado - User: {request.headers.get('Authorization', 'Unknown')}")
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Access denied."})

@app.exception_handler(DuplicateAccountError)
async def duplicate_account_error_handler(request: Request, exc: DuplicateAccountError):
    logger.warning(f"Tentativa de criar conta duplicada")
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})

# --- HEALTH CHECK ---

@app.get("/health", tags=["health"])
@limiter.limit("100/minute")
async def health_check(request: Request):
    """Verificar saúde da API"""
    try:
        await database.fetch_one("SELECT 1")
        logger.info("Health check: OK")
        return {
            "status": "healthy",
            "database": "connected",
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "detail": str(e)}
        )