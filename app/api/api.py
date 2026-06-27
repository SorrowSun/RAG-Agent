from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.request.request import ChangePasswordRequest, EmailBindRequest, GetUsersBody, LoginRequest, PhoneChangeRequest, RegisterRequest, SendCodeRequest, UpdateUserBody
from app.service.auth_service import change_password_service, create_user_service, login_service, send_sms_code
from app.service.departments_service import get_departments_service
from app.service.user_service import (
    disable_user_service,
    enable_user_service,
    get_current_user,
    get_users_service,
    logout_service,
    update_user_role_service,
    delete_user_service, bind_email_service, change_phone_service,
)

router = APIRouter(prefix="/api", tags=["API"])


@router.post("/auth/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return create_user_service(data, db)


@router.post("/auth/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return login_service(data, db)


@router.post("/auth/send-code")
def send_code(data: SendCodeRequest):
    send_sms_code(data)
    return {"code": 200, "message": "验证码已发送", "data": {"success": True, "expireSeconds": 300}}


@router.post("/auth/logout")
def logout(authorization: str = Header(default="")):
    return logout_service(authorization)

@router.get("/auth/current-user")
def current_user_info(current_user=Depends(get_current_user)):
    return {"code": 200, "message": "获取成功", "data": current_user}


@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    return {"code": 200, "message": "获取成功", "data": get_departments_service(db)}


@router.get("/users")
def list_users(data: GetUsersBody = Depends(), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    users = get_users_service(data, db, current_user)
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "list": users,
            "total": len(users),
            "page": data.page,
            "pageSize": data.pageSize,
        },
    }


@router.put("/users/{id}")
def update_user(id: int, data: UpdateUserBody, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="无权访问")
    return update_user_role_service(id, data, db)


@router.patch("/users/{id}/status")
def update_user_status(id: int, status: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="无权访问")
    if status == "active":
        return enable_user_service(id, db)
    if status == "disabled":
        return disable_user_service(id, db)
    raise HTTPException(status_code=400, detail="status参数错误")


@router.delete("/users/{id}")
def delete_user(id:int,current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="无权访问")
    delete_user_service(id,db)
    return {"code": 200, "message": "删除成功", "data": None}

@router.post("/users/bind-email")
def bind_email(data:EmailBindRequest,current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = bind_email_service(current_user,db,data)
    if result ==1:
        return {
            "code": 200,
            "message": "邮箱绑定成功",
            "data": {
                "email": data.email,
                "emailVerified": "true"
            }
        }
    elif result ==0:
        return {
            "code": 1003,
            "message": "验证码错误",
            "data": {
                "email": data.email,
                "emailVerified": "false"
            }
        }
    else:
        return {
            "code": 1002,
            "message": "邮箱已被绑定",
            "data": {
                "email": data.email,
                "emailVerified": "false"
            }
        }


@router.post("/auth/change-password")
def change_password(data: ChangePasswordRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return change_password_service(data, db, current_user)
