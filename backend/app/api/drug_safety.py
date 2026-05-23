"""
用药安全核查 API 路由
"""
from fastapi import APIRouter, HTTPException
from ..models.schemas import DrugSafetyRequest, DrugSafetyResponse
from ..services.rag_service import RagService
from ..services import log_service

router = APIRouter(prefix="/api/drug-safety", tags=["用药安全核查"])


@router.post("/check")
async def check_drug_safety(req: DrugSafetyRequest, operator: str = ""):
    """用药安全核查"""
    if not req.drug_name.strip():
        raise HTTPException(status_code=400, detail="请填写药物名称")

    rag = RagService()
    result = rag.drug_safety_check(req.drug_name, req.age, req.allergy, req.notes)

    log_service.add_log("drug_safety", f"用药安全核查：药物「{req.drug_name.strip()}」", operator=operator)
    return {"result": result}
