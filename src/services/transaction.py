import logging
from databases.interfaces import Record

from src.database import database
from src.exceptions import AccountNotFoundError, BusinessError, TransactionNotFoundError
from src.models.account import accounts
from src.models.transaction import TransactionType, transactions
from src.schemas.transaction import TransactionIn
from src.config import settings

logger = logging.getLogger(__name__)


class TransactionService:
    async def read_all(
        self, account_id: int, limit: int, skip: int = 0
    ) -> list[Record]:
        """Busca transações de uma conta com paginação"""
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1
        if skip < 0:
            skip = 0
            
        query = (
            transactions.select()
            .where(transactions.c.account_id == account_id)
            .limit(limit)
            .offset(skip)
        )
        result = await database.fetch_all(query)
        logger.info(f"Listadas {len(result)} transações para account_id={account_id}")
        return result

    async def read_all_transactions(self, limit: int, skip: int = 0) -> list[Record]:
        """Busca todas as transações do sistema"""
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1
        if skip < 0:
            skip = 0
            
        query = transactions.select().limit(limit).offset(skip)
        result = await database.fetch_all(query)
        logger.info(f"Listadas {len(result)} transações totais")
        return result

    async def read_by_id(self, transaction_id: int) -> Record:
        """Busca uma transação específica por ID"""
        query = transactions.select().where(transactions.c.id == transaction_id)
        result = await database.fetch_one(query)
        
        if not result:
            logger.warning(f"Transação não encontrada: id={transaction_id}")
            raise TransactionNotFoundError
            
        logger.info(f"Transação recuperada: id={transaction_id}")
        return result

    @database.transaction()
    async def create(self, transaction: TransactionIn) -> Record:
        """Cria uma transação com validação de saldo"""
        # Validar se a conta existe
        query = accounts.select().where(accounts.c.id == transaction.account_id)
        account = await database.fetch_one(query)
        if not account:
            logger.error(f"Tentativa de transação em conta inexistente: account_id={transaction.account_id}")
            raise AccountNotFoundError

        # Validar montante mínimo
        if transaction.amount < settings.min_transaction_amount:
            logger.warning(f"Transação com valor menor que o mínimo: {transaction.amount}")
            raise BusinessError(f"Valor mínimo de transação: {settings.min_transaction_amount}")

        # Calcular novo saldo
        if transaction.type == TransactionType.WITHDRAWAL:
            balance = float(account.balance) - transaction.amount
            if balance < 0:
                logger.warning(f"Saldo insuficiente para saque: account_id={transaction.account_id}, saldo={account.balance}, valor={transaction.amount}")
                raise BusinessError("Operation not carried out due to lack of balance")
        else:
            balance = float(account.balance) + transaction.amount

        # Validar limite de saldo
        if balance > settings.max_account_balance:
            logger.warning(f"Saldo ultrapassaria o limite: {balance}")
            raise BusinessError(f"Saldo máximo permitido: {settings.max_account_balance}")

        # Registrar transação
        transaction_id = await self.__register_transaction(transaction)
        # Atualizar saldo
        await self.__update_account_balance(transaction.account_id, balance)

        logger.info(f"Transação criada: id={transaction_id}, account_id={transaction.account_id}, type={transaction.type}, amount={transaction.amount}")

        query = transactions.select().where(transactions.c.id == transaction_id)
        return await database.fetch_one(query)
    

    async def __update_account_balance(self, account_id: int, balance: float) -> None:
        """Atualiza o saldo da conta"""
        command = (
            accounts.update().where(accounts.c.id == account_id).values(balance=balance)
        )
        await database.execute(command)

    async def __register_transaction(self, transaction: TransactionIn) -> int:
        """Registra uma nova transação no banco"""
        command = transactions.insert().values(
            account_id=transaction.account_id,
            type=transaction.type,
            amount=transaction.amount,
        )
        return await database.execute(command)
