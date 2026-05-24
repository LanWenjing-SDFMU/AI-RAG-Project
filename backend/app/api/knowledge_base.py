"""
知识库 API 路由
"""
import os
import tempfile
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Depends
from ..services import kb_service, log_service
from ..core.security import require_admin

router = APIRouter(prefix="/api/knowledge-base", tags=["知识库"])


@router.get("/documents")
async def get_documents(admin: str = Depends(require_admin)):
    """获取知识库文档列表（仅管理员）"""
    ks = kb_service.KnowledgeBaseService()
    docs = ks.get_all_documents()
    return {"documents": docs, "total": len(docs)}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    operator: str = Form("", description="操作人工号"),
    admin: str = Depends(require_admin),
):
    """上传文件到知识库（仅管理员）"""
    # 读取文件内容
    content_bytes = await file.read()
    file_name = file.filename or "unknown"
    file_ext = file_name.split(".")[-1].lower() if "." in file_name else "unknown"

    # 提取文本内容
    text_content = ""
    if file_ext in ["txt", "md"]:
        text_content = content_bytes.decode("utf-8", errors="replace")
    elif file_ext == "pdf":
        try:
            from PyPDF2 import PdfReader
            import io
            reader = PdfReader(io.BytesIO(content_bytes))
            texts = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    texts.append(t)
            text_content = "\n".join(texts)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF 解析失败: {str(e)}")
    elif file_ext == "docx":
        try:
            from docx import Document
            import io
            doc = Document(io.BytesIO(content_bytes))
            texts = [p.text for p in doc.paragraphs if p.text.strip()]
            text_content = "\n".join(texts)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"DOCX 解析失败: {str(e)}")
    else:
        # 兜底：按 UTF-8 文本处理
        text_content = content_bytes.decode("utf-8", errors="replace")

    if not text_content.strip():
        raise HTTPException(status_code=400, detail="无法提取文件内容")

    # 上传到知识库
    ks = kb_service.KnowledgeBaseService()
    result = ks.upload_by_str(text_content, file_name, operator=operator)

    if "成功" in result:
        log_service.add_log("upload", f"上传文件「{file_name}」成功", operator=operator)
        return {"message": result, "success": True}
    elif "跳过" in result:
        log_service.add_log("upload", f"文件「{file_name}」已存在，自动跳过", operator=operator, status="warning")
        return {"message": result, "success": True}
    else:
        return {"message": result, "success": False}


@router.delete("/documents/{source_name}")
async def delete_document(
    source_name: str,
    operator: str = Query("", description="操作人工号"),
    admin: str = Depends(require_admin),
):
    """删除知识库文档（仅管理员）"""
    ks = kb_service.KnowledgeBaseService()
    result = ks.delete_document(source_name)

    if "成功" in result:
        log_service.add_log("kb_delete", f"删除知识库文档「{source_name}」", operator=operator)
        return {"message": result, "success": True}
    else:
        return {"message": result, "success": False}
