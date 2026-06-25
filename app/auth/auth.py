from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.dto.dto import User
from app.request.request import UserRequest, PhoneLoginRequest
from app.service.auth_service import create_user_service, send_sms_code, login_service, phone_login_service

router = APIRouter(
    prefix="/auth",
    tags=["认证服务"]
)


@router.post("/username-signup")
def create_user(
    data: UserRequest,
    db: Session = Depends(get_db)
):
    user = User(
        username=data.username,
        password=data.password,
        name=data.username,
        role_id=settings.DEFAULT_ROLE_ID,
        status=1,
    )
    return create_user_service(user, db)




@router.post("/phone-login")
def login_by_phone(
    data: PhoneLoginRequest,
    db: Session = Depends(get_db)
):
    return phone_login_service(data, db)


@router.post("/send_code")
def send_code(phone: str):
    send_sms_code(phone)

    return {
        "code": 200,
        "message": "验证码已发送"
    }
@router.post("/login")
def login(
    data: UserRequest,
    db: Session = Depends(get_db)
):
    return login_service(data, db)