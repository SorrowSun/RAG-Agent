from pydantic import BaseModel
from typing import Optional

class UserRequest(BaseModel):
    username: str
    password: str


class PhoneLoginRequest(BaseModel):
    phone: str
    code: str

class UpdateUserRequest(BaseModel):
    username: str
    name: str
    phone: Optional[str] = None
    avatar: Optional[str] = None
    role_id: int
    department_id: Optional[int] = None
    status: int