"""
基于StreamLit完成WEB网页上传服务
已去除中间白色矩形（上传卡片背景、阴影等）
"""
import streamlit as st
from knowledge_base import KnowledgeBaseService
import time
import os
import config_data as config
import datetime

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="知识库管理系统",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 自定义CSS样式 ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    /* 去除了白色矩形背景、阴影和圆角 */
    .upload-card {
        /* 背景色已移除，变为透明 */
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .history-card {
        /* 保留样式但去除了背景和阴影 */
        padding: 1rem;
        margin-top: 1rem;
    }
    .info-box {
        border-left: 5px solid #2a5298;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        background-color: transparent; /* 确保无白色背景 */
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        font-size: 0.8rem;
        color: #6c757d;
        border-top: 1px solid #dee2e6;
    }
    .stButton > button {
        background-color: #2a5298;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #1e3c72;
        color: white;
    }
    /* 去除 st.expander 内容区域的白色背景 */
    .streamlit-expanderContent {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 初始化服务和状态 ====================
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()
if "upload_history" not in st.session_state:
    st.session_state["upload_history"] = []  # 存储 (文件名, 状态, 时间)

# 获取向量库中文档数量（可选）
try:
    collection = st.session_state["service"].chroma._collection
    doc_count = collection.count()
except Exception:
    doc_count = "未知"

# ==================== 侧边栏 ====================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/medical-doctor.png", width=80)
    st.markdown("## 📋 系统状态")
    st.metric("📚 向量库文档片段数", doc_count)
    st.markdown("---")
    st.markdown("### 📌 操作指南")
    st.markdown("""
    1. 支持 **.txt** 格式文件
    2. 文件内容会自动分块并向量化
    3. 系统基于MD5自动去重
    4. 上传成功后可用于智能问答
    """)
    st.markdown("---")
    st.caption("© 2026 智能临床决策支持系统")

# ==================== 主区域 ====================
# 头部
st.markdown("""
<div class="main-header">
    <h1>📚 知识库更新服务</h1>
    <p>智能临床知识管理 · 支持文本向量化与去重上传</p>
</div>
""", unsafe_allow_html=True)

# 上传卡片（已去除白色矩形背景）
with st.container():
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        uploader_file = st.file_uploader(
            label="**请选择要上传的TXT文件**",
            type=['txt'],
            accept_multiple_files=False,
            help="仅支持UTF-8编码的TXT文件，文件内容将作为知识库检索来源"
        )
    with col2:
        st.markdown("#### 💡 提示")
        st.caption("上传后系统将自动提取文本、分块并生成向量索引。重复文件会被自动跳过。")
    st.markdown('</div>', unsafe_allow_html=True)

# 处理上传文件
if uploader_file is not None:
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024

    # 显示文件详细信息
    with st.expander("📄 文件详情", expanded=True):
        col_info1, col_info2, col_info3 = st.columns(3)
        col_info1.metric("文件名", file_name)
        col_info2.metric("文件类型", file_type)
        col_info3.metric("文件大小", f"{file_size:.2f} KB")

        content = uploader_file.read().decode("utf-8")
        with st.expander("🔍 内容预览（前500字符）"):
            st.text(content[:500] + ("..." if len(content) > 500 else ""))

    # 执行上传（带状态反馈）
    with st.status("⏳ 处理中...", expanded=True) as status:
        st.write(f"正在检查文件 `{file_name}` 的MD5...")
        time.sleep(0.5)

        result = st.session_state["service"].upload_by_str(content, file_name)

        if "成功" in result:
            status.update(label="✅ 上传成功", state="complete", expanded=False)
            st.toast(f"🎉 {result}", icon="✅")
        elif "跳过" in result:
            status.update(label="⚠️ 文件已存在", state="complete", expanded=False)
            st.toast(f"ℹ️ {result}", icon="⚠️")
        else:
            status.update(label="❌ 上传失败", state="error", expanded=False)
            st.toast(f"❌ {result}", icon="❌")

        # 记录历史（加入时间戳）
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.upload_history.append((file_name, result, now))

        if "成功" in result:
            st.success(result)
        elif "跳过" in result:
            st.info(result)
        else:
            st.error(result)

    # 显示更新后的向量库计数
    try:
        new_count = st.session_state["service"].chroma._collection.count()
        st.caption(f"📊 当前向量库总片段数：{new_count}")
    except:
        pass

# ==================== 最近上传记录（主区域下方，实时显示） ====================
st.markdown("---")
st.markdown("### 🕒 最近上传记录")
if st.session_state.upload_history:
    # 倒序显示最新的5条
    history_display = st.session_state.upload_history[::-1][:5]
    for file, status, timestamp in history_display:
        if "成功" in status:
            icon = "✅"
        elif "跳过" in status:
            icon = "⚠️"
        else:
            icon = "❌"
        st.markdown(f"{icon} **{file}** – {status} – `{timestamp}`")
else:
    st.info("暂无上传记录，请上传TXT文件。")

# 页脚
st.markdown('<div class="footer">© 2026智能临床决策支持系统 | 知识库版本 v2.0</div>', unsafe_allow_html=True)