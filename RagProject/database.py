"""
SQLite 数据库核心模块
提供统一的数据库连接、表创建、数据迁移（从 JSON 文件导入）功能
"""
import os
import json
import sqlite3
import hashlib
from datetime import datetime
from typing import Optional

import config_data as config


def get_connection() -> sqlite3.Connection:
    """
    获取数据库连接（每次调用返回新连接，线程安全）
    Returns:
        sqlite3.Connection 对象（row_factory 已设置为 sqlite3.Row）
    """
    os.makedirs(os.path.dirname(config.db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ==================== 建表 ====================

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    work_id     TEXT PRIMARY KEY,          -- 工号（唯一标识）
    password    TEXT NOT NULL,              -- SHA-256 哈希密码
    created_at  TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
"""

CREATE_DIAGNOSIS_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS diagnosis_records (
    id               TEXT PRIMARY KEY,      -- UUID 前8位
    patient_name     TEXT NOT NULL,          -- 患者姓名
    id_number        TEXT DEFAULT '',        -- 身份证号
    age              INTEGER DEFAULT 0,      -- 年龄
    gender           TEXT DEFAULT '',        -- 性别
    symptoms         TEXT DEFAULT '',        -- 主要症状或体征
    notes            TEXT DEFAULT '',        -- 备注（过敏史/特殊状态）
    examinations     TEXT DEFAULT '',        -- 进行的检查
    diagnosis_result TEXT DEFAULT '',        -- 最终诊断结果
    treatment_decision TEXT DEFAULT '',      -- 诊断决策（用药等）
    diagnosis_time   TEXT DEFAULT '',        -- 诊断时间
    doctor           TEXT DEFAULT '',        -- 诊断人
    create_time      TEXT NOT NULL,          -- 记录创建时间
    update_time      TEXT NOT NULL           -- 记录更新时间
);
"""

CREATE_OPERATION_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS operation_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    time        TEXT NOT NULL,               -- 操作时间
    action_type TEXT NOT NULL,               -- 操作类型
    detail      TEXT NOT NULL,               -- 操作详情
    operator    TEXT DEFAULT '',             -- 操作人工号
    status      TEXT DEFAULT 'success'       -- 操作状态
);
"""

CREATE_CHAT_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS chat_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,               -- 会话ID
    type        TEXT NOT NULL,               -- 消息类型（human / ai）
    content     TEXT NOT NULL,               -- 消息内容
    created_at  TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
"""

CREATE_CHAT_HISTORY_INDEX = """
CREATE INDEX IF NOT EXISTS idx_chat_history_session ON chat_history(session_id);
"""


def init_database():
    """初始化数据库，创建所有表"""
    conn = get_connection()
    try:
        conn.execute(CREATE_USERS_TABLE)
        conn.execute(CREATE_DIAGNOSIS_RECORDS_TABLE)
        conn.execute(CREATE_OPERATION_LOGS_TABLE)
        conn.execute(CREATE_CHAT_HISTORY_TABLE)
        conn.execute(CREATE_CHAT_HISTORY_INDEX)
        conn.commit()
        print("[数据库] 表结构初始化完成")
    finally:
        conn.close()


# ==================== 数据迁移（从 JSON 文件导入） ====================

def _hash_password(password: str) -> str:
    """SHA-256 哈希"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def migrate_users_from_json(json_path: str = None):
    """
    从 users.json 迁移用户数据到 SQLite
    Args:
        json_path: users.json 路径，默认 config.USERS_JSON_PATH
    """
    if json_path is None:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
    if not os.path.exists(json_path):
        print("[迁移] users.json 不存在，跳过")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        users = json.load(f)

    conn = get_connection()
    try:
        count = 0
        for work_id, user_data in users.items():
            conn.execute(
                "INSERT OR IGNORE INTO users (work_id, password) VALUES (?, ?)",
                (work_id, user_data.get("password", _hash_password(""))),
            )
            count += 1
        conn.commit()
        print(f"[迁移] 用户数据迁移完成，共 {count} 条")
    finally:
        conn.close()


def migrate_diagnosis_from_json(json_path: str = None):
    """
    从 diagnosis_records.json 迁移诊断记录到 SQLite
    """
    if json_path is None:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagnosis_records.json")
    if not os.path.exists(json_path):
        print("[迁移] diagnosis_records.json 不存在，跳过")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    conn = get_connection()
    try:
        count = 0
        for rec in records:
            conn.execute(
                """INSERT OR REPLACE INTO diagnosis_records
                   (id, patient_name, id_number, age, gender, symptoms, notes,
                    examinations, diagnosis_result, treatment_decision,
                    diagnosis_time, doctor, create_time, update_time)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    rec.get("id", ""),
                    rec.get("patient_name", ""),
                    rec.get("id_number", ""),
                    rec.get("age", 0),
                    rec.get("gender", ""),
                    rec.get("symptoms", ""),
                    rec.get("notes", ""),
                    rec.get("examinations", ""),
                    rec.get("diagnosis_result", ""),
                    rec.get("treatment_decision", ""),
                    rec.get("diagnosis_time", ""),
                    rec.get("doctor", ""),
                    rec.get("create_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    rec.get("update_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                ),
            )
            count += 1
        conn.commit()
        print(f"[迁移] 诊断记录迁移完成，共 {count} 条")
    finally:
        conn.close()


def migrate_logs_from_json(json_path: str = None):
    """
    从 operation_log.json 迁移操作日志到 SQLite
    """
    if json_path is None:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "operation_log.json")
    if not os.path.exists(json_path):
        print("[迁移] operation_log.json 不存在，跳过")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        logs = json.load(f)

    conn = get_connection()
    try:
        count = 0
        for log in logs:
            conn.execute(
                "INSERT INTO operation_logs (time, action_type, detail, operator, status) VALUES (?, ?, ?, ?, ?)",
                (
                    log.get("time", ""),
                    log.get("action_type", ""),
                    log.get("detail", ""),
                    log.get("operator", ""),
                    log.get("status", "success"),
                ),
            )
            count += 1
        conn.commit()
        print(f"[迁移] 操作日志迁移完成，共 {count} 条")
    finally:
        conn.close()


def migrate_chat_history_from_json(chat_dir: str = None):
    """
    从 chat_history/*.json 迁移聊天历史到 SQLite
    """
    if chat_dir is None:
        chat_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history")
    if not os.path.exists(chat_dir):
        print("[迁移] chat_history 目录不存在，跳过")
        return

    conn = get_connection()
    try:
        total = 0
        for fname in os.listdir(chat_dir):
            if not fname.endswith(".json"):
                continue
            session_id = fname.replace(".json", "")
            fpath = os.path.join(chat_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                messages = json.load(f)
            for msg in messages:
                msg_type = msg.get("type", "")
                msg_data = msg.get("data", {})
                content = msg_data.get("content", "") if isinstance(msg_data, dict) else str(msg_data)
                conn.execute(
                    "INSERT INTO chat_history (session_id, type, content) VALUES (?, ?, ?)",
                    (session_id, msg_type, content),
                )
                total += 1
        conn.commit()
        print(f"[迁移] 聊天历史迁移完成，共 {total} 条消息")
    finally:
        conn.close()


def run_all_migrations():
    """执行所有数据迁移"""
    print("=" * 50)
    print("开始数据迁移（JSON → SQLite）")
    print("=" * 50)
    migrate_users_from_json()
    migrate_diagnosis_from_json()
    migrate_logs_from_json()
    migrate_chat_history_from_json()
    print("=" * 50)
    print("数据迁移完成")
    print("=" * 50)


if __name__ == '__main__':
    init_database()
    run_all_migrations()
