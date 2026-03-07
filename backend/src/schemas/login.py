from pydantic import BaseModel
from typing import Optional

class UserInfo(BaseModel):
    id: int
    username: str
    role: str
    full_name: Optional[str] = None
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    requires_2fa: Optional[bool] = False
    user_info: Optional[UserInfo] = None

class LoginRequest(BaseModel):
    email: str
    password: str
