from fastapi import APIRouter, Depends, Header, HTTPException

from app.core.redis_client import redis_client
from app.service.user_service import get_current_user

router = APIRouter(
    prefix="/api",
    tags=["用户服务"]
)


@router.get("/auth/current-user")
def current_user_info(current_user=Depends(get_current_user)):
    return {
        "code": 200,
        "message": "获取成功",
        "data": current_user,
    }


@router.post("/auth/logout")
def logout(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="未登录")

    redis_client.delete(f"auth:token:{token}")
    return {
        "code": 200,
        "message": "退出成功",
        "data": None,
    }
