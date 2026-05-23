"""
操作日志服务
"""
from datetime import datetime, timedelta
from ..core.database import get_connection

_MAX_LOG_ENTRIES = 10000

ACTION_TYPE_LABELS = {
    "login": "登录系统",
    "logout": "退出登录",
    "register": "注册账号",
    "upload": "上传知识库",
    "kb_delete": "删除知识库文档",
    "diagnosis": "鉴别诊断",
    "drug_safety": "用药安全核查",
    "record_crud": "诊断记录操作",
    "pdf_export": "导出PDF报告",
    "qa_chat": "智能问答",
}


def add_log(action_type: str, detail: str, operator: str = "", status: str = "success") -> None:
    """添加一条操作日志"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO operation_logs (time, action_type, detail, operator, status) VALUES (?, ?, ?, ?, ?)",
            (now, action_type, detail, operator, status),
        )
        conn.commit()
        _trim_logs(conn)
    finally:
        conn.close()


def _trim_logs(conn):
    """保留最近 _MAX_LOG_ENTRIES 条日志"""
    conn.execute(
        f"DELETE FROM operation_logs WHERE id NOT IN (SELECT id FROM operation_logs ORDER BY id DESC LIMIT {_MAX_LOG_ENTRIES})"
    )
    conn.commit()


def get_logs(page: int = 1, page_size: int = 50, action_type: str = None, keyword: str = None) -> dict:
    """分页查询操作日志"""
    conn = get_connection()
    try:
        conditions = []
        params = []

        if action_type:
            conditions.append("action_type = ?")
            params.append(action_type)
        if keyword:
            conditions.append("(detail LIKE ? OR operator LIKE ?)")
            like_pattern = f"%{keyword}%"
            params.append(like_pattern)
            params.append(like_pattern)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        count_row = conn.execute(
            f"SELECT COUNT(*) as cnt FROM operation_logs WHERE {where_clause}", params
        ).fetchone()
        total = count_row["cnt"]

        total_pages = max(1, (total + page_size - 1) // page_size)
        page = max(1, min(page, total_pages))
        offset = (page - 1) * page_size

        rows = conn.execute(
            f"SELECT * FROM operation_logs WHERE {where_clause} ORDER BY time DESC LIMIT ? OFFSET ?",
            params + [page_size, offset],
        ).fetchall()

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "records": [dict(row) for row in rows],
        }
    finally:
        conn.close()


def get_action_type_stats() -> list[dict]:
    """获取各操作类型的统计"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT action_type as type, COUNT(*) as count FROM operation_logs GROUP BY action_type ORDER BY count DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_today_count() -> int:
    """获取今日操作次数"""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM operation_logs WHERE time LIKE ?",
            (f"{today}%",),
        ).fetchone()
        return row["cnt"]
    finally:
        conn.close()
