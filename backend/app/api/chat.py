"""
智能问答 API 路由
"""
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..models.schemas import ChatRequest, ChatResponse
from ..services.rag_service import RagService
from ..services import log_service
from ..rag.file_history_store import FileChatMessageHistory

router = APIRouter(prefix="/api/chat", tags=["智能问答"])


@router.post("/qa")
async def chat(req: ChatRequest, operator: str = ""):
    """智能临床问答（流式输出）"""
    try:
        rag = RagService()
        log_service.add_log("qa_chat", f"智能问答：{req.input[:50]}", operator=operator)

        async def generate():
            async for chunk in rag.chat_stream(req.input, req.session_id):
                yield json.dumps({"response": chunk}, ensure_ascii=False) + "\n"

        return StreamingResponse(generate(), media_type="application/x-ndjson")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答服务出错: {str(e)}")


@router.post("/clear-history")
async def clear_history(session_id: str = "default", operator: str = ""):
    """清空指定会话的历史记录"""
    try:
        history = FileChatMessageHistory(session_id=session_id)
        history.clear()
        log_service.add_log("qa_chat", f"清空会话历史记录：{session_id}", operator=operator)
        return {"message": f"会话 {session_id} 的历史记录已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空历史记录出错: {str(e)}")
