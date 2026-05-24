"""
用户管理 API 路由（管理员专用）
"""
from fastapi import APIRouter, HTTPException, Depends
from ..services import user_service, log_service
from ..core.security import require_admin

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("/list")
async def get_users(admin: str = Depends(require_admin)):
    """获取所有用户列表（仅管理员）"""
    users = user_service.get_all_users()
    return {"users": users, "total": len(users)}


@router.delete("/{work_id}")
async def delete_user(
    work_id: str,
    admin: str = Depends(require_admin),
):
    """删除指定用户（仅管理员，不能删除自己）"""
    if work_id == admin:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")

    success = user_service.delete_user(work_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"用户「{work_id}」不存在")

    log_service.add_log("user_management", f"管理员 {admin} 删除了用户「{work_id}」", operator=admin)
    return {"message": f"用户「{work_id}」已删除", "success": True}
