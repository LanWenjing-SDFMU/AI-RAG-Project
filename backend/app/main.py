"""
智能临床决策助手 - FastAPI 后端入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.database import init_database
from .api import auth, dashboard, diagnosis, knowledge_base, chat, diagnosis_assist, drug_safety, logs

# 初始化数据库
init_database()

app = FastAPI(
    title="智能临床决策助手 API",
    description="基于 RAG 技术的临床辅助决策平台后端接口",
    version="1.0.0",
)

# CORS 配置 - 允许前端开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(diagnosis.router)
app.include_router(knowledge_base.router)
app.include_router(chat.router)
app.include_router(diagnosis_assist.router)
app.include_router(drug_safety.router)
app.include_router(logs.router)


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "智能临床决策助手 API 运行正常"}
