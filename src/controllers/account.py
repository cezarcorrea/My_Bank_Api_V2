import logging
from fastapi import APIRouter, Depends, status, Query
from typing import Annotated

from src.schemas.account import AccountIn
from src.security import login_required, get_current_user
from src.services.account import AccountService
from src.services.transaction import TransactionService
from src.views.account import AccountOut, TransactionOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/accounts", dependencies=[Depends(login_required)])

account_service = AccountService()
tx_service = TransactionService() 

@router.get("/", response_model=list[AccountOut])
async def read_account(
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """Lista todas as contas com paginação"""
    logger.info(f"Listando contas - user_id={current_user['user_id']}, limit={limit}, skip={skip}")
    return await account_service.read_all(limit=limit, skip=skip)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AccountOut)
async def create_account(
    account: AccountIn,
    current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """Cria uma nova conta"""
    logger.info(f"Criando conta para user_id={account.user_id}")
    return await account_service.create(account)

@router.get("/{id}/transactions", response_model=list[TransactionOut])
async def read_account_transactions(
    id: int,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """Lista transações de uma conta específica"""
    logger.info(f"Listando transações da conta {id} - user_id={current_user['user_id']}")
    return await tx_service.read_all(account_id=id, limit=limit, skip=skip)
