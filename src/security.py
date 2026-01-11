import logging
from datetime import datetime, timezone, timedelta
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)

SECRET = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm

# --- SCHEMAS ---

class AccessToken(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: float
    iat: float
    jti: str
    # nbf removido para evitar rejeição por micro-diferenças de relógio

class JWTToken(BaseModel):
    access_token: AccessToken

# --- FUNÇÕES CORE ---

def sign_jwt(user_id: int, token_type: str = "access") -> dict:
    """Gera um JWT com duração configurável"""
    now = datetime.now(timezone.utc)
    
    if token_type == "refresh":
        expiration = now + timedelta(days=settings.jwt_refresh_expiration_days)
    else:
        expiration = now + timedelta(hours=settings.jwt_expiration_hours)
    
    payload = {
        "iss": "desafio-bank.com.br",
        "sub": str(user_id),
        "aud": "desafio-bank",
        "exp": expiration.timestamp(),
        "iat": now.timestamp(),
        "jti": uuid4().hex,
        "type": token_type,
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    logger.info(f"Token {token_type} gerado para user_id={user_id}")
    return {"access_token": token}

def sign_refresh_jwt(user_id: int) -> dict:
    """Gera um refresh token com duração longa"""
    return sign_jwt(user_id, token_type="refresh")

async def decode_jwt(token: str) -> JWTToken | None:
    try:
        decoded_payload = jwt.decode(
            token, 
            SECRET, 
            audience="desafio-bank", 
            algorithms=[ALGORITHM],
            leeway=10
        )
        return JWTToken(access_token=AccessToken(**decoded_payload))
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token inválido: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erro ao decodificar token: {str(e)}")
        return None
        
# --- AUTH MIDDLEWARE ---

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> JWTToken:
        # O FastAPI já extrai o token do Header para nós aqui
        credentials = await super(JWTBearer, self).__call__(request)
        
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme.",
                )

            payload = await decode_jwt(credentials.credentials)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token.",
                )
            return payload
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization code.",
        )

# --- DEPENDENCIAS ---

async def get_current_user(
    token: Annotated[JWTToken, Depends(JWTBearer())],
) -> dict[str, int]:
    return {"user_id": int(token.access_token.sub)}

def login_required(current_user: Annotated[dict[str, int], Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return current_user