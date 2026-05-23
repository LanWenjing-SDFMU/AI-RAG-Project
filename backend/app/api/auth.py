"""
认证 API 路由
"""
from fastapi import APIRouter, HTTPException
from ..models.schemas import LoginRequest, RegisterRequest, TokenResponse
from ..services import auth_service, log_service

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login")
async def login(req: LoginRequest):
    """用户登录"""
    result = auth_service.login(req.work_id, req.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])

    log_service.add_log("login", f"用户登录系统", operator=req.work_id)
    return {
        "access_token": result["token"],
        "token_type": "bearer",
        "work_id": result["work_id"],
    }


@router.post("/register")
async def register(req: RegisterRequest):
    """用户注册"""
    result = auth_service.register(req.work_id, req.password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    log_service.add_log("register", f"新用户注册成功", operator=req.work_id)
    return {"message": "注册成功，请登录"}
