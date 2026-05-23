"""
诊断记录 API 路由
"""
from fastapi import APIRouter, HTTPException, Query
from ..models.schemas import DiagnosisRecordCreate, DiagnosisRecordUpdate
from ..services import diagnosis_service, log_service

router = APIRouter(prefix="/api/diagnosis", tags=["诊断记录"])


@router.get("/records")
async def get_records(search: str = Query("", description="搜索关键词")):
    """获取诊断记录列表"""
    if search:
        records = diagnosis_service.search_records(search)
    else:
        records = diagnosis_service.get_all_records()
    return {"records": records, "total": len(records)}


@router.get("/records/{record_id}")
async def get_record(record_id: str):
    """获取单条诊断记录"""
    record = diagnosis_service.get_record(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.post("/records")
async def create_record(record: DiagnosisRecordCreate, operator: str = Query("", description="操作人工号")):
    """新增诊断记录"""
    record_id = diagnosis_service.add_record(record.model_dump())
    log_service.add_log("record_crud", f"新增诊断记录：患者「{record.patient_name}」，ID: {record_id}", operator=operator)
    return {"id": record_id, "message": "记录已保存"}


@router.put("/records/{record_id}")
async def update_record(record_id: str, record: DiagnosisRecordUpdate, operator: str = Query("", description="操作人工号")):
    """更新诊断记录"""
    success = diagnosis_service.update_record(record_id, record.model_dump())
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    log_service.add_log("record_crud", f"编辑诊断记录：患者「{record.patient_name}」，ID: {record_id}", operator=operator)
    return {"message": "记录已更新"}


@router.delete("/records/{record_id}")
async def delete_record(record_id: str, operator: str = Query("", description="操作人工号")):
    """删除诊断记录"""
    success = diagnosis_service.delete_record(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    log_service.add_log("record_crud", f"删除诊断记录 ID: {record_id}", operator=operator)
    return {"message": "记录已删除"}


@router.post("/records/{record_id}/sync-kb")
async def sync_to_knowledge_base(record_id: str, operator: str = Query("", description="操作人工号")):
    """将诊断记录同步到知识库"""
    record = diagnosis_service.get_record(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="记录不存在")

    kb_text = diagnosis_service.format_record_for_knowledge_base(record)
    kb_filename = f"诊断记录_{record.get('patient_name', 'unknown')}_{record_id}.txt"

    from ..services.kb_service import KnowledgeBaseService
    ks = KnowledgeBaseService()
    result = ks.upload_by_str(kb_text, kb_filename, operator=operator)

    if "成功" in result:
        log_service.add_log("upload", f"诊断记录同步到知识库：{kb_filename}", operator=operator)
        return {"message": result, "success": True}
    elif "跳过" in result:
        return {"message": result, "success": True}
    else:
        return {"message": result, "success": False}
