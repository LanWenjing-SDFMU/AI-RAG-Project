"""
诊断报告 PDF 生成模块
使用 reportlab 生成结构化临床诊断报告
"""
import os
import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ===== 尝试注册中文字体 =====
# Windows 系统常见中文字体路径
_FONT_REGISTERED = False
_FONT_NAME = "Helvetica"

# 尝试注册微软雅黑
for font_path, font_name in [
    ("C:/Windows/Fonts/msyh.ttc", "MicrosoftYaHei"),
    ("C:/Windows/Fonts/msyhbd.ttc", "MicrosoftYaHeiBold"),
    ("C:/Windows/Fonts/simhei.ttf", "SimHei"),
    ("C:/Windows/Fonts/simsun.ttc", "SimSun"),
]:
    try:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            if not _FONT_REGISTERED:
                _FONT_NAME = font_name
                _FONT_REGISTERED = True
    except Exception:
        pass


def _get_styles():
    """获取样式集合"""
    styles = getSampleStyleSheet()

    # 标题样式
    styles.add(ParagraphStyle(
        name='ReportTitle',
        fontName=_FONT_NAME,
        fontSize=20,
        leading=28,
        alignment=TA_CENTER,
        textColor=HexColor('#1a3a6b'),
        spaceAfter=6,
        spaceBefore=0,
    ))

    # 副标题
    styles.add(ParagraphStyle(
        name='ReportSubtitle',
        fontName=_FONT_NAME,
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=HexColor('#97a8be'),
        spaceAfter=20,
        spaceBefore=0,
    ))

    # 章节标题
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontName=_FONT_NAME,
        fontSize=13,
        leading=18,
        alignment=TA_LEFT,
        textColor=HexColor('#1a3a6b'),
        spaceAfter=8,
        spaceBefore=16,
        borderPadding=(0, 0, 4, 0),
    ))

    # 字段标签（如 "患者姓名："）
    styles.add(ParagraphStyle(
        name='FieldLabel',
        fontName=_FONT_NAME,
        fontSize=10,
        leading=16,
        alignment=TA_LEFT,
        textColor=HexColor('#5a6a7e'),
        spaceAfter=2,
        spaceBefore=2,
    ))

    # 字段值
    styles.add(ParagraphStyle(
        name='FieldValue',
        fontName=_FONT_NAME,
        fontSize=10,
        leading=16,
        alignment=TA_LEFT,
        textColor=HexColor('#303133'),
        spaceAfter=2,
        spaceBefore=2,
    ))

    # 正文内容
    styles.add(ParagraphStyle(
        name='ReportBody',
        fontName=_FONT_NAME,
        fontSize=10,
        leading=16,
        alignment=TA_LEFT,
        textColor=HexColor('#303133'),
        spaceAfter=6,
        spaceBefore=2,
    ))

    # 页脚
    styles.add(ParagraphStyle(
        name='ReportFooter',
        fontName=_FONT_NAME,
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=HexColor('#c0c4cc'),
        spaceAfter=0,
        spaceBefore=0,
    ))

    return styles


def generate_diagnosis_report(
    symptoms: str,
    diagnosis_result: str,
    patient_info: dict = None,
    additional_sections: list = None,
) -> bytes:
    """
    生成诊断报告 PDF

    Args:
        symptoms: 患者症状描述
        diagnosis_result: 诊断结果/建议（支持 Markdown 风格文本）
        patient_info: 患者信息字典，可选字段：
            - name: 姓名
            - age: 年龄
            - gender: 性别
            - id_number: 身份证号
            - doctor: 诊断医生
        additional_sections: 附加章节列表，每项为 (标题, 内容) 元组

    Returns:
        PDF 文件的 bytes
    """
    buf = io.BytesIO()
    styles = _get_styles()

    # 创建文档
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=25 * mm,
        rightMargin=25 * mm,
    )

    story = []
    S = styles

    # ===== 标题区域 =====
    story.append(Paragraph("临床诊断报告", S['ReportTitle']))
    story.append(Paragraph(
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        S['ReportSubtitle']
    ))

    # 分隔线
    story.append(HRFlowable(
        width="100%",
        thickness=1,
        color=HexColor('#ebeef5'),
        spaceAfter=12,
        spaceBefore=0,
    ))

    # ===== 患者信息 =====
    if patient_info:
        story.append(Paragraph("患者信息", S['SectionTitle']))

        info_data = []
        info_fields = [
            ("患者姓名", patient_info.get("name", "")),
            ("年龄", str(patient_info.get("age", "")) if patient_info.get("age") else ""),
            ("性别", patient_info.get("gender", "")),
            ("身份证号", patient_info.get("id_number", "")),
            ("诊断医生", patient_info.get("doctor", "")),
        ]

        # 过滤空字段
        info_fields = [(label, val) for label, val in info_fields if val]

        # 两列布局
        row1, row2 = [], []
        for i, (label, val) in enumerate(info_fields):
            cell = Paragraph(
                f'<b>{label}：</b>{val}',
                S['FieldValue']
            )
            if i % 2 == 0:
                row1.append(cell)
            else:
                row2.append(cell)

        if row1:
            # 创建表格
            max_cols = max(len(row1), len(row2) if row2 else 0)
            table_data = []
            if row1:
                table_data.append(row1 + [Paragraph('', S['FieldValue'])] * (max_cols - len(row1)))
            if row2:
                table_data.append(row2 + [Paragraph('', S['FieldValue'])] * (max_cols - len(row2)))

            if table_data:
                t = Table(table_data, colWidths=[doc.width / max_cols] * max_cols)
                t.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                story.append(t)

        story.append(Spacer(1, 8))

    # ===== 主诉/症状 =====
    story.append(Paragraph("主诉与症状", S['SectionTitle']))
    story.append(Paragraph(symptoms.replace('\n', '<br/>'), S['ReportBody']))
    story.append(Spacer(1, 6))

    # ===== 诊断结果 =====
    story.append(Paragraph("诊断结果与建议", S['SectionTitle']))

    # 处理诊断结果中的 Markdown 格式
    formatted_result = diagnosis_result
    # 将 **text** 转为 <b>text</b>
    import re
    formatted_result = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', formatted_result)
    # 将 ## 标题转为加粗
    formatted_result = re.sub(r'^##\s+(.+)$', r'<b>\1</b>', formatted_result, flags=re.MULTILINE)
    # 将换行转为 <br/>
    formatted_result = formatted_result.replace('\n', '<br/>')

    story.append(Paragraph(formatted_result, S['ReportBody']))

    # ===== 附加章节 =====
    if additional_sections:
        for title, content in additional_sections:
            story.append(Spacer(1, 4))
            story.append(Paragraph(title, S['SectionTitle']))
            formatted_content = content.replace('\n', '<br/>')
            formatted_content = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', formatted_content)
            story.append(Paragraph(formatted_content, S['ReportBody']))

    # ===== 页脚 =====
    story.append(Spacer(1, 20))
    story.append(HRFlowable(
        width="100%",
        thickness=0.5,
        color=HexColor('#ebeef5'),
        spaceAfter=6,
        spaceBefore=0,
    ))
    story.append(Paragraph(
        "本报告由智能临床决策支持系统自动生成，仅供参考，不构成最终诊疗依据。",
        S['ReportFooter']
    ))
    story.append(Paragraph(
        f"智能临床决策支持系统 · {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        S['ReportFooter']
    ))

    # 生成 PDF
    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()

    return pdf_bytes
