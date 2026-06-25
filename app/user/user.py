from fastapi import APIRouter, Depends, Header, HTTPException

from app.core.redis_client import redis_client
from app.service.user_service import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["用户服务"]
)


@router.get("/profile")
def profile(current_user=Depends(get_current_user)):
    return {
        "message": "你已登录",
        "user": current_user,
    }


@router.post("/logout")
def logout(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="未登录")

    key = f"auth:token:{token}"
    redis_client.delete(key)
    return {
        "message": "退出成功"
    }

