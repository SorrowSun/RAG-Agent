from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from app.core.database import engine
from app.core.redis_client import redis_client
from app.tools.tools import generate_code
from app.auth.auth import router as auth_router
from app.user.user import router as user_router
from app.api.api import router as api_router
app = FastAPI(title="RAG 智能问答系统后端")
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(api_router)
@app.get("/health")
def health_check():
    return {"code": 200, "message": "服务运行正常"}


@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            value = result.scalar()

        return {
            "code": 200,
            "message": "数据库连接成功",
            "data": {"result": value}
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"数据库连接失败：{str(e)}"
        )

@app.get("/redis-test")
def redis_test():
    try:
        # ping() 成功会返回 True
        redis_client.ping()

        # 写入一个测试数据，60 秒后自动过期
        redis_client.set("test:hello", "Redis 连接成功", ex=60)

        # 再读取出来
        value = redis_client.get("test:hello")

        return {
            "code": 200,
            "message": "Redis 连接成功",
            "data": {
                "value": value
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Redis 连接失败：{str(e)}"
        )

for route in app.routes:
    if hasattr(route, "path"):
        print(route.path, route.methods)