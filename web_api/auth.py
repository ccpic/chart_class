"""
JWT 认证和密码加密工具
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import os

# JWT 配置
# 生产环境必须设置 JWT_SECRET_KEY 环境变量，否则启动失败
# 开发环境可以使用默认值（仅用于本地开发，不安全）


def _validate_secret_key(secret_key: str, environment: str) -> bool:
    """
    验证 JWT 秘钥强度
    
    Args:
        secret_key: 秘钥字符串
        environment: 环境名称
        
    Returns:
        bool: 是否通过验证
    """
    if not secret_key:
        return False
    
    # 生产环境要求更严格
    if environment in ("production", "prod"):
        # 至少 32 字符，包含字母和数字
        if len(secret_key) < 32:
            return False
        # 不能是明显的默认值
        forbidden_values = [
            "your-secret-key-change-in-production",
            "dev-secret-key-change-in-production-not-secure",
            "secret",
            "password",
            "123456",
        ]
        if secret_key.lower() in [v.lower() for v in forbidden_values]:
            return False
    
    return True


def _get_environment() -> str:
    """获取当前环境"""
    env = os.getenv("ENVIRONMENT") or os.getenv("NODE_ENV") or os.getenv("FLASK_ENV")
    if env:
        return env.lower()
    # 检查是否在 Docker 容器中
    if os.path.exists("/.dockerenv"):
        return "production"  # Docker 中默认视为生产环境
    return "development"


ENVIRONMENT = _get_environment()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    if ENVIRONMENT in ("production", "prod"):
        # 生产环境强制要求
        raise ValueError(
            "❌ JWT_SECRET_KEY 环境变量未设置！\n"
            "生产环境必须设置一个强随机秘钥（至少 32 字符）。\n"
            "生成方法：\n"
            "  - Linux/Mac: openssl rand -hex 32\n"
            "  - Windows: python -c \"import secrets; print(secrets.token_hex(32))\"\n"
            "  - Python: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )
    else:
        # 开发环境使用默认值（不安全，仅用于开发）
        import warnings
        warnings.warn(
            "⚠️  警告：JWT_SECRET_KEY 未设置，使用不安全的默认值。"
            "生产环境必须设置环境变量！"
            "生成方法：python -c \"import secrets; print(secrets.token_hex(32))\"",
            UserWarning
        )
        SECRET_KEY = "dev-secret-key-change-in-production-not-secure"
        print("⚠️  警告：使用开发环境默认 JWT 秘钥，生产环境请设置 JWT_SECRET_KEY 环境变量")
elif not _validate_secret_key(SECRET_KEY, ENVIRONMENT):
    # 秘钥强度不足
    if ENVIRONMENT in ("production", "prod"):
        raise ValueError(
            f"❌ JWT_SECRET_KEY 强度不足！\n"
            f"当前秘钥长度: {len(SECRET_KEY)} 字符\n"
            f"要求：至少 32 字符，且不能是默认值\n"
            f"生成方法：python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    else:
        import warnings
        warnings.warn(
            f"⚠️  JWT_SECRET_KEY 强度不足（长度: {len(SECRET_KEY)}），建议使用至少 32 字符的随机字符串",
            UserWarning
        )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7  # Token 过期时间（天）


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    # JWT 的 exp 字段需要是 Unix 时间戳（整数）
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码 JWT Token"""
    import logging

    logger = logging.getLogger(__name__)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}")
        return None
