"""
仪表盘 API 路由
"""
from fastapi import APIRouter, Depends
from ..services import dashboard_service, kb_service
from ..core.database import get_connection

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("/stats")
async def get_dashboard_stats():
    """获取仪表盘统计数据"""
    # 获取向量存储对象
    try:
        ks = kb_service.KnowledgeBaseService()
        vector_store = ks.get_vector_store()
    except Exception:
        vector_store = None

    kb_stats = dashboard_service.get_kb_stats(vector_store)
    diag_stats = dashboard_service.get_diagnosis_stats()
    chat_stats = dashboard_service.get_chat_stats()
    user_stats = dashboard_service.get_user_stats()

    return {
        "kb_stats": kb_stats,
        "diag_stats": diag_stats,
        "chat_stats": chat_stats,
        "user_stats": user_stats,
    }
