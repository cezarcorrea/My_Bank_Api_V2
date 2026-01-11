class AccountNotFoundError(Exception):
    """Levantada quando uma conta não é encontrada"""
    pass


class TransactionNotFoundError(Exception):
    """Levantada quando uma transação não é encontrada"""
    pass


class BusinessError(Exception):
    """Levantada para erros de negócio"""
    pass


class UnauthorizedError(Exception):
    """Levantada quando usuário não tem autorização"""
    pass


class DuplicateAccountError(Exception):
    """Levantada quando tenta criar conta duplicada"""
    pass