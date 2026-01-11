import logging
from databases.interfaces import Record

from src.database import database
from src.models.account import accounts
from src.schemas.account import AccountIn
from src.exceptions import DuplicateAccountError

logger = logging.getLogger(__name__)


class AccountService:
    async def read_all(self, limit: int, skip: int = 0) -> list[Record]:
        """Busca todas as contas com paginação"""
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1
        if skip < 0:
            skip = 0
            
        query = accounts.select().limit(limit).offset(skip)
        result = await database.fetch_all(query)
        logger.info(f"Listadas {len(result)} contas (limit={limit}, skip={skip})")
        return result

    async def create(self, account: AccountIn) -> Record:
        """Cria uma nova conta com validação de duplicata"""
        # Validar se já existe conta para este user_id
        query = accounts.select().where(accounts.c.user_id == account.user_id)
        existing = await database.fetch_one(query)
        
        if existing:
            logger.warning(f"Tentativa de criar conta duplicada para user_id={account.user_id}")
            raise DuplicateAccountError(f"Conta já existe para o usuário {account.user_id}")
        
        command = accounts.insert().values(user_id=account.user_id, balance=account.balance)
        account_id = await database.execute(command)
        
        logger.info(f"Conta criada: id={account_id}, user_id={account.user_id}, balance={account.balance}")

        query = accounts.select().where(accounts.c.id == account_id)
        return await database.fetch_one(query)