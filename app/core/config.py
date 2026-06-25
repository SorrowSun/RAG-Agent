from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    db_host: str
    db_port: int = 3306
    db_name: str
    db_user: str
    db_password: str

    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    app_prefix: str = "sms:code:"
    SMS_CODE_EXPIRE_SECONDS: int = 300
    TOKEN_EXPIRE_SECONDS: int = 7200
    DEFAULT_ROLE_ID:int =  1
    ALIYUN_ACCESS_KEY_ID: str
    ALIYUN_ACCESS_KEY_SECRET: str
    ALIYUN_SMS_SIGN_NAME:str
    ALIYUN_SMS_TEMPLATE_CODE: str
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8"
    )


settings = Settings()