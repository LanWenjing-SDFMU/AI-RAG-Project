"""
SQLite 数据库核心模块
"""
import os
import sqlite3
from .config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ==================== 建表 SQL ====================

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    work_id     TEXT PRIMARY KEY,
    password    TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
"""

CREATE_DIAGNOSIS_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS diagnosis_records (
    id               TEXT PRIMARY KEY,
    patient_name     TEXT NOT NULL,
    id_number        TEXT DEFAULT '',
    age              INTEGER DEFAULT 0,
    gender           TEXT DEFAULT '',
    symptoms         TEXT DEFAULT '',
    notes            TEXT DEFAULT '',
    examinations     TEXT DEFAULT '',
    diagnosis_result TEXT DEFAULT '',
    treatment_decision TEXT DEFAULT '',
    diagnosis_time   TEXT DEFAULT '',
    doctor           TEXT DEFAULT '',
    create_time      TEXT NOT NULL,
    update_time      TEXT NOT NULL
);
"""

CREATE_OPERATION_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS operation_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    time        TEXT NOT NULL,
    action_type TEXT NOT NULL,
    detail      TEXT NOT NULL,
    operator    TEXT DEFAULT '',
    status      TEXT DEFAULT 'success'
);
"""

CREATE_CHAT_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS chat_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    type        TEXT NOT NULL,
    content     TEXT NOT NULL,
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
