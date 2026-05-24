"""
仪表盘数据服务
"""
from ..core.database import get_connection


def get_kb_stats(vector_store=None) -> dict:
    """获取知识库统计信息"""
    stats = {"total_chunks": 0, "source_distribution": []}
    if vector_store is None:
        return stats
    try:
        collection_data = vector_store._collection.get()
        metadatas = collection_data.get("metadatas", [])
        stats["total_chunks"] = len(metadatas)

        from collections import Counter
        source_counter = Counter()
        for meta in metadatas:
            source = meta.get("source", "未知")
            source_counter[source] += 1

        stats["source_distribution"] = [
            {"name": name, "count": count}
            for name, count in source_counter.most_common()
        ]
    except Exception:
        pass
    return stats


def get_diagnosis_stats() -> dict:
    """获取诊断记录统计信息"""
    stats = {
        "total_records": 0,
        "disease_distribution": [],
        "daily_trend": [],
        "doctor_distribution": [],
    }

    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) as cnt FROM diagnosis_records").fetchone()
        stats["total_records"] = row["cnt"]

        disease_rows = conn.execute(
            """SELECT diagnosis_result as name, COUNT(*) as count
               FROM diagnosis_records
               WHERE diagnosis_result != ''
               GROUP BY diagnosis_result
               ORDER BY count DESC LIMIT 8"""
        ).fetchall()
        stats["disease_distribution"] = [dict(r) for r in disease_rows]

        # 查询所有日期的诊断记录数，按日期降序取最近7天
        date_rows = conn.execute(
            """SELECT SUBSTR(create_time, 1, 10) as date, COUNT(*) as count
               FROM diagnosis_records
               GROUP BY date
               ORDER BY date DESC
               LIMIT 7"""
        ).fetchall()
        # 反转回升序排列
        stats["daily_trend"] = [dict(r) for r in reversed(date_rows)]

        doctor_rows = conn.execute(
            """SELECT doctor as name, COUNT(*) as count
               FROM diagnosis_records
               WHERE doctor != ''
               GROUP BY doctor
               ORDER BY count DESC"""
        ).fetchall()
        stats["doctor_distribution"] = [dict(r) for r in doctor_rows]
    except Exception:
        pass
    finally:
        conn.close()

    return stats


def get_chat_stats() -> dict:
    """获取聊天历史统计信息"""
    stats = {"total_sessions": 0, "total_messages": 0}
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(DISTINCT session_id) as sessions, COUNT(*) as messages FROM chat_history"
        ).fetchone()
        stats["total_sessions"] = row["sessions"]
        stats["total_messages"] = row["messages"]
    except Exception:
        pass
    finally:
        conn.close()
    return stats


def get_user_stats() -> dict:
    """获取用户统计信息"""
    stats = {"total_users": 0}
    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
        stats["total_users"] = row["cnt"]
    except Exception:
        pass
    finally:
        conn.close()
    return stats
