from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


# MySQL 连接地址
DATABASE_URL = (
    f"mysql+pymysql://{settings.db_user}:"
    f"{settings.db_password}@"
    f"{settings.db_host}:"
    f"{settings.db_port}/"
    f"{settings.db_name}"
    "?charset=utf8mb4"
)


# 类似 Spring 的 DataSource / 连接池
engine = create_engine(
    DATABASE_URL,
    echo=True,          # 开发时打印执行的 SQL，后面可改 False
    pool_pre_ping=True  # 每次取连接前先检查连接是否有效
)


# 专门生产 Session 的工厂
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


# 所有数据库实体类的父类
class Base(DeclarativeBase):
    pass


# 给 FastAPI 接口使用：每个请求创建一个 Session，用完关闭
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()