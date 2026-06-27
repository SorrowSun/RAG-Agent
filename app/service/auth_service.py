from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

import json

from app.core.config import settings
from app.core.redis_client import redis_client as redis
from app.dto.dto import User,Role,RolePermission,Permission,Department
from app.request.request import ChangePasswordRequest, LoginRequest, PhoneLoginRequest, RegisterRequest, SendCodeRequest
from app.service.sms_service import ali_send_sms_code
from app.service.user_service import get_user_info
from app.tools.tools import generate_code, generate_token


def create_user_service(data: RegisterRequest, db: Session):
    exists_user = db.scalar(select(User).where((User.username == data.phone) | (User.phone == data.phone)))
    if exists_user:
        raise HTTPException(status_code=1001, detail="手机号已注册")

    department = db.scalar(
        select(Department).where(
            (Department.name == data.department) | (Department.code == data.department)
        )
    )
    if not department:
        raise HTTPException(status_code=404, detail="部门不存在")

    role = db.scalar(select(Role).where(Role.code == "employee"))
    if not role:
        raise HTTPException(status_code=404, detail="默认角色不存在")

    user = User(
        username=data.phone,
        password=data.password,
        name=data.realName,
        phone=data.phone,
        department_id=department.id,
        role_id=role.id,
        status=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    role, department, permissions = get_user_info(user, db)
    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "id": str(user.id),
            "phone": user.phone,
            "realName": user.name,
            "department": department.name if department else None,
            "role": role.code,
            "token": None,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "phone": user.phone,
                "email": None,
                "realName": user.name,
                "avatar": user.avatar or "",
                "role": role.code,
                "roleName": role.name,
                "department": department.name if department else None,
                "departmentId": str(user.department_id) if user.department_id else None,
                "roles": [role.code],
                "permissions": permissions,
            }
        }
    }

def send_sms_code(data: SendCodeRequest):
    code = generate_code(6)
    purpose_key = f"verify:{data.purpose}:{data.type}:{data.target}"
    redis.set(purpose_key, code, ex=settings.SMS_CODE_EXPIRE_SECONDS)

    if data.type == "phone":
        return ali_send_sms_code(data.target, code)

    print(f"邮箱验证码：{data.target} -> {code}")
    return {"success": True, "code": "OK", "message": "邮件验证码已生成"}


def phone_login_service(data: PhoneLoginRequest, db: Session):
    """
    data
    {
        phone
        code
    }
    :param data:
    :param db:
    :return:
    """
    redis_key = f"verify:login:phone:{data.phone}"
    redis_code = redis.get(redis_key)

    if redis_code is None:
        raise HTTPException(status_code=400, detail="验证码已过期或未发送")

    if redis_code != data.code:
        raise HTTPException(status_code=1003, detail="验证码错误")

    stmt = select(User).where(User.phone == data.phone)
    user = db.scalar(stmt)
    created = False
    if user is None:
        user = User(
            username=data.phone,
            name=data.phone,
            phone=data.phone,
            role_id=settings.DEFAULT_ROLE_ID,
            status=1,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        created = True

    role, department, permissions = get_user_info(user, db)
    redis.delete(redis_key)

    token = generate_token()
    expires_at = int(__import__("time").time() * 1000) + settings.TOKEN_EXPIRE_SECONDS * 1000
    user_data = {
        "id": user.id,
        "username": user.username,
        "phone": user.phone,
        "email": None,
        "realName": user.name,
        "avatar": user.avatar or "",
        "role": role.code,
        "roleName": role.name,
        "department": department.name if department else None,
        "departmentId": str(user.department_id) if user.department_id else None,
        "roles": [role.code],
        "permissions": permissions,
        "status": "active" if user.status == 1 else "disabled",
    }
    redis.setex(f"auth:token:{token}", settings.TOKEN_EXPIRE_SECONDS, json.dumps(user_data, ensure_ascii=False))

    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": token,
            "expiresAt": expires_at,
            "user": user_data,
        }
    }

def login_service(data: LoginRequest, db: Session):
    stmt = select(User).where((User.username == data.account) | (User.phone == data.account))
    user = db.scalar(stmt)
    if user is None:
        raise HTTPException(status_code=1005, detail="账号不存在")
    if user.password != data.password:
        raise HTTPException(status_code=1004, detail="密码错误")

    role, department, permissions = get_user_info(user, db)
    token = generate_token()
    expires_at = int(__import__("time").time() * 1000) + settings.TOKEN_EXPIRE_SECONDS * 1000
    user_data = {
        "id": user.id,
        "username": user.username,
        "phone": user.phone,
        "email": None,
        "emailVerified": bool(getattr(user, "email_verified", 0)),
        "realName": user.name,
        "avatar": user.avatar or "",
        "role": role.code,
        "roleName": role.name,
        "department": department.name if department else None,
        "departmentId": str(user.department_id) if user.department_id else None,
        "roles": [role.code],
        "permissions": permissions,
        "status": "active" if user.status == 1 else "disabled",
    }
    redis.setex(f"auth:token:{token}", settings.TOKEN_EXPIRE_SECONDS, json.dumps(user_data, ensure_ascii=False))
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": token,
            "expiresAt": expires_at,
            "user": user_data,
        }
    }


def change_password_service(data: ChangePasswordRequest, db: Session, current_user: dict):
    if data.newPassword != data.confirmPassword:
        raise HTTPException(status_code=400, detail="两次密码不一致")

    if data.verifyType not in ("phone", "email"):
        raise HTTPException(status_code=400, detail="verifyType参数错误")

    user = db.scalar(select(User).where(User.id == current_user["id"]))
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    target = user.phone if data.verifyType == "phone" else user.email
    if not target:
        raise HTTPException(status_code=400, detail="验证码目标不存在")
    verify_key = f"verify:change_password:{data.verifyType}:{target}"
    cached_code = redis.get(verify_key)
    if not cached_code:
        raise HTTPException(status_code=400, detail="验证码已过期或未发送")
    if cached_code != data.verifyCode:
        raise HTTPException(status_code=1003, detail="验证码错误")

    user.password = data.newPassword
    db.commit()
    redis.delete(verify_key)
    return {"code": 200, "message": "密码修改成功", "data": None}


