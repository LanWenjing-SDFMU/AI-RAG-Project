"""
患者诊断记录管理模块
提供基于 SQLite 的增删改查（CRUD）功能
"""
import uuid
from datetime import datetime
from database import get_connection


def add_record(record: dict) -> str:
    """
    新增一条诊断记录
    返回记录ID
    """
    record_id = str(uuid.uuid4())[:8]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO diagnosis_records
               (id, patient_name, id_number, age, gender, symptoms, notes,
                examinations, diagnosis_result, treatment_decision,
                diagnosis_time, doctor, create_time, update_time)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                record_id,
                record.get("patient_name", ""),
                record.get("id_number", ""),
                record.get("age", 0),
                record.get("gender", ""),
                record.get("symptoms", ""),
                record.get("notes", ""),
                record.get("examinations", ""),
                record.get("diagnosis_result", ""),
                record.get("treatment_decision", ""),
                record.get("diagnosis_time", ""),
                record.get("doctor", ""),
                now,
                now,
            ),
        )
        conn.commit()
        return record_id
    finally:
        conn.close()


def update_record(record_id: str, updated_data: dict) -> bool:
    """
    更新指定ID的诊断记录
    返回是否更新成功
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        # 检查记录是否存在
        existing = conn.execute(
            "SELECT create_time FROM diagnosis_records WHERE id = ?", (record_id,)
        ).fetchone()
        if existing is None:
            return False

        conn.execute(
            """UPDATE diagnosis_records SET
               patient_name = ?, id_number = ?, age = ?, gender = ?,
               symptoms = ?, notes = ?, examinations = ?,
               diagnosis_result = ?, treatment_decision = ?,
               diagnosis_time = ?, doctor = ?, update_time = ?
               WHERE id = ?""",
            (
                updated_data.get("patient_name", ""),
                updated_data.get("id_number", ""),
                updated_data.get("age", 0),
                updated_data.get("gender", ""),
                updated_data.get("symptoms", ""),
                updated_data.get("notes", ""),
                updated_data.get("examinations", ""),
                updated_data.get("diagnosis_result", ""),
                updated_data.get("treatment_decision", ""),
                updated_data.get("diagnosis_time", ""),
                updated_data.get("doctor", ""),
                now,
                record_id,
            ),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def delete_record(record_id: str) -> bool:
    """
    删除指定ID的诊断记录
    返回是否删除成功
    """
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM diagnosis_records WHERE id = ?", (record_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_record(record_id: str) -> dict | None:
    """根据ID获取单条诊断记录"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM diagnosis_records WHERE id = ?", (record_id,)
        ).fetchone()
        if row is None:
            return None
        return dict(row)
    finally:
        conn.close()


def get_all_records() -> list[dict]:
    """获取所有诊断记录（按创建时间倒序）"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM diagnosis_records ORDER BY create_time DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def search_records(keyword: str) -> list[dict]:
    """
    根据关键词搜索诊断记录
    匹配字段：患者姓名、身份证号、主要症状、诊断结果
    """
    conn = get_connection()
    try:
        keyword = keyword.strip()
        if not keyword:
            rows = conn.execute(
                "SELECT * FROM diagnosis_records ORDER BY create_time DESC"
            ).fetchall()
            return [dict(row) for row in rows]

        like_pattern = f"%{keyword}%"
        rows = conn.execute(
            """SELECT * FROM diagnosis_records WHERE
               patient_name LIKE ? OR id_number LIKE ? OR
               symptoms LIKE ? OR diagnosis_result LIKE ?
               ORDER BY create_time DESC""",
            (like_pattern, like_pattern, like_pattern, like_pattern),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def format_record_for_knowledge_base(record: dict) -> str:
    """
    将一条诊断记录格式化为知识库文本
    用于同步到向量知识库
    """
    lines = []
    lines.append("【患者诊断记录】")
    lines.append(f"患者姓名：{record.get('patient_name', '')}")
    lines.append(f"身份证号：{record.get('id_number', '')}")
    lines.append(f"年龄：{record.get('age', '')}")
    lines.append(f"性别：{record.get('gender', '')}")
    lines.append(f"主要症状或体征：{record.get('symptoms', '')}")
    lines.append(f"备注（过敏史/特殊状态）：{record.get('notes', '')}")
    lines.append(f"进行的检查：{record.get('examinations', '')}")
    lines.append(f"最终诊断结果：{record.get('diagnosis_result', '')}")
    lines.append(f"诊断决策（用药等）：{record.get('treatment_decision', '')}")
    lines.append(f"诊断时间：{record.get('diagnosis_time', '')}")
    lines.append(f"诊断人：{record.get('doctor', '')}")
    lines.append(f"记录创建时间：{record.get('create_time', '')}")
    return "\n".join(lines)
