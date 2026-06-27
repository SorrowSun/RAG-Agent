from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    account: str
    password: str


class RegisterRequest(BaseModel):
    phone: str
    realName: str
    department: str
    password: str
    confirmPassword: str


class SendCodeRequest(BaseModel):
    target: str
    type: str = Field(pattern="^(phone|email)$")
    purpose: str


class PhoneLoginRequest(BaseModel):
    phone: str
    code: str


class UpdateUserRequest(BaseModel):
    realName: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None


class UpdateUserBody(BaseModel):
    username: Optional[str] = None
    realName: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None

class GetUsersBody(BaseModel):
    page: Optional[int] = 1
    pageSize: Optional[int] = 10
    name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


class EmailBindRequest(BaseModel):
    email:str
    verifyCode:str

class PhoneChangeRequest(BaseModel):
    newPhone: str
    verifyCode: str


class ChangePasswordRequest(BaseModel):
    verifyType: str = Field(pattern="^(phone|email)$")
    verifyCode: str
    newPassword: str
    confirmPassword: str
