"""
RAG 模块配置
路径基于当前文件位置计算绝对路径，确保无论工作目录如何都能正确找到数据文件
"""
import os

# 当前文件所在目录: backend/app/rag/
_RAG_DIR = os.path.dirname(os.path.abspath(__file__))
# backend/ 目录
_BACKEND_DIR = os.path.dirname(os.path.dirname(_RAG_DIR))
# 项目根目录
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)

# MD5去重记录文件路径（用于存储已处理文件的MD5值）
md5_path = os.path.join(_BACKEND_DIR, "md5.txt")

# Chroma向量数据库配置
collection_name = "rag"
persist_directory = os.path.join(_BACKEND_DIR, "chroma_db")

# ==================== SQLite 数据库配置 ====================
db_path = os.path.join(_BACKEND_DIR, "app_data.db")  # SQLite 数据库文件路径

# 旧 JSON 文件路径（用于数据迁移）
users_json_path = os.path.join(_BACKEND_DIR, "users.json")
diagnosis_json_path = os.path.join(_BACKEND_DIR, "diagnosis_records.json")
logs_json_path = os.path.join(_BACKEND_DIR, "operation_log.json")
chat_history_dir = os.path.join(_BACKEND_DIR, "chat_history")

# 文本分割器配置
chunk_size = 500
chunk_overlap = 50
separators = ["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
max_split_char_number = 200

similarity_threshold = 5

embedding_model_name = "text-embedding-v4"
chat_model_name = "qwen3-max"

session_config = {
    "configurable": {
        "session_id": "user_001",
    }
}
