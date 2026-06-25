import json
from sqlalchemy import select
from fastapi import Header, HTTPException
from sqlalchemy.orm import Session
from app.core.redis_client import redis_client
from app.dto.dto import User, RolePermission, Department, Role
from app.request.request import UpdateUserRequest


def get_user_info(user,db:Session):
    # 1. 查角色
    role = db.scalar(
        select(Role).where(Role.id == user.role_id)
    )

    if not role:
        raise HTTPException(status_code=404, detail="用户角色不存在")

    # 2. 查部门
    department = None
    if user.department_id:
        department = db.scalar(
            select(Department).where(
                Department.id == user.department_id
            )
        )

    # 3. 根据角色查权限
    permissions = db.scalars(
        select(RolePermission)
        .where(RolePermission.role_id == user.role_id)
    ).all()
    return role,department,permissions

def get_current_user(authorization: str = Header(default="")):
    """
    从请求头读取 token:
    Authorization: Bearer xxx
    """
    if authorization == "":
        raise HTTPException(status_code=401, detail="请携带token")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="请以Bearer 为前缀")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="未登录")

    key = f"auth:token:{token}"
    user_json = redis_client.get(key)
    if not user_json:
        raise HTTPException(status_code=401, detail="登录已过期")

    return json.loads(user_json)

def get_users_service(db: Session,current_user:User):
    if current_user["role_id"] !=4:
        raise HTTPException(status_code=409, detail="用户权限不足")

    users = db.scalars(select(User)).all()

    if not users:
        raise HTTPException(status_code=404, detail="用户为空")

    return [
        {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "phone": user.phone,
            "avatar": user.avatar,
            "role_id": user.role_id,
            "department_id": user.department_id,
            "status": user.status
        }
        for user in users
    ]

def update_user_role_service(
    user_id: int,
    data: UpdateUserRequest,
    db: Session
):
    user = db.scalar(
        select(User).where(User.id == user_id)
    )

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.username = data.username
    user.name = data.name
    user.phone = data.phone
    user.avatar = data.avatar
    user.role_id = data.role_id
    user.department_id = data.department_id
    user.status = data.status

    db.commit()
    db.refresh(user)

    return {
        "code":200,
        "message": "修改成功",
        "user": user
    }

def disable_user_service(
    user_id:int,
    db:Session
):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.status = 0
    db.commit()
    db.refresh(user)
    return {
        "code":200,
        "message": "禁用成功",
        "user": user
    }

def enable_user_service(
    user_id:int,
    db:Session
):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.status = 1
    db.commit()
    db.refresh(user)
    return {
        "code":200,
        "message": "启用成功",
        "user": user
    }