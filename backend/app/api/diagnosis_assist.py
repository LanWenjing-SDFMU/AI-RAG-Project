"""
鉴别诊断辅助 API 路由
"""
import base64
import io
from fastapi import APIRouter, HTTPException
from ..models.schemas import DifferentialDiagnosisRequest, DifferentialDiagnosisResponse
from ..services.rag_service import RagService
from ..services import log_service

router = APIRouter(prefix="/api/diagnosis-assist", tags=["鉴别诊断"])


@router.post("/generate")
async def generate_differential_diagnosis(req: DifferentialDiagnosisRequest, operator: str = ""):
    """生成鉴别诊断"""
    if not req.symptoms.strip():
        raise HTTPException(status_code=400, detail="请至少输入一个症状或体征")

    query_parts = [f"患者症状：{req.symptoms.strip()}"]
    if req.age > 0:
        query_parts.append(f"年龄：{req.age}岁")
    if req.gender != "未指定":
        query_parts.append(f"性别：{req.gender}")

    query = "，".join(query_parts)
    query += """

请根据临床指南知识库，输出以下内容（用Markdown格式，分小节）：

## 📋 可能的疾病列表
（按可能性排序，每个疾病附上简要依据）

## 🔬 关键检查项目
（针对上述疾病需要做的检查）

## 📝 鉴别诊断要点
（如何区分这些疾病）

请严格基于提供的参考资料进行推理，不要编造。如果知识库中没有足够信息，请明确告知。"""

    rag = RagService()
    result = rag.diagnose(query)

    if "错误" not in result:
        log_service.add_log("diagnosis", f"生成鉴别诊断：症状「{req.symptoms.strip()[:50]}」", operator=operator)
    else:
        log_service.add_log("diagnosis", f"鉴别诊断生成失败", operator=operator, status="error")

    # 生成 PDF
    try:
        from ..services.report_service import generate_diagnosis_report
        pdf_bytes = generate_diagnosis_report(
            symptoms=req.symptoms.strip(),
            diagnosis_result=result,
            patient_info={
                "name": "",
                "age": str(req.age) if req.age > 0 else "",
                "gender": req.gender if req.gender != "未指定" else "",
                "doctor": operator,
            }
        )
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    except Exception:
        pdf_b64 = None

    return {"result": result, "pdf_bytes": pdf_b64}
