import logging
from fastapi import APIRouter, Depends, status, Query
from typing import Annotated

from src.schemas.transaction import TransactionIn
from src.security import login_required, get_current_user
from src.services.transaction import TransactionService
from src.views.transaction import TransactionOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", dependencies=[Depends(login_required)])

service = TransactionService()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TransactionOut)
async def create_transaction(
    transaction: TransactionIn,
    current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """Criar uma nova transação de depósito ou saque"""
    logger.info(f"Criando transação - account_id={transaction.account_id}, type={transaction.type}, amount={transaction.amount}")
    return await service.create(transaction)

@router.get("/", response_model=list[TransactionOut])
async def list_all_transactions(
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """Retorna o histórico de todas as transações do sistema com paginação"""
    logger.info(f"Listando todas as transações - user_id={current_user['user_id']}")
    return await service.read_all_transactions(limit=limit, skip=skip)

@router.get("/{transaction_id}", response_model=TransactionOut)
async def get_transaction(
    transaction_id: int,
    current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """Retorna os detalhes de uma transação específica pelo ID"""
    logger.info(f"Obtendo transação {transaction_id} - user_id={current_user['user_id']}")
    return await service.read_by_id(transaction_id)


