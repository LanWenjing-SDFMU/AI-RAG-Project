"""
诊断报告 PDF 生成服务
复用 app.rag 中的 report_generator 模块
"""
from app.rag.report_generator import generate_diagnosis_report as _original_generate
# 直接复用原有函数
generate_diagnosis_report = _original_generate
