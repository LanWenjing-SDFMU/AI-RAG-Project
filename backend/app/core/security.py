"""
JWT 认证模块
"""
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Header
from jose import JWTError, jwt
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict) -> str:
    """创建 JWT token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict | None:
    """验证 JWT token，返回 payload 或 None"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(authorization: str = Header("", description="Bearer Token")) -> str:
    """从 Authorization header 获取当前登录用户的工号"""
    token = authorization
    if token.startswith("Bearer "):
        token = token[7:]
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="未登录或 Token 已过期")
    return payload.get("sub", "")


async def require_admin(authorization: str = Header("", description="Bearer Token")) -> str:
    """验证当前用户是否为管理员，返回工号"""
    token = authorization
    if token.startswith("Bearer "):
        token = token[7:]
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="未登录或 Token 已过期")
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可执行此操作")
    return payload.get("sub", "")
