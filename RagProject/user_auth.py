"""
用户认证模块
支持医生工号 + 密码的注册、登录、登出功能
数据存储于 SQLite 数据库
"""
import hashlib
from database import get_connection


def _hash_password(password: str) -> str:
    """对密码进行 SHA-256 哈希"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register(work_id: str, password: str) -> str:
    """
    注册新用户
    :param work_id: 工号
    :param password: 密码（明文）
    :return: 成功返回 "ok"，失败返回错误信息
    """
    work_id = work_id.strip()
    if not work_id:
        return "工号不能为空"
    if not password or len(password) < 4:
        return "密码长度不能少于4位"

    conn = get_connection()
    try:
        # 检查工号是否已存在
        row = conn.execute("SELECT work_id FROM users WHERE work_id = ?", (work_id,)).fetchone()
        if row:
            return f"工号「{work_id}」已存在，请直接登录"

        conn.execute(
            "INSERT INTO users (work_id, password) VALUES (?, ?)",
            (work_id, _hash_password(password)),
        )
        conn.commit()
        return "ok"
    finally:
        conn.close()


def login(work_id: str, password: str) -> str:
    """
    用户登录
    :param work_id: 工号
    :param password: 密码（明文）
    :return: 成功返回 "ok"，失败返回错误信息
    """
    work_id = work_id.strip()
    if not work_id:
        return "请输入工号"
    if not password:
        return "请输入密码"

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT password FROM users WHERE work_id = ?", (work_id,)
        ).fetchone()
        if row is None:
            return f"工号「{work_id}」不存在，请先注册"

        if row["password"] != _hash_password(password):
            return "密码错误"

        return "ok"
    finally:
        conn.close()


def user_exists(work_id: str) -> bool:
    """检查工号是否已注册"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT work_id FROM users WHERE work_id = ?", (work_id.strip(),)
        ).fetchone()
        return row is not None
    finally:
        conn.close()
