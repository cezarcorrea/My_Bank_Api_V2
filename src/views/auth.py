from pydantic import BaseModel
from typing import Optional


class LoginOut(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 900 