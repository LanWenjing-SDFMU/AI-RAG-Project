"""
操作日志 API 路由
"""
from fastapi import APIRouter, Query, Depends
from ..services import log_service
from ..core.security import require_admin

router = APIRouter(prefix="/api/logs", tags=["操作日志"])


@router.get("/list")
async def get_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    action_type: str = Query(None, description="操作类型筛选"),
    keyword: str = Query(None, description="关键词搜索"),
    admin: str = Depends(require_admin),
):
    """获取操作日志列表（仅管理员）"""
    result = log_service.get_logs(
        page=page,
        page_size=page_size,
        action_type=action_type,
        keyword=keyword,
    )
    return result


@router.get("/stats")
async def get_log_stats(admin: str = Depends(require_admin)):
    """获取日志统计信息（仅管理员）"""
    today_count = log_service.get_today_count()
    type_stats = log_service.get_action_type_stats()
    return {
        "today_count": today_count,
        "type_stats": type_stats,
    }


@router.get("/action-types")
async def get_action_types(admin: str = Depends(require_admin)):
    """获取操作类型列表（仅管理员）"""
    return log_service.ACTION_TYPE_LABELS
