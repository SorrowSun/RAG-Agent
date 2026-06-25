from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

import json

from app.core.config import settings
from app.core.redis_client import redis_client as redis
from app.dto.dto import User,Role,RolePermission,Permission,Department
from app.request.request import PhoneLoginRequest, UserRequest
from app.service.sms_service import ali_send_sms_code
from app.service.user_service import get_user_info
from app.tools.tools import generate_code, generate_token

def create_user_service(
        user,
        db: Session
        ):
    """

    data
    {
        username,
        password
    }
    :param user:
    :param data:
    :param db:
    :return:
    """
    exists_user = db.scalar(
        select(User).where(User.username == user.username)
    )

    if exists_user:
        raise HTTPException(status_code=409, detail="用户名已经存在")

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "id": user.id,
            "username": user.username,
            "name":user.username,
            "phone":user.phone,
            "avatar":user.avatar,
            "role_id":1,
            "roleName":"普通员工",
            "departmentId":"暂无",
            "departmentName":"暂无",
            "status":1,
            "permissions":[],
        }
    }

def send_sms_code(phone: str):
    code = generate_code(6)

    key = f"{settings.app_prefix}{phone}"

    redis.set(
        key,
        code,
        ex=settings.SMS_CODE_EXPIRE_SECONDS
    )
    # 现在先打印，之后再接阿里云/腾讯云短信服务

    print(f"手机号：{phone}，验证码：{code}")

    return ali_send_sms_code(phone,code)




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
    redis_key = f"sms:code:{data.phone}"
    redis_code = redis.get(redis_key)

    if redis_code is None:
        raise HTTPException(status_code=400, detail="验证码已过期或未发送")

    if redis_code != data.code:
        raise HTTPException(status_code=400, detail="验证码错误")

    stmt = select(User).where(User.phone == data.phone)
    user = db.scalar(stmt)
    if user is None:
        user = User(
            username=data.phone,
            name=data.phone,
            phone=data.phone,
            role_id=settings.DEFAULT_ROLE_ID,
            status=1,
        )
        return create_user_service(user,db)
    role,department,permissions = get_user_info(user,db)

    redis.delete(redis_key)

    token = generate_token()

    user_data = {
        "user_id": user.id,
        "username": user.username,
        "name": user.name,
        "phone": user.phone,
        "avatar": user.avatar,
        "role_id": user.role_id,
        "role_name": role.name,
        "department_id": user.department_id,
        "department_name": department.name if department else None,
        "status": user.status,
        "permissions": permissions

    }
    token_key = f"auth:token:{token}"
    redis.setex(token_key, settings.TOKEN_EXPIRE_SECONDS, json.dumps(user_data, ensure_ascii=False))

    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "user": user_data,
            "token": token,
            "token_type": "Bearer",
            "expires_in": settings.TOKEN_EXPIRE_SECONDS,
        }
    }

def login_service(data: UserRequest, db: Session):
    """
    data
    {
        username
        password
    }
    :param data:
    :param db:
    :return:
    """
    stmt = select(User).where(User.username == data.username)
    user = db.scalar(stmt)
    if user is None:
        raise HTTPException(status_code=400, detail="用户不存在")

    if user.password != data.password:
        raise HTTPException(status_code=400, detail="密码错误")
    role, department, permissions = get_user_info(user, db)
    token = generate_token()
    user_data = {
        "user_id": user.id,
        "username": user.username,
        "name": user.name,
        "phone": user.phone,
        "avatar": user.avatar,
        "role_id": user.role_id,
        "role_name": role.name,
        "department_id": user.department_id,
        "department_name": department.name if department else None,
        "status": user.status,
        "permissions": permissions
    }
    token_key = f"auth:token:{token}"
    redis.setex(token_key, settings.TOKEN_EXPIRE_SECONDS, json.dumps(user_data, ensure_ascii=False))

    return {
        "code": 200,
        "message": "登陆成功",
        "data": {
            "user": user_data,
            "token": token,
            "token_type": "Bearer",
            "expires_in": settings.TOKEN_EXPIRE_SECONDS,
        }
    }


