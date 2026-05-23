"""
应用配置
"""
import os

# backend 目录（当前文件在 backend/app/core/config.py，向上三级到 backend/）
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== 数据库配置 ====================
DB_PATH = os.path.join(BACKEND_DIR, "app_data.db")

# ==================== Chroma 向量数据库配置 ====================
COLLECTION_NAME = "rag"
PERSIST_DIRECTORY = os.path.join(BACKEND_DIR, "chroma_db")
MD5_PATH = os.path.join(BACKEND_DIR, "md5.txt")

# ==================== 文本分割器配置 ====================
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
SEPARATORS = ["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
MAX_SPLIT_CHAR_NUMBER = 200
SIMILARITY_THRESHOLD = 5

# ==================== 模型配置 ====================
EMBEDDING_MODEL_NAME = "text-embedding-v4"
CHAT_MODEL_NAME = "qwen3-max"

# ==================== JWT 配置 ====================
SECRET_KEY = "clinical-decision-assistant-secret-key-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8小时

# ==================== 聊天历史配置 ====================
CHAT_HISTORY_DIR = os.path.join(BACKEND_DIR, "chat_history")
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
