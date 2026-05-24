"""
用户管理服务
"""
from ..core.database import get_connection


def get_all_users() -> list[dict]:
    """获取所有用户列表"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT work_id, role, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def delete_user(work_id: str) -> bool:
    """删除指定用户"""
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM users WHERE work_id = ?", (work_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_user_count_by_role() -> dict:
    """按角色统计用户数"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT role, COUNT(*) as count FROM users GROUP BY role"
        ).fetchall()
        return {row["role"]: row["count"] for row in rows}
    finally:
        conn.close()
