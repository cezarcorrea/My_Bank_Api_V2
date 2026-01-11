import logging
from fastapi import APIRouter, status

from src.schemas.auth import LoginIn
from src.security import sign_jwt, sign_refresh_jwt
from src.views.auth import LoginOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth")

@router.post("/login", response_model=LoginOut, status_code=status.HTTP_200_OK)
async def login(data: LoginIn):
    """Realizar login e obter tokens de acesso e refresh"""
    logger.info(f"Login realizado para user_id={data.user_id}")
    access_token = sign_jwt(user_id=data.user_id, token_type="access")
    refresh_token = sign_refresh_jwt(user_id=data.user_id)
    
    return {
        "access_token": access_token["access_token"],
        "refresh_token": refresh_token["access_token"],
        "token_type": "bearer",
        "expires_in": int(0.25 * 3600)
    }

@router.post("/refresh", response_model=LoginOut, status_code=status.HTTP_200_OK)
async def refresh_token(data: LoginIn):
    """Renovar token de acesso"""
    logger.info(f"Token renovado para user_id={data.user_id}")
    access_token = sign_jwt(user_id=data.user_id, token_type="access")
    
    return {
        "access_token": access_token["access_token"],
        "refresh_token": None,
        "token_type": "bearer",
        "expires_in": int(0.25 * 3600)
    }