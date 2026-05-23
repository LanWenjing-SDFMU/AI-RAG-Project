# MD5去重记录文件路径（用于存储已处理文件的MD5值）
md5_path = "./md5.txt"

# Chroma向量数据库配置
collection_name = "rag"
persist_directory = "./chroma_db"

# ==================== SQLite 数据库配置 ====================
db_path = "./app_data.db"                # SQLite 数据库文件路径

# 旧 JSON 文件路径（用于数据迁移）
users_json_path = "./users.json"
diagnosis_json_path = "./diagnosis_records.json"
logs_json_path = "./operation_log.json"
chat_history_dir = "./chat_history"

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