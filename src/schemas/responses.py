"""Schemas para respostas padronizadas da API"""
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ResponseEnvelope(BaseModel, Generic[T]):
    """Envelope padronizado para todas as respostas"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": 1, "user_id": 123},
                "error": None,
                "message": "Operação realizada com sucesso"
            }
        }


class PaginationParams(BaseModel):
    """Parâmetros de paginação padronizados"""
    limit: int = 10
    skip: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "limit": 10,
                "skip": 0
            }
        }


class TokenResponse(BaseModel):
    """Resposta de tokens (access e refresh)"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutos em segundos
