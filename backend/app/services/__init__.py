"""
服务层 - 业务逻辑实现
"""
import os
import sys

# 确保 RagProject 路径在 sys.path 中（uvicorn 子进程需要）
_rag_project_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "RagProject")
if _rag_project_path not in sys.path:
    sys.path.insert(0, _rag_project_path)
