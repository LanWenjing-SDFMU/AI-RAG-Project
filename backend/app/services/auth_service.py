"""
用户认证服务
"""
import hashlib
from ..core.database import get_connection
from ..core.security import create_access_token


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register(work_id: str, password: str) -> dict:
    """注册新用户"""
    work_id = work_id.strip()
    if not work_id:
        return {"success": False, "message": "工号不能为空"}
    if not password or len(password) < 4:
        return {"success": False, "message": "密码长度不能少于4位"}

    conn = get_connection()
    try:
        row = conn.execute("SELECT work_id FROM users WHERE work_id = ?", (work_id,)).fetchone()
        if row:
            return {"success": False, "message": f"工号「{work_id}」已存在，请直接登录"}

        conn.execute(
            "INSERT INTO users (work_id, password) VALUES (?, ?)",
            (work_id, _hash_password(password)),
        )
        conn.commit()
        return {"success": True, "message": "注册成功"}
    finally:
        conn.close()


def login(work_id: str, password: str) -> dict:
    """用户登录，成功返回 token"""
    work_id = work_id.strip()
    if not work_id:
        return {"success": False, "message": "请输入工号"}
    if not password:
        return {"success": False, "message": "请输入密码"}

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT password FROM users WHERE work_id = ?", (work_id,)
        ).fetchone()
        if row is None:
            return {"success": False, "message": f"工号「{work_id}」不存在，请先注册"}

        if row["password"] != _hash_password(password):
            return {"success": False, "message": "密码错误"}

        token = create_access_token({"sub": work_id})
        return {"success": True, "message": "ok", "token": token, "work_id": work_id}
    finally:
        conn.close()
