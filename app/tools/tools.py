import random
import secrets


def generate_code(length: int = 6) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def generate_token() -> str:
    # 32字节安全随机 token
    return secrets.token_urlsafe(32)
