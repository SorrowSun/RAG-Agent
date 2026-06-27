import json
from typing import Any

from fastapi import Header, HTTPException
from sqlalchemy import select,delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis_client import redis_client
from app.dto.dto import Department, Permission, Role, RolePermission, User
from app.request.request import GetUsersBody, UpdateUserBody, EmailBindRequest, PhoneChangeRequest

ADMIN_ROLE_CODE = "admin"


def _build_permissions(db: Session, role_id: int) -> list[str]:
    permission_rows = db.scalars(
        select(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(RolePermission.role_id == role_id)
    ).all()
    return list(permission_rows)


def get_user_info(user: User, db: Session):
    role = db.scalar(select(Role).where(Role.id == user.role_id))
    if not role:
        raise HTTPException(status_code=404, detail="用户角色不存在")

    department = None
    if user.department_id:
        department = db.scalar(select(Department).where(Department.id == user.department_id))

    permissions = _build_permissions(db, user.role_id)
    return role, department, permissions

def check_authorization(authorization):
    if not authorization:
        raise HTTPException(status_code=401, detail="请携带token")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="请以Bearer 为前缀")




def get_current_user(authorization: str = Header(default="")):
    check_authorization(authorization)
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    user_json = redis_client.get(f"auth:token:{token}")
    if not user_json:
        raise HTTPException(status_code=401, detail="登录已过期")

    return json.loads(user_json)

def logout_service(authorization: str):
    check_authorization(authorization)
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    redis_client.delete(f"auth:token:{token}")
    return {"code": 200, "message": "退出成功", "data": None}



def get_users_service(data: GetUsersBody, db: Session, current_user: dict[str, Any]):
    if current_user.get("role") != ADMIN_ROLE_CODE and current_user.get("roleName") != "系统管理员":
        raise HTTPException(status_code=403, detail="用户权限不足")

    stmt = select(User)
    if data.name is not None:
        stmt = stmt.where(User.name == data.name)
    if data.phone is not None:
        stmt = stmt.where(User.phone == data.phone)
    if data.department is not None:
        department = db.scalar(select(Department).where((Department.name == data.department) | (Department.code == data.department)))
        if department:
            stmt = stmt.where(User.department_id == department.id)
    if data.role is not None:
        role = db.scalar(select(Role).where((Role.name == data.role) | (Role.code == data.role)))
        if role:
            stmt = stmt.where(User.role_id == role.id)
    stmt = stmt.offset((data.page - 1) * data.pageSize).limit(data.pageSize)

    users = db.scalars(stmt).all()
    if not users:
        return []

    results = []
    for user in users:
        role = db.scalar(select(Role).where(Role.id == user.role_id))
        department = db.scalar(select(Department).where(Department.id == user.department_id)) if user.department_id else None
        permissions = _build_permissions(db, user.role_id)
        results.append({
            "id": user.id,
            "username": user.username,
            "phone": user.phone,
            "email": None,
            "realName": user.name,
            "avatar": user.avatar or "",
            "role": role.code if role else None,
            "roleName": role.name if role else None,
            "department": department.name if department else None,
            "departmentId": str(user.department_id) if user.department_id else None,
            "roles": [role.code] if role else [],
            "permissions": permissions,
            "status": "active" if user.status == 1 else "disabled",
        })
    return results


def update_user_role_service(user_id: int, data: UpdateUserBody, db: Session):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if data.realName is not None:
        user.name = data.realName
    if data.status is not None:
        user.status = 1 if data.status == "active" else 0

    if data.role is not None:
        role = db.scalar(select(Role).where(Role.code == data.role))
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        user.role_id = role.id

    if data.department is not None:
        department = db.scalar(
            select(Department).where((Department.code == data.department) | (Department.name == data.department))
        )
        if not department:
            raise HTTPException(status_code=404, detail="部门不存在")
        user.department_id = department.id

    db.commit()
    db.refresh(user)
    return {"code": 200, "message": "更新成功", "data": None}


def disable_user_service(user_id: int, db: Session):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.status = 0
    db.commit()
    db.refresh(user)
    return {"code": 200, "message": "禁用成功", "data": None}


def enable_user_service(user_id: int, db: Session):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.status = 1
    db.commit()
    db.refresh(user)
    return {"code": 200, "message": "启用成功", "data": None}

def delete_user_service(user_id:int, db:Session):
    stmt = delete(User).where(User.id == user_id)
    db.execute(stmt)
    db.commit()

def bind_email_service(user,db:Session,data:EmailBindRequest):
    exist_email = db.scalar(select(User).where(User.email == data.email))
    if exist_email:
        return 2
    key =f"{settings.app_prefix}{data.email}"
    emailCode =  redis_client.get(key)
    if data.verifyCode == emailCode:
        user = db.scalar(select(User).where(User.id == user["id"]))
        user.email = data.email
        user.email_verified = 1
        db.commit()
        db.refresh(user)
        return 1
    return 0


def change_phone_service(user,db:Session,data:PhoneChangeRequest):
    exist_phone = db.scalar(select(User).where(User.phone == data.newPhone))
    if exist_phone:
        return 2
    key =f"{settings.app_prefix}{data.newPhone}"
    emailCode =  redis_client.get(key)
    if data.verifyCode == emailCode:
        user = db.scalar(select(User).where(User.id == user["id"]))
        user.phone = data.newPhone
        db.commit()
        db.refresh(user)
        return 1
    return 0