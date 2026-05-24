"""
Pydantic 数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional


# ==================== 认证 ====================
class LoginRequest(BaseModel):
    work_id: str = Field(..., description="工号")
    password: str = Field(..., description="密码")


class RegisterRequest(BaseModel):
    work_id: str = Field(..., description="工号")
    password: str = Field(..., description="密码（至少4位）")
    role: str = Field("doctor", description="角色：doctor（医生）/ admin（管理员）")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    work_id: str
    role: str = "doctor"


# ==================== 用户管理 ====================
class UserInfo(BaseModel):
    work_id: str
    role: str
    created_at: str


class UserListResponse(BaseModel):
    users: list
    total: int


# ==================== 诊断记录 ====================
class DiagnosisRecordCreate(BaseModel):
    patient_name: str = Field(..., description="患者姓名")
    id_number: str = Field("", description="身份证号")
    age: int = Field(0, ge=0, le=150)
    gender: str = Field("男", description="性别")
    symptoms: str = Field(..., description="主要症状或体征")
    notes: str = Field("", description="备注（过敏史/特殊状态）")
    examinations: str = Field("", description="进行的检查")
    diagnosis_result: str = Field(..., description="最终诊断结果")
    treatment_decision: str = Field("", description="诊断决策（用药等）")
    diagnosis_time: str = Field("", description="诊断时间")
    doctor: str = Field("", description="诊断人")


class DiagnosisRecordUpdate(BaseModel):
    patient_name: str = Field(..., description="患者姓名")
    id_number: str = Field("", description="身份证号")
    age: int = Field(0, ge=0, le=150)
    gender: str = Field("男", description="性别")
    symptoms: str = Field(..., description="主要症状或体征")
    notes: str = Field("", description="备注（过敏史/特殊状态）")
    examinations: str = Field("", description="进行的检查")
    diagnosis_result: str = Field(..., description="最终诊断结果")
    treatment_decision: str = Field("", description="诊断决策（用药等）")
    diagnosis_time: str = Field("", description="诊断时间")
    doctor: str = Field("", description="诊断人")


class DiagnosisRecordResponse(BaseModel):
    id: str
    patient_name: str
    id_number: str
    age: int
    gender: str
    symptoms: str
    notes: str
    examinations: str
    diagnosis_result: str
    treatment_decision: str
    diagnosis_time: str
    doctor: str
    create_time: str
    update_time: str


# ==================== 知识库 ====================
class KnowledgeBaseDocument(BaseModel):
    source: str
    chunk_count: int
    create_time: str
    operator: str
    sample_content: str


# ==================== 操作日志 ====================
class LogQueryParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    action_type: Optional[str] = None
    keyword: Optional[str] = None


class LogResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    records: list


# ==================== 仪表盘 ====================
class DashboardResponse(BaseModel):
    kb_stats: dict
    diag_stats: dict
    chat_stats: dict
    user_stats: dict


# ==================== 问答 ====================
class ChatRequest(BaseModel):
    input: str = Field(..., description="用户输入")
    session_id: str = Field("default", description="会话ID")


class ChatResponse(BaseModel):
    response: str


# ==================== 鉴别诊断 ====================
class DifferentialDiagnosisRequest(BaseModel):
    symptoms: str = Field(..., description="症状描述")
    age: int = Field(0, ge=0, le=150)
    gender: str = Field("未指定")


class DifferentialDiagnosisResponse(BaseModel):
    result: str
    pdf_bytes: Optional[str] = None  # Base64 encoded PDF


# ==================== 用药安全核查 ====================
class DrugSafetyRequest(BaseModel):
    drug_name: str = Field(..., description="药物名称")
    age: int = Field(0, ge=0, le=150)
    allergy: str = Field("", description="过敏史")
    notes: str = Field("", description="备注")


class DrugSafetyResponse(BaseModel):
    result: str
