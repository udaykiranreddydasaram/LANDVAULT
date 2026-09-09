from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserRead"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: str = "viewer"
    department: Optional[str] = "Revenue Department"


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    department: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


Token.model_rebuild()
