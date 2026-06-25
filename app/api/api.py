from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.dto.dto import User
from app.request.request import UserRequest, PhoneLoginRequest, UpdateUserRequest
from app.service.auth_service import create_user_service, send_sms_code, login_service, phone_login_service
from app.service.departments_service import get_departments_service
from app.service.user_service import get_users_service, get_current_user, update_user_role_service,  \
    disable_user_service, enable_user_service

router = APIRouter(
    prefix="/api",
    tags=["认证服务"]
)

@router.get("/departments")
def get_departments(
    db: Session = Depends(get_db),
):
    departments = get_departments_service(db)
    return {
        "code":200,
        "message":"获取成功",
        "data":departments,
    }

@router.get("/admin/users")
def get_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    users = get_users_service(db,current_user)
    return {
        "code":200,
        "message":"获取成功",
        "data":users,
    }

@router.put("/admin/users/update/{user_id}")
def update_user_role(
    user_id: int,
    data: UpdateUserRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role_id"]!=4:
        return {
            "code": 409,
            "message": "权限不够",
            "data": current_user,
        }
    return update_user_role_service(user_id,data,db)

@router.put("/admin/users/disable/{user_id}")
def disable_user(
    user_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role_id"]!=4:
        return {
            "code": 409,
            "message": "权限不够",
            "data": current_user,
        }
    return disable_user_service(user_id,db)

@router.put("/admin/users/enable/{user_id}")
def enable_user(
    user_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role_id"]!=4:
        return {
            "code": 409,
            "message": "权限不够",
            "data": current_user,
        }
    return enable_user_service(user_id,db)