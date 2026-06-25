from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

import json

from app.core.config import settings
from app.core.redis_client import redis_client as redis
from app.dto.dto import User,Role,RolePermission,Permission,Department
from app.request.request import PhoneLoginRequest, UserRequest
from app.tools.tools import generate_code, generate_token

def get_departments_service(db:Session):
    departments = db.scalars(select(Department)).all()
    if not departments:
        raise HTTPException(status_code=404, detail="部门为空")
    return [
        {
            "id": department.id,
            "name": department.name,
            "status": department.status
        }
        for department in departments
    ]