"""
智能临床决策助手 - 五合一主应用
企业级界面 · 顶部横幅 + 左侧功能导航
"""
import streamlit as st
from rag import RagService
from knowledge_base import KnowledgeBaseService
import diagnosis_records as dr
import config_data as config
import user_auth as ua
import dashboard_data as dd
from datetime import datetime
import time
import os
from report_generator import generate_diagnosis_report
import operation_log as ol
from database import init_database, run_all_migrations

# ==================== 数据库初始化 ====================
init_database()
# 首次运行时自动迁移旧 JSON 数据（如果存在）
_db_init_flag = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".db_migrated")
if not os.path.exists(_db_init_flag):
    run_all_migrations()
    try:
        with open(_db_init_flag, "w") as _f:
            _f.write("1")
    except Exception:
        pass

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="智能临床决策助手",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 登录/注册状态初始化 ====================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""  # 存储工号
if "login_tab" not in st.session_state:
    st.session_state["login_tab"] = "login"  # "login" 或 "register"

# ==================== 登录/注册界面 ====================
if not st.session_state["logged_in"]:
    # 读取背景图片
    bg_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "homepage.png")
    bg_b64 = ""
    if os.path.exists(bg_img_path):
        import base64
        with open(bg_img_path, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode("utf-8")

    # 获取消息状态
    login_msg = st.session_state.get("login_msg", "")
    login_msg_type = st.session_state.get("login_msg_type", "")
    current_tab = st.session_state.get("login_tab", "login")

    # 隐藏 Streamlit 默认元素
    st.markdown("""
    <style>
        #MainMenu, footer, .stDeployButton, header { display: none !important; }
        .stApp { background: transparent !important; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        .main > div:first-child > div:first-child { padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    # 使用 st.components.v1.html 嵌入完整登录页面（所有内容在白色卡片内部）
    import streamlit.components.v1 as components

    # 构建消息HTML
    msg_html = ""
    if login_msg:
        msg_class = "error" if login_msg_type == "error" else "success"
        msg_html = f'<div class="msg {msg_class}">{login_msg}</div>'

    # 当前tab状态通过隐藏input传递
    login_display = "block" if current_tab == "login" else "none"
    register_display = "block" if current_tab == "register" else "none"

    login_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:100%; height:100%; font-family:"Microsoft YaHei","PingFang SC","Helvetica Neue",Arial,sans-serif; }}
.login-page {{
    width:100vw; height:100vh;
    background:url('data:image/png;base64,{bg_b64}') no-repeat center center fixed;
    background-size:cover;
    display:flex; align-items:center; justify-content:center;
}}
.login-card {{
    background:rgba(255,255,255,0.95);
    backdrop-filter:blur(12px);
    border-radius:12px;
    padding:40px 36px 32px;
    width:420px; max-width:92vw;
    box-shadow:0 12px 48px rgba(0,0,0,0.20);
}}
.login-title {{ text-align:center; font-size:24px; font-weight:700; color:#1a3a6b; margin:0 0 6px; letter-spacing:2px; }}
.login-subtitle {{ text-align:center; font-size:13px; color:#97a8be; margin:0 0 24px; }}
.tab-bar {{ display:flex; gap:12px; margin-bottom:20px; }}
.tab-btn {{
    flex:1; padding:10px 0; text-align:center;
    border:1px solid #dcdfe6; border-radius:6px;
    background:#fff; color:#606266;
    font-size:15px; cursor:pointer; transition:all 0.2s;
    font-family:inherit;
}}
.tab-btn.active {{ border-color:#409EFF; background:#ecf5ff; color:#409EFF; font-weight:600; }}
.form-group {{ margin-bottom:18px; }}
.form-group label {{ display:block; font-size:13px; color:#606266; margin-bottom:6px; font-weight:500; }}
.form-group input {{
    width:100%; padding:10px 14px;
    border:1px solid #dcdfe6; border-radius:6px;
    font-size:14px; color:#303133;
    outline:none; transition:border-color 0.2s;
    font-family:inherit;
}}
.form-group input:focus {{ border-color:#409EFF; }}
.form-group input::placeholder {{ color:#c0c4cc; }}
.submit-btn {{
    width:100%; padding:12px 0;
    background:linear-gradient(135deg,#409EFF,#337ecc);
    color:#fff; border:none; border-radius:6px;
    font-size:16px; font-weight:600; cursor:pointer;
    transition:opacity 0.2s; margin-top:4px;
    font-family:inherit;
}}
.submit-btn:hover {{ opacity:0.9; }}
.msg {{ padding:10px 14px; border-radius:6px; font-size:13px; margin-bottom:14px; }}
.msg.error {{ background:#fef0f0; color:#f56c6c; border:1px solid #fde2e2; }}
.msg.success {{ background:#f0f9eb; color:#67c23a; border:1px solid #e1f3d8; }}
</style>
</head>
<body>
<div class="login-page">
<div class="login-card">
<div class="login-title">临床决策支持系统</div>
<div class="login-subtitle">医生登录 · 智能辅助诊疗平台</div>
{msg_html}
<div class="tab-bar">
<div class="tab-btn{' active' if current_tab=='login' else ''}" onclick="switchTab('login')">登录</div>
<div class="tab-btn{' active' if current_tab=='register' else ''}" onclick="switchTab('register')">注册</div>
</div>

<div id="login-form" style="display:{login_display};">
<form action="?" method="get" onsubmit="return submitLogin()">
<input type="hidden" name="login_action" value="login">
<div class="form-group">
<label>工号</label>
<input type="text" name="wid" id="login-wid" placeholder="请输入工号" autocomplete="off" required>
</div>
<div class="form-group">
<label>密码</label>
<input type="password" name="pwd" id="login-pwd" placeholder="请输入密码" required>
</div>
<button type="submit" class="submit-btn">登 录</button>
</form>
</div>

<div id="register-form" style="display:{register_display};">
<form action="?" method="get" onsubmit="return submitRegister()">
<input type="hidden" name="login_action" value="register">
<div class="form-group">
<label>工号</label>
<input type="text" name="wid" id="reg-wid" placeholder="请输入工号" autocomplete="off" required>
</div>
<div class="form-group">
<label>密码</label>
<input type="password" name="pwd" id="reg-pwd" placeholder="请输入密码（至少4位）" required>
</div>
<div class="form-group">
<label>确认密码</label>
<input type="password" id="reg-pwd2" placeholder="请再次输入密码" required>
</div>
<button type="submit" class="submit-btn">注 册</button>
</form>
</div>

</div>
</div>
<script>
function switchTab(tab){{
    document.querySelectorAll('.tab-btn').forEach(function(b){{b.classList.remove('active');}});
    document.querySelectorAll('.tab-btn')[tab==='login'?0:1].classList.add('active');
    document.getElementById('login-form').style.display=tab==='login'?'block':'none';
    document.getElementById('register-form').style.display=tab==='register'?'block':'none';
}}
function submitLogin(){{
    var w=document.getElementById('login-wid').value.trim();
    var p=document.getElementById('login-pwd').value;
    if(!w||!p){{alert('请填写工号和密码');return false;}}
    return true;
}}
function submitRegister(){{
    var w=document.getElementById('reg-wid').value.trim();
    var p=document.getElementById('reg-pwd').value;
    var p2=document.getElementById('reg-pwd2').value;
    if(!w||!p){{alert('请填写完整信息');return false;}}
    if(p!==p2){{alert('两次密码输入不一致');return false;}}
    return true;
}}
</script>
</body>
</html>"""

    components.html(login_html, height=1000, scrolling=False)

    # 通过 query_params 接收前端提交的数据
    query_params = st.query_params
    if "login_action" in query_params:
        action = query_params["login_action"]
        wid = query_params.get("wid", "")
        pwd = query_params.get("pwd", "")
        if action == "login":
            result = ua.login(wid, pwd)
            if result == "ok":
                st.session_state["logged_in"] = True
                st.session_state["current_user"] = wid
                st.session_state["login_msg"] = ""
                st.session_state["login_msg_type"] = ""
                ol.add_log("login", f"用户登录系统", operator=wid)
            else:
                st.session_state["login_msg"] = result
                st.session_state["login_msg_type"] = "error"
                ol.add_log("login", f"登录失败：{result}", operator=wid, status="error")
        elif action == "register":
            result = ua.register(wid, pwd)
            if result == "ok":
                st.session_state["login_msg"] = "注册成功，请登录"
                st.session_state["login_msg_type"] = "success"
                st.session_state["login_tab"] = "login"
                ol.add_log("register", f"新用户注册成功", operator=wid)
            else:
                st.session_state["login_msg"] = result
                st.session_state["login_msg_type"] = "error"
                ol.add_log("register", f"注册失败：{result}", operator=wid, status="error")
        # 清除参数，防止重复提交
        st.query_params.clear()
        st.rerun()

    st.stop()  # 未登录时停止渲染后续内容

# ==================== 企业级CSS（vue-element-admin 风格） ====================
st.markdown("""
<style>
    /* ===== 字体与全局重置 ===== */
    * { box-sizing: border-box; }
    html, body, .stApp {
        font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    .stApp {
        background-color: #f0f2f5;
    }

    /* ===== 顶部横幅（全宽居中渐变） ===== */
    .top-banner {
        width: 100%;
        background: linear-gradient(135deg, #1a3a6b 0%, #2a5298 50%, #3a6ab8 100%);
        padding: 28px 20px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.12);
        position: relative;
        z-index: 1000;
    }
    .top-banner-title {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 4px;
        letter-spacing: 2px;
    }
    .top-banner-subtitle {
        color: rgba(255,255,255,0.7);
        font-size: 0.85rem;
        margin: 0;
        letter-spacing: 1px;
    }

    /* ===== 侧边栏（Sidebar 风格 — 深色） ===== */
    section[data-testid="stSidebar"] {
        background-color: #304156 !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        background-color: #304156 !important;
    }
    /* 侧边栏按钮 — 默认状态 */
    section[data-testid="stSidebar"] .stButton button {
        background: transparent !important;
        border: none !important;
        color: #bfcbd9 !important;
        text-align: center !important;
        padding: 12px 20px !important;
        font-size: 17px !important;
        font-weight: 400 !important;
        border-radius: 0 !important;
        transition: all 0.2s ease;
        width: 100% !important;
        justify-content: center !important;
        line-height: 1.5 !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: #263445 !important;
        color: #ffffff !important;
    }
    /* 侧边栏按钮 — 激活状态（primary） */
    section[data-testid="stSidebar"] .stButton button[kind="primary"] {
        background-color: #263445 !important;
        color: #409EFF !important;
        font-weight: 600 !important;
        border-right: 3px solid #409EFF !important;
    }
    /* 侧边栏分隔线 */
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1) !important;
        margin: 12px 16px !important;
    }
    /* 侧边栏 caption */
    section[data-testid="stSidebar"] .stCaption {
        color: #ffffff !important;
        font-size: 0.65rem !important;
        padding: 0 16px !important;
    }
    /* 侧边栏导航头部 */
    .nav-header {
        padding: 10px 16px 6px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 4px;
    }
    .nav-header-text {
        color: rgba(255,255,255,0.85);
        font-size: 0.9rem;
        font-weight: 600;
        letter-spacing: 2px;
    }

    /* ===== 内容区域 ===== */
    .content-area {
        padding: 0 24px 16px;
        background: #f0f2f5;
    }
    .page-header {
        margin-bottom: 14px;
    }
    .page-header h2 {
        color: #304156;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0 0 6px;
    }
    .page-header p {
        color: #97a8be;
        font-size: 0.9rem;
        margin: 0;
    }

    /* ===== 卡片容器 ===== */
    .stContainer {
        background: transparent;
    }
    /* 让 st.form 和 st.expander 等有白色卡片背景 */
    div[data-testid="stForm"], div[data-testid="stExpander"] {
        background: #ffffff !important;
        border: 1px solid #ebeef5 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04) !important;
    }
    div[data-testid="stExpander"] div[data-testid="stExpander"] {
        box-shadow: none !important;
        border: 1px solid #f0f2f5 !important;
        padding: 12px !important;
    }

    /* ===== 聊天消息样式 ===== */
    div[data-testid="stChatMessage"][data-kind="user"] {
        background-color: #409EFF !important;
        color: white !important;
        border-radius: 18px 18px 4px 18px;
        padding: 8px 16px;
        margin-bottom: 12px;
    }
    div[data-testid="stChatMessage"][data-kind="assistant"] {
        background-color: #ffffff !important;
        color: #304156 !important;
        border-radius: 18px 18px 18px 4px;
        padding: 8px 16px;
        margin-bottom: 12px;
        border-left: 4px solid #409EFF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    div[data-testid="stChatMessage"][data-kind="assistant"] * {
        color: #304156 !important;
    }
    div[data-testid="stChatMessage"][data-kind="user"] * {
        color: white !important;
    }
    .message-timestamp {
        font-size: 0.65rem;
        color: #c0c4cc !important;
        margin-top: 6px;
        text-align: right;
    }
    .input-hint {
        font-size: 0.75rem;
        color: #97a8be;
        margin-top: 8px;
        text-align: center;
    }

    /* ===== 隐藏Streamlit原生元素 ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {visibility: hidden; height: 0;}

    /* ===== 诊断记录卡片 ===== */
    .record-card {
        background: #ffffff;
        border: 1px solid #ebeef5;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        transition: all 0.15s ease;
    }
    .record-card:hover {
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border-color: #c0c4cc;
    }

    /* ===== 通用按钮样式 ===== */
    .stButton button[kind="primary"] {
        background: #409EFF !important;
        border-color: #409EFF !important;
    }
    .stButton button[kind="primary"]:hover {
        background: #66b1ff !important;
        border-color: #66b1ff !important;
    }
    .stButton button[kind="secondary"] {
        color: #606266 !important;
        border-color: #dcdfe6 !important;
    }
    .stButton button[kind="secondary"]:hover {
        color: #409EFF !important;
        border-color: #c6e2ff !important;
        background: #ecf5ff !important;
    }

    /* ===== 输入框样式 ===== */
    input, textarea, div[data-baseweb="select"] {
        border-color: #dcdfe6 !important;
        border-radius: 4px !important;
    }
    input:focus, textarea:focus {
        border-color: #409EFF !important;
        box-shadow: 0 0 0 2px rgba(64,158,255,0.2) !important;
    }

    /* ===== 指标卡片 ===== */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #ebeef5;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetric"] label {
        color: #97a8be !important;
        font-size: 0.75rem !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #304156 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }

    /* ===== 状态消息 ===== */
    .stAlert {
        border-radius: 6px !important;
        border: none !important;
    }
    div[data-testid="stStatusWidget"] {
        border-radius: 6px !important;
    }
    /* ===== 内容区顶部深蓝横幅 ===== */
    .top-bar {
        width: calc(100% + 48px);
        background: linear-gradient(135deg, #1a3a6b 0%, #2a5298 50%, #3a6ab8 100%);
        padding: 18px 20px;
        text-align: center;
        margin: 0 0 0 -24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.10);
        box-sizing: border-box;
    }
    .top-bar-title {
        color: #ffffff;
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 3px;
        margin: 0;
    }

    /* ===== 页面动态横幅 ===== */
    .page-banner {
        width: calc(100% + 48px);
        background: linear-gradient(135deg, #e8f4fd 0%, #d1ecfa 100%);
        padding: 14px 20px;
        text-align: center;
        margin: 0 0 12px -24px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        box-sizing: border-box;
    }
    .page-banner-title {
        font-size: 18px;
        font-weight: 700;
        color: #1a3a6b;
        letter-spacing: 1px;
        margin: 0 0 4px;
    }
    .page-banner-desc {
        font-size: 13px;
        font-weight: 400;
        color: #5a6a7e;
        margin: 0;
        letter-spacing: 0.5px;
    }

    /* ===== 登录/注册界面（vue-element-admin 风格） ===== */
    .login-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .login-card {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 40px 36px;
        width: 420px;
        max-width: 92vw;
        box-shadow: 0 12px 48px rgba(0,0,0,0.20);
        position: relative;
    }
    .login-card .login-title {
        text-align: center;
        font-size: 24px;
        font-weight: 700;
        color: #1a3a6b;
        margin: 0 0 6px;
        letter-spacing: 2px;
    }
    .login-card .login-subtitle {
        text-align: center;
        font-size: 13px;
        color: #97a8be;
        margin: 0 0 28px;
    }
    .login-card .login-tabs {
        display: flex;
        gap: 0;
        margin-bottom: 24px;
        border-bottom: 2px solid #ebeef5;
    }
    .login-card .login-tab {
        flex: 1;
        text-align: center;
        padding: 10px 0;
        font-size: 15px;
        font-weight: 500;
        color: #97a8be;
        cursor: pointer;
        border-bottom: 2px solid transparent;
        margin-bottom: -2px;
        transition: all 0.2s;
    }
    .login-card .login-tab.active {
        color: #409EFF;
        border-bottom-color: #409EFF;
    }
    .login-card .login-field {
        margin-bottom: 18px;
    }
    .login-card .login-field label {
        display: block;
        font-size: 13px;
        font-weight: 500;
        color: #5a6a7e;
        margin-bottom: 6px;
    }
    .login-card .login-field input {
        width: 100%;
        padding: 10px 14px;
        border: 1px solid #dcdfe6;
        border-radius: 6px;
        font-size: 14px;
        color: #304156;
        outline: none;
        transition: border-color 0.2s;
        box-sizing: border-box;
    }
    .login-card .login-field input:focus {
        border-color: #409EFF;
        box-shadow: 0 0 0 2px rgba(64,158,255,0.15);
    }
    .login-card .login-btn {
        width: 100%;
        padding: 11px 0;
        background: linear-gradient(135deg, #409EFF, #337ecc);
        color: #fff;
        border: none;
        border-radius: 6px;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        transition: opacity 0.2s;
        margin-top: 6px;
    }
    .login-card .login-btn:hover {
        opacity: 0.9;
    }
    .login-card .login-error {
        color: #f56c6c;
        font-size: 13px;
        text-align: center;
        margin: 10px 0 0;
        padding: 8px 12px;
        background: #fef0f0;
        border-radius: 4px;
    }
    .login-card .login-success {
        color: #67c23a;
        font-size: 13px;
        text-align: center;
        margin: 10px 0 0;
        padding: 8px 12px;
        background: #f0f9eb;
        border-radius: 4px;
    }
    .login-card .login-divider {
        text-align: center;
        font-size: 12px;
        color: #c0c4cc;
        margin: 16px 0 0;
    }
    .login-card .login-divider span {
        cursor: pointer;
        color: #409EFF;
    }
    .login-card .login-divider span:hover {
        text-decoration: underline;
    }

</style>
""", unsafe_allow_html=True)

# ==================== 辅助函数 ====================
def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def get_doc_count():
    try:
        if "rag" in st.session_state:
            vs = st.session_state["rag"].vector_service
            count = vs.vector_store._collection.count()
            return count
    except Exception:
        pass
    return "未知"

# ==================== 页面配置字典 ====================
PAGE_CONFIG = {
    "首页": {
        "title": "首页",
        "desc": "智能临床决策支持系统 · 欢迎使用",
    },
    "知识库管理": {
        "title": "知识库管理",
        "desc": "智能临床知识管理 · 支持文本向量化与去重上传",
    },
    "鉴别诊断辅助": {
        "title": "鉴别诊断辅助",
        "desc": "基于知识库的症状分析与鉴别诊断建议",
    },
    "智能临床问答": {
        "title": "智能临床问答",
        "desc": "基于RAG的病症分析与药物推荐系统",
    },
    "用药安全核查": {
        "title": "用药安全核查",
        "desc": "基于知识库的药物安全信息检索与核查",
    },
    "患者诊断记录": {
        "title": "患者诊断记录",
        "desc": "诊断信息管理 · 支持增删改查与知识库同步",
    },
    "操作日志": {
        "title": "操作日志",
        "desc": "系统操作审计 · 记录登录、上传、诊断等所有关键操作",
    },
}

PAGE_NAMES = list(PAGE_CONFIG.keys())

# ==================== 初始化 ====================
if "message" not in st.session_state:
    st.session_state["message"] = [
        {"role": "assistant", "content": "请医生输入病症？", "timestamp": get_current_time()}
    ]

if "rag" not in st.session_state:
    st.session_state["rag"] = RagService()

if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()

if "upload_history" not in st.session_state:
    st.session_state["upload_history"] = []

if "diagnosis_page" not in st.session_state:
    st.session_state["diagnosis_page"] = "list"

if "editing_record_id" not in st.session_state:
    st.session_state["editing_record_id"] = None

if "viewing_record_id" not in st.session_state:
    st.session_state["viewing_record_id"] = None

# ==================== 侧边栏导航 ====================
if "current_page" not in st.session_state:
    st.session_state["current_page"] = PAGE_NAMES[0]

with st.sidebar:
    # 当前登录用户信息
    current_user = st.session_state.get("current_user", "")
    if current_user:
        st.markdown(f"""
        <div style="padding:8px 12px;margin-bottom:8px;background:rgba(64,158,255,0.10);border-radius:6px;border-left:3px solid #409EFF;">
            <div style="font-size:12px;color:#97a8be;">当前用户</div>
            <div style="font-size:15px;font-weight:600;color:#ffffff;">{current_user}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="nav-header"><span class="nav-header-text">功能选择</span></div>', unsafe_allow_html=True)

    for i, pname in enumerate(PAGE_NAMES):
        is_active = (st.session_state["current_page"] == pname)
        clicked = st.button(
            pname,
            key=f"nav_{pname}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
            help=f"切换到「{pname}」"
        )
        if clicked:
            st.session_state["current_page"] = pname
            st.rerun()

    st.markdown("---")
    if st.button("退出登录", use_container_width=True, type="secondary"):
        ol.add_log("logout", f"用户退出登录", operator=st.session_state.get("current_user", ""))
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = ""
        st.session_state["login_msg"] = ""
        st.session_state["login_msg_type"] = ""
        st.rerun()
    st.caption("© 2026 智能临床决策支持系统")

# ==================== 主内容区 ====================
page = st.session_state["current_page"]
cfg = PAGE_CONFIG[page]

st.markdown(f'<div class="content-area">', unsafe_allow_html=True)

st.markdown(f'<div class="top-bar"><div class="top-bar-title">临床决策支持对话机器人</div></div>', unsafe_allow_html=True)

# ==================== 各页面内容分支 ====================
if page == "首页":
    doc_count = get_doc_count()

    # ===== 读取图片并转为base64，作为CSS固定背景 =====
    bg_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "homepage.png")
    bg_b64 = ""
    if os.path.exists(bg_img_path):
        import base64
        with open(bg_img_path, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode("utf-8")
    else:
        st.warning("请将首页图片放到 RagProject/assets/homepage.png")

    # ===== 采集仪表盘数据 =====
    vector_store = None
    if "rag" in st.session_state:
        try:
            vector_store = st.session_state["rag"].vector_service.vector_store
        except Exception:
            pass

    kb_stats = dd.get_kb_stats(vector_store)
    diag_stats = dd.get_diagnosis_stats()
    chat_stats = dd.get_chat_stats()
    user_stats = dd.get_user_stats()

    # ===== 首页样式 =====
    st.markdown(f"""
    <style>
        .home-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-image: url('data:image/png;base64,{bg_b64}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            z-index: 0;
            pointer-events: none;
        }}
        .home-content {{
            position: relative;
            z-index: 1;
            min-height: 70vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
        }}
        .home-welcome {{
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(235,238,245,0.6);
            border-radius: 16px;
            padding: 32px 40px;
            text-align: center;
            max-width: 800px;
            width: 100%;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
            margin-bottom: 24px;
        }}
        .home-welcome h1 {{
            color: #1a3a6b;
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0 0 8px;
            letter-spacing: 2px;
        }}
        .home-welcome p {{
            color: #5a6a7e;
            font-size: 0.95rem;
            margin: 0;
            line-height: 1.6;
        }}
        /* 仪表盘容器 */
        .dashboard-section {{
            width: 100%;
            max-width: 1000px;
        }}
        .dashboard-metrics {{
            display: flex;
            gap: 14px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(235,238,245,0.6);
            border-radius: 12px;
            padding: 18px 24px;
            min-width: 150px;
            flex: 1;
            text-align: center;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        }}
        .metric-card .metric-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #409EFF;
            margin-bottom: 4px;
        }}
        .metric-card .metric-label {{
            font-size: 0.8rem;
            color: #5a6a7e;
            font-weight: 500;
        }}
        .chart-container {{
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(235,238,245,0.6);
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        }}
        .chart-container .chart-title {{
            font-size: 0.95rem;
            font-weight: 600;
            color: #304156;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #ebeef5;
        }}
    </style>
    <div class="home-bg"></div>
    <div class="home-content">
        <div class="home-welcome">
            <h1>智能临床决策支持系统</h1>
            <p>基于检索增强生成（RAG）技术的临床辅助决策平台 · 助力精准医疗</p>
        </div>
        <div class="dashboard-section">
            <!-- 4个关键指标 -->
            <div class="dashboard-metrics">
                <div class="metric-card">
                    <div class="metric-value">{kb_stats["total_chunks"]}</div>
                    <div class="metric-label">知识库片段数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{diag_stats["total_records"]}</div>
                    <div class="metric-label">诊断记录数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{user_stats["total_users"]}</div>
                    <div class="metric-label">注册用户数</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{chat_stats["total_sessions"]}</div>
                    <div class="metric-label">对话会话数</div>
                </div>
            </div>
    """, unsafe_allow_html=True)

    # ===== 诊断趋势折线图 =====
    if diag_stats["daily_trend"]:
        trend_data = {item["date"]: item["count"] for item in diag_stats["daily_trend"]}
        st.markdown('<div class="chart-container"><div class="chart-title">诊断记录趋势</div>', unsafe_allow_html=True)
        st.line_chart(trend_data, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ===== 疾病分布 + 知识库文件分布（并排） =====
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        if diag_stats["disease_distribution"]:
            disease_data = {
                item["name"]: item["count"]
                for item in diag_stats["disease_distribution"]
            }
            st.markdown('<div class="chart-container"><div class="chart-title">诊断结果分布（Top 8）</div>', unsafe_allow_html=True)
            st.bar_chart(disease_data, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="chart-container"><div class="chart-title">诊断结果分布</div><p style="color:#97a8be;font-size:0.85rem;text-align:center;">暂无诊断记录</p></div>', unsafe_allow_html=True)

    with col_chart2:
        if kb_stats["source_distribution"]:
            source_data = {
                item["name"]: item["count"]
                for item in kb_stats["source_distribution"]
            }
            st.markdown('<div class="chart-container"><div class="chart-title">知识库文件分布</div>', unsafe_allow_html=True)
            st.bar_chart(source_data, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="chart-container"><div class="chart-title">知识库文件分布</div><p style="color:#97a8be;font-size:0.85rem;text-align:center;">暂无知识库数据</p></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif page == "知识库管理":
    st.markdown(f'<div class="page-banner"><div class="page-banner-title">{cfg["title"]}</div><div class="page-banner-desc">{cfg["desc"]}</div></div>', unsafe_allow_html=True)
    # 上传区域
    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            uploader_file = st.file_uploader(
                label="**请选择要上传的文件**",
                type=['txt', 'pdf', 'docx', 'md'],
                accept_multiple_files=False,
                help="支持 TXT / PDF / DOCX / MD 格式，文件内容将作为知识库检索来源"
            )
        with col2:
            st.markdown("#### 提示")
            st.caption("支持 TXT / PDF / DOCX / MD 格式。上传后系统将自动提取文本、分块并生成向量索引。重复文件会被自动跳过。")

    # 处理上传文件
    if uploader_file is not None:
        file_name = uploader_file.name
        file_ext = file_name.split(".")[-1].lower() if "." in file_name else "unknown"
        file_size = uploader_file.size / 1024

        with st.expander("文件详情", expanded=True):
            col_info1, col_info2, col_info3 = st.columns(3)
            col_info1.metric("文件名", file_name)
            col_info2.metric("文件格式", f".{file_ext}")
            col_info3.metric("文件大小", f"{file_size:.2f} KB")

            # 使用多格式文本提取
            from knowledge_base import extract_text_from_uploaded_file
            content, detected_type = extract_text_from_uploaded_file(uploader_file)
            with st.expander("内容预览（前500字符）"):
                st.text(content[:500] + ("..." if len(content) > 500 else ""))

        with st.status("⏳ 处理中...", expanded=True) as status:
            st.write(f"正在检查文件 `{file_name}` 的MD5...")
            time.sleep(0.5)

            result = st.session_state["service"].upload_by_str(content, file_name)

            if "成功" in result:
                status.update(label="✅ 上传成功", state="complete", expanded=False)
                st.toast(f"🎉 {result}", icon="✅")
                st.success(result)
                ol.add_log("upload", f"上传文件「{file_name}」成功", operator=st.session_state.get("current_user", ""))
                del st.session_state["rag"]
                del st.session_state["service"]
                st.rerun()
            elif "跳过" in result:
                status.update(label="⚠️ 文件已存在", state="complete", expanded=False)
                st.toast(f"ℹ️ {result}", icon="⚠️")
                st.info(result)
                ol.add_log("upload", f"文件「{file_name}」已存在，自动跳过", operator=st.session_state.get("current_user", ""), status="warning")
                del st.session_state["rag"]
                del st.session_state["service"]
                st.rerun()
            else:
                status.update(label="❌ 上传失败", state="error", expanded=False)
                st.toast(f"❌ {result}", icon="❌")
                st.error(result)

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.upload_history.append((file_name, result, now))

        try:
            new_count = st.session_state["service"].chroma._collection.count()
            st.caption(f"📊 当前向量库总片段数：{new_count}")
        except Exception:
            pass

    # 最近上传记录
    st.markdown("---")
    st.markdown("### 🕒 最近上传记录")
    if st.session_state.upload_history:
        history_display = st.session_state.upload_history[::-1][:5]
        for file, status_text, timestamp in history_display:
            if "成功" in status_text:
                icon = "✅"
            elif "跳过" in status_text:
                icon = "⚠️"
            else:
                icon = "❌"
            st.markdown(f"{icon} **{file}** – {status_text} – `{timestamp}`")
    else:
        st.info("暂无上传记录，请上传TXT文件。")

    # ===== 知识库文档管理 =====
    st.markdown("---")
    st.markdown("### 📂 知识库文档管理")
    st.caption("查看和管理已上传到知识库的所有文档。删除文档后需重新上传才能恢复。")

    # 初始化删除确认状态
    if "kb_delete_confirm" not in st.session_state:
        st.session_state["kb_delete_confirm"] = None

    try:
        kb_service = st.session_state.get("service")
        if kb_service is None:
            st.info("知识库服务尚未初始化，请先上传文件。")
        else:
            doc_list = kb_service.get_all_documents()
            if not doc_list:
                st.info("知识库中暂无文档。")
            else:
                total_chunks = sum(d["chunk_count"] for d in doc_list)
                st.markdown(f"**共 {len(doc_list)} 个文档，{total_chunks} 个文本片段**")

                for doc in doc_list:
                    source = doc["source"]
                    chunk_count = doc["chunk_count"]
                    create_time = doc.get("create_time", "未知")
                    operator = doc.get("operator", "未知")
                    sample = doc.get("sample_content", "")

                    with st.container():
                        cols = st.columns([3, 1, 1, 1])
                        with cols[0]:
                            st.markdown(f"**{source}**")
                            st.caption(f"上传时间：{create_time} ｜ 操作人：{operator}")
                            if sample:
                                st.caption(f"片段预览：{sample}...")
                        with cols[1]:
                            st.markdown(f"**{chunk_count}** 片段")
                        with cols[2]:
                            if st.session_state["kb_delete_confirm"] == source:
                                st.warning(f"确认删除「{source}」？")
                            else:
                                if st.button("🗑️ 删除", key=f"kb_del_{source}"):
                                    st.session_state["kb_delete_confirm"] = source
                                    st.rerun()
                        with cols[3]:
                            if st.session_state["kb_delete_confirm"] == source:
                                col_c1, col_c2 = st.columns(2)
                                with col_c1:
                                    if st.button("✅ 确认", key=f"kb_confirm_{source}"):
                                        result = kb_service.delete_document(source)
                                        if "成功" in result:
                                            st.toast(f"✅ {result}", icon="✅")
                                            st.success(result)
                                            ol.add_log("kb_delete", f"删除知识库文档「{source}」", operator=st.session_state.get("current_user", ""))
                                            # 清除 rag 缓存，下次访问时重新加载
                                            if "rag" in st.session_state:
                                                del st.session_state["rag"]
                                            if "service" in st.session_state:
                                                del st.session_state["service"]
                                        else:
                                            st.toast(f"❌ {result}", icon="❌")
                                            st.error(result)
                                            ol.add_log("kb_delete", f"删除文档「{source}」失败：{result}", operator=st.session_state.get("current_user", ""), status="error")
                                        st.session_state["kb_delete_confirm"] = None
                                        st.rerun()
                                with col_c2:
                                    if st.button("❌ 取消", key=f"kb_cancel_{source}"):
                                        st.session_state["kb_delete_confirm"] = None
                                        st.rerun()
                        st.markdown("---")
    except Exception as e:
        st.error(f"加载文档列表失败：{str(e)}")

elif page == "鉴别诊断辅助":
    st.markdown(f'<div class="page-banner"><div class="page-banner-title">{cfg["title"]}</div><div class="page-banner-desc">{cfg["desc"]}</div></div>', unsafe_allow_html=True)
    symptoms = st.text_area(
        "🩺 主要症状或体征",
        placeholder="例如：咳嗽、发热、胸痛、呼吸困难...",
        height=120,
        help="请详细描述患者的症状和体征，多个症状用逗号或换行分隔"
    )

    col1, col2 = st.columns(2)
    with col1:
        patient_age = st.number_input("👤 年龄（岁）", min_value=0, max_value=150, value=0, step=1, help="可选")
    with col2:
        patient_gender = st.selectbox("👤 性别", ["未指定", "男", "女"], index=0, help="可选")

    generate_clicked = st.button("🔍 生成鉴别诊断", type="primary", use_container_width=True)

    if generate_clicked:
        if not symptoms.strip():
            st.error("❌ 请至少输入一个症状或体征！")
        else:
            query_parts = [f"患者症状：{symptoms.strip()}"]
            if patient_age > 0:
                query_parts.append(f"年龄：{patient_age}岁")
            if patient_gender != "未指定":
                query_parts.append(f"性别：{patient_gender}")

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

            with st.spinner("正在检索知识库并生成鉴别诊断建议..."):
                diag_config = {"configurable": {"session_id": "differential_diag_001"}}
                try:
                    res = st.session_state["rag"].chain.invoke(
                        {"input": query},
                        diag_config
                    )
                except Exception as e:
                    res = f"生成鉴别诊断时出现错误：{str(e)}"

            st.markdown("---")
            st.markdown("### 📊 鉴别诊断结果")
            st.markdown("> *基于知识库检索结果*")
            st.markdown(res)

            # 记录鉴别诊断日志
            if "错误" not in res:
                ol.add_log("diagnosis", f"生成鉴别诊断：症状「{symptoms.strip()[:50]}」", operator=st.session_state.get("current_user", ""))
            else:
                ol.add_log("diagnosis", f"鉴别诊断生成失败", operator=st.session_state.get("current_user", ""), status="error")

            # PDF 导出按钮
            pdf_bytes = generate_diagnosis_report(
                symptoms=symptoms.strip(),
                diagnosis_result=res,
                patient_info={
                    "name": "",
                    "age": str(patient_age) if patient_age > 0 else "",
                    "gender": patient_gender if patient_gender != "未指定" else "",
                    "doctor": st.session_state.get("current_user", ""),
                }
            )
            st.download_button(
                "📄 导出诊断报告 (PDF)",
                data=pdf_bytes,
                file_name=f"诊断报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            # 记录 PDF 导出日志（点击下载时触发）
            if st.session_state.get("_pdf_exported", False) is False:
                st.session_state["_pdf_exported"] = True
                ol.add_log("pdf_export", f"导出诊断报告PDF：症状「{symptoms.strip()[:50]}」", operator=st.session_state.get("current_user", ""))

            with st.expander("📝 查看输入信息"):
                st.markdown(f"- **症状描述**：{symptoms.strip()}")
                st.markdown(f"- **年龄**：{f'{patient_age}岁' if patient_age > 0 else '未提供'}")
                st.markdown(f"- **性别**：{patient_gender if patient_gender != '未指定' else '未提供'}")

elif page == "智能临床问答":
    st.markdown(f'<div class="page-banner"><div class="page-banner-title">{cfg["title"]}</div><div class="page-banner-desc">{cfg["desc"]}</div></div>', unsafe_allow_html=True)
    # 清空对话按钮
    col_clear, _ = st.columns([1, 5])
    with col_clear:
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state["message"] = [
                {"role": "assistant", "content": "对话已清空，请重新输入症状。", "timestamp": get_current_time()}
            ]
            st.rerun()

    # 显示历史消息
    for msg in st.session_state["message"]:
        avatar = "🩺" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            timestamp = msg.get("timestamp", "")
            if timestamp:
                st.markdown(f'<div class="message-timestamp">{timestamp}</div>', unsafe_allow_html=True)

    # 用户输入
    prompt = st.chat_input(placeholder="例如：我咳嗽（干咳无痰），推荐什么药？")
    st.markdown('<div class="input-hint">💡 提示：您可以直接描述症状，机器人将基于知识库给出建议。</div>', unsafe_allow_html=True)

    if prompt:
        user_msg = {"role": "user", "content": prompt, "timestamp": get_current_time()}
        st.session_state["message"].append(user_msg)
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            st.markdown(f'<div class="message-timestamp">{user_msg["timestamp"]}</div>', unsafe_allow_html=True)

        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                yield chunk

        with st.spinner("正在检索知识库并思考..."):
            res_stream = st.session_state["rag"].chain.stream(
                {"input": prompt},
                config.session_config
            )
            ai_res_list = []
            with st.chat_message("assistant", avatar="🩺"):
                full_response = st.write_stream(capture(res_stream, ai_res_list))
                st.markdown(f'<div class="message-timestamp">{get_current_time()}</div>', unsafe_allow_html=True)
                if not full_response and ai_res_list:
                    full_response = "".join(ai_res_list)

        if not full_response:
            full_response = "抱歉，没有检索到相关信息。"
            with st.chat_message("assistant", avatar="🩺"):
                st.markdown(full_response)
                st.markdown(f'<div class="message-timestamp">{get_current_time()}</div>', unsafe_allow_html=True)

        assistant_msg = {"role": "assistant", "content": full_response, "timestamp": get_current_time()}
        st.session_state["message"].append(assistant_msg)

elif page == "用药安全核查":
    st.markdown(f'<div class="page-banner"><div class="page-banner-title">{cfg["title"]}</div><div class="page-banner-desc">{cfg["desc"]}</div></div>', unsafe_allow_html=True)
    with st.form(key="drug_safety_form"):
        col1, col2 = st.columns(2)
        with col1:
            drug_name = st.text_input("💊 药物名称 *", placeholder="例如：阿司匹林、布洛芬", help="请输入需要核查的药物名称（必填）")
            age = st.number_input("👤 患者年龄（岁）", min_value=0, max_value=150, value=0, step=1, help="可选，输入患者年龄有助于个性化评估")
        with col2:
            allergy = st.text_input("⚠️ 过敏史", placeholder="例如：青霉素过敏", help="可选，输入已知过敏药物或成分")
            notes = st.text_input("📋 备注", placeholder="例如：肾功能不全、妊娠状态", help="可选，如肝肾功能、妊娠状态等特殊信息")

        submitted = st.form_submit_button("🔍 核查", use_container_width=True, type="primary")

    if submitted:
        if not drug_name.strip():
            st.error("❌ 请填写药物名称！")
        else:
            with st.spinner("正在评估药物安全性..."):
                vector_store = st.session_state["rag"].vector_service.vector_store
                llm = st.session_state["rag"].chat_model

                search_query = f"{drug_name.strip()} 可用性 不良反应 禁忌"
                try:
                    all_docs = vector_store.similarity_search(search_query, k=5)
                    filtered_docs = [doc for doc in all_docs if "drug_safety_structured" in doc.metadata.get("source", "").lower()]
                except Exception as e:
                    filtered_docs = []
                    st.error(f"检索失败：{e}")

                if not filtered_docs:
                    context = "未找到该药物的安全信息文档。"
                else:
                    context = "\n\n".join([doc.page_content for doc in filtered_docs])

                prompt = f"""你是一个药物安全评估专家。严格基于以下药物安全知识库内容，根据患者信息判断该药物是否可以使用，并按指定格式输出。

患者信息：
- 药物名称：{drug_name.strip()}
- 年龄：{age if age > 0 else '未提供'} 岁
- 过敏史：{allergy.strip() if allergy.strip() else '无'}
- 备注（如怀孕、疾病等）：{notes.strip() if notes.strip() else '无'}

知识库内容：
{context}

请输出以下内容（严格遵守格式，不要添加额外解释）：

决策：[✅ 可以使用该药物] 或 [❌ 不可使用该药物]（二选一，并根据患者信息和知识库规则给出理由）

1. 主要不良反应：（列出知识库中提到的主要不良反应）

2. 用药禁忌：（列出知识库中提到的禁忌症，并结合患者信息说明是否存在）

3. 针对该患者的特别提醒：（结合年龄、过敏史、备注，给出个性化提醒）

如果知识库中没有相关信息，请明确说明"知识库中无此药物信息"。
"""
                try:
                    response = llm.invoke(prompt)
                    res = response.content
                except Exception as e:
                    res = f"生成评估时出错：{str(e)}"

        st.markdown("---")
        st.markdown("### 📋 核查结果")
        st.markdown(res)

        # 记录用药安全核查日志
        if submitted and drug_name.strip():
            ol.add_log("drug_safety", f"用药安全核查：药物「{drug_name.strip()}」", operator=st.session_state.get("current_user", ""))

elif page == "患者诊断记录":
    st.markdown(f'<div class="page-banner"><div class="page-banner-title">{cfg["title"]}</div><div class="page-banner-desc">{cfg["desc"]}</div></div>', unsafe_allow_html=True)
    current_page = st.session_state["diagnosis_page"]

    # ========== 列表视图 ==========
    if current_page == "list":
        col_add, col_search = st.columns([1, 3])
        with col_add:
            if st.button("➕ 新增诊断记录", type="primary", use_container_width=True):
                st.session_state["diagnosis_page"] = "add"
                st.rerun()

        with col_search:
            search_keyword = st.text_input("🔍 搜索", placeholder="按患者姓名、身份证号、症状或诊断结果搜索...", label_visibility="collapsed")

        if search_keyword:
            records = dr.search_records(search_keyword)
        else:
            records = dr.get_all_records()

        st.markdown("---")

        if not records:
            st.info("📭 暂无诊断记录，请点击「新增诊断记录」添加。")
        else:
            st.markdown(f"**共 {len(records)} 条记录**")
            for rec in records:
                with st.container():
                    st.markdown(f'<div class="record-card">', unsafe_allow_html=True)
                    cols = st.columns([3, 1, 1, 1])
                    patient_name = rec.get("patient_name", "未知")
                    diagnosis_result = rec.get("diagnosis_result", "未填写")
                    diagnosis_time = rec.get("diagnosis_time", "未填写")
                    record_id = rec.get("id", "")

                    with cols[0]:
                        st.markdown(f"**👤 {patient_name}** — `{diagnosis_result}`")
                        st.caption(f"🕒 {diagnosis_time} | ID: {record_id}")
                    with cols[1]:
                        if st.button("👁️ 查看", key=f"view_{record_id}", use_container_width=True):
                            st.session_state["viewing_record_id"] = record_id
                            st.session_state["diagnosis_page"] = "detail"
                            st.rerun()
                    with cols[2]:
                        if st.button("✏️ 编辑", key=f"edit_{record_id}", use_container_width=True):
                            st.session_state["editing_record_id"] = record_id
                            st.session_state["diagnosis_page"] = "edit"
                            st.rerun()
                    with cols[3]:
                        if st.button("🗑️ 删除", key=f"del_{record_id}", use_container_width=True):
                            if dr.delete_record(record_id):
                                st.toast(f"✅ 已删除记录 {record_id}", icon="🗑️")
                                ol.add_log("record_crud", f"删除诊断记录 ID: {record_id}", operator=st.session_state.get("current_user", ""))
                                st.rerun()
                            else:
                                st.error("删除失败")
                    st.markdown('</div>', unsafe_allow_html=True)

    # ========== 新增视图 ==========
    elif current_page == "add":
        st.markdown("### ➕ 新增诊断记录")
        with st.form(key="diagnosis_add_form"):
            col1, col2 = st.columns(2)
            with col1:
                patient_name = st.text_input("👤 患者姓名 *", placeholder="请输入患者姓名")
                id_number = st.text_input("🆔 身份证号", placeholder="18位身份证号（可选）")
                age = st.number_input("📅 年龄（岁）", min_value=0, max_value=150, value=0, step=1)
                gender = st.selectbox("⚤ 性别", ["男", "女", "其他"], index=0)
            with col2:
                symptoms = st.text_area("🩺 主要症状或体征 *", placeholder="例如：咳嗽、发热、胸痛...", height=100)
                notes = st.text_area("📋 备注（过敏史或特殊状态）", placeholder="例如：青霉素过敏、肾功能不全、妊娠状态...", height=100)

            examinations = st.text_area("🔬 进行的检查", placeholder="若无则留空。例如：血常规、CT、心电图...", height=80)
            diagnosis_result = st.text_area("📝 最终诊断结果 *", placeholder="例如：上呼吸道感染、高血压2级...", height=80)
            treatment_decision = st.text_area("💊 诊断决策（用药等）", placeholder="例如：阿莫西林 500mg tid × 7天...", height=80)

            col_t1, col_t2 = st.columns(2)
            with col_t1:
                diagnosis_time = st.text_input("🕒 诊断时间", value=datetime.now().strftime("%Y-%m-%d %H:%M"), help="可手动修改")
            with col_t2:
                current_doctor = st.session_state.get("current_user", "")
                doctor = st.text_input("诊断人", value=current_doctor, disabled=True)

            submitted = st.form_submit_button("💾 保存记录", type="primary", use_container_width=True)

        if submitted:
            if not patient_name.strip():
                st.error("❌ 患者姓名为必填项！")
            elif not symptoms.strip():
                st.error("❌ 主要症状或体征为必填项！")
            elif not diagnosis_result.strip():
                st.error("❌ 最终诊断结果为必填项！")
            else:
                record = {
                    "patient_name": patient_name.strip(),
                    "id_number": id_number.strip(),
                    "age": age,
                    "gender": gender,
                    "symptoms": symptoms.strip(),
                    "notes": notes.strip(),
                    "examinations": examinations.strip(),
                    "diagnosis_result": diagnosis_result.strip(),
                    "treatment_decision": treatment_decision.strip(),
                    "diagnosis_time": diagnosis_time.strip(),
                    "doctor": doctor.strip(),
                }
                record_id = dr.add_record(record)
                st.toast(f"✅ 诊断记录已保存（ID: {record_id}）", icon="✅")
                ol.add_log("record_crud", f"新增诊断记录：患者「{patient_name.strip()}」，ID: {record_id}", operator=st.session_state.get("current_user", ""))
                st.session_state["diagnosis_page"] = "list"
                st.rerun()

        if st.button("🔙 返回列表", use_container_width=True):
            st.session_state["diagnosis_page"] = "list"
            st.rerun()

    # ========== 编辑视图 ==========
    elif current_page == "edit":
        record_id = st.session_state.get("editing_record_id")
        rec = dr.get_record(record_id) if record_id else None

        if not rec:
            st.error("❌ 未找到该记录")
            st.session_state["diagnosis_page"] = "list"
            st.rerun()
        else:
            st.markdown(f"### ✏️ 编辑诊断记录 — {rec.get('patient_name', '')}")
            with st.form(key="diagnosis_edit_form"):
                col1, col2 = st.columns(2)
                with col1:
                    patient_name = st.text_input("👤 患者姓名 *", value=rec.get("patient_name", ""))
                    id_number = st.text_input("🆔 身份证号", value=rec.get("id_number", ""))
                    age = st.number_input("📅 年龄（岁）", min_value=0, max_value=150, value=int(rec.get("age", 0)), step=1)
                    gender = st.selectbox("⚤ 性别", ["男", "女", "其他"], index=["男", "女", "其他"].index(rec.get("gender", "男")))
                with col2:
                    symptoms = st.text_area("🩺 主要症状或体征 *", value=rec.get("symptoms", ""), height=100)
                    notes = st.text_area("📋 备注（过敏史或特殊状态）", value=rec.get("notes", ""), height=100)

                examinations = st.text_area("🔬 进行的检查", value=rec.get("examinations", ""), height=80)
                diagnosis_result = st.text_area("📝 最终诊断结果 *", value=rec.get("diagnosis_result", ""), height=80)
                treatment_decision = st.text_area("💊 诊断决策（用药等）", value=rec.get("treatment_decision", ""), height=80)

                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    diagnosis_time = st.text_input("🕒 诊断时间", value=rec.get("diagnosis_time", ""))
                with col_t2:
                    current_doctor = st.session_state.get("current_user", "")
                    doctor = st.text_input("诊断人", value=current_doctor, disabled=True)

                submitted = st.form_submit_button("💾 更新记录", type="primary", use_container_width=True)

            if submitted:
                if not patient_name.strip():
                    st.error("❌ 患者姓名为必填项！")
                elif not symptoms.strip():
                    st.error("❌ 主要症状或体征为必填项！")
                elif not diagnosis_result.strip():
                    st.error("❌ 最终诊断结果为必填项！")
                else:
                    updated = {
                        "patient_name": patient_name.strip(),
                        "id_number": id_number.strip(),
                        "age": age,
                        "gender": gender,
                        "symptoms": symptoms.strip(),
                        "notes": notes.strip(),
                        "examinations": examinations.strip(),
                        "diagnosis_result": diagnosis_result.strip(),
                        "treatment_decision": treatment_decision.strip(),
                        "diagnosis_time": diagnosis_time.strip(),
                        "doctor": doctor.strip(),
                    }
                    if dr.update_record(record_id, updated):
                        st.toast(f"✅ 记录已更新", icon="✅")
                        ol.add_log("record_crud", f"编辑诊断记录：患者「{patient_name.strip()}」，ID: {record_id}", operator=st.session_state.get("current_user", ""))
                        st.session_state["diagnosis_page"] = "list"
                        st.rerun()
                    else:
                        st.error("❌ 更新失败")

        if st.button("🔙 返回列表", use_container_width=True):
            st.session_state["diagnosis_page"] = "list"
            st.rerun()

    # ========== 详情视图 ==========
    elif current_page == "detail":
        record_id = st.session_state.get("viewing_record_id")
        rec = dr.get_record(record_id) if record_id else None

        if not rec:
            st.error("❌ 未找到该记录")
            st.session_state["diagnosis_page"] = "list"
            st.rerun()
        else:
            st.markdown(f"### 👤 患者详情 — {rec.get('patient_name', '')}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**患者姓名：** {rec.get('patient_name', '')}")
                st.markdown(f"**身份证号：** {rec.get('id_number', '未填写')}")
                st.markdown(f"**年龄：** {rec.get('age', '')} 岁")
                st.markdown(f"**性别：** {rec.get('gender', '')}")
                st.markdown(f"**诊断时间：** {rec.get('diagnosis_time', '未填写')}")
                st.markdown(f"**诊断人：** {rec.get('doctor', '未填写')}")
            with col2:
                st.markdown(f"**主要症状或体征：**")
                st.info(rec.get('symptoms', '无'))
                st.markdown(f"**备注（过敏史/特殊状态）：**")
                st.info(rec.get('notes', '无') if rec.get('notes') else '无')

            st.markdown("---")
            st.markdown(f"**🔬 进行的检查：**")
            st.write(rec.get('examinations', '无') if rec.get('examinations') else '无')

            st.markdown(f"**📝 最终诊断结果：**")
            st.success(rec.get('diagnosis_result', '未填写'))

            st.markdown(f"**💊 诊断决策（用药等）：**")
            st.write(rec.get('treatment_decision', '无') if rec.get('treatment_decision') else '无')

            st.markdown("---")
            st.caption(f"记录ID: {rec.get('id', '')} | 创建时间: {rec.get('create_time', '')} | 更新时间: {rec.get('update_time', '')}")

            col_b1, col_b2, col_b3, col_b4 = st.columns(4)
            with col_b1:
                if st.button("🔙 返回列表", use_container_width=True):
                    st.session_state["diagnosis_page"] = "list"
                    st.rerun()
            with col_b2:
                if st.button("✏️ 编辑", use_container_width=True):
                    st.session_state["editing_record_id"] = record_id
                    st.session_state["diagnosis_page"] = "edit"
                    st.rerun()
            with col_b3:
                if st.button("🗑️ 删除", use_container_width=True):
                    if dr.delete_record(record_id):
                        st.toast("✅ 已删除", icon="🗑️")
                        st.session_state["diagnosis_page"] = "list"
                        st.rerun()
            with col_b4:
                if st.button("📤 同步到知识库", type="primary", use_container_width=True):
                    kb_text = dr.format_record_for_knowledge_base(rec)
                    kb_filename = f"诊断记录_{rec.get('patient_name', 'unknown')}_{rec.get('id', '')}.txt"
                    try:
                        result = st.session_state["service"].upload_by_str(kb_text, kb_filename)
                        if "成功" in result:
                            st.toast(f"✅ 已同步到知识库", icon="✅")
                            st.success(f"记录已成功同步到知识库（文件名：{kb_filename}）")
                            del st.session_state["rag"]
                            del st.session_state["service"]
                        elif "跳过" in result:
                            st.info(f"ℹ️ 该记录内容已在知识库中（MD5重复）")
                        else:
                            st.error(f"❌ 同步失败：{result}")
                    except Exception as e:
                        st.error(f"❌ 同步出错：{str(e)}")

elif page == "操作日志":
    st.markdown(f'<div class="page-banner"><div class="page-banner-title">{cfg["title"]}</div><div class="page-banner-desc">{cfg["desc"]}</div></div>', unsafe_allow_html=True)

    # 筛选与搜索区域
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        action_filter = st.selectbox(
            "操作类型筛选",
            ["全部", "登录系统", "退出登录", "注册账号", "上传知识库", "删除知识库文档",
             "鉴别诊断", "用药安全核查", "诊断记录操作", "导出PDF报告", "智能问答"],
            index=0,
        )
    with col_f2:
        keyword = st.text_input("关键词搜索", placeholder="搜索操作详情或操作人...")
    with col_f3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()

    # 类型筛选映射
    type_map = {
        "全部": None, "登录系统": "login", "退出登录": "logout", "注册账号": "register",
        "上传知识库": "upload", "删除知识库文档": "kb_delete", "鉴别诊断": "diagnosis",
        "用药安全核查": "drug_safety", "诊断记录操作": "record_crud", "导出PDF报告": "pdf_export",
        "智能问答": "qa_chat",
    }

    # 分页参数
    if "log_page" not in st.session_state:
        st.session_state["log_page"] = 1

    page_size = 20
    action_type = type_map.get(action_filter)
    kw = keyword.strip() if keyword.strip() else None

    result = ol.get_logs(
        page=st.session_state["log_page"],
        page_size=page_size,
        action_type=action_type,
        keyword=kw,
    )

    total = result["total"]
    records = result["records"]
    total_pages = result["total_pages"]
    current_page = result["page"]

    # 统计信息
    today_count = ol.get_today_count()
    type_stats = ol.get_action_type_stats()
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric("今日操作次数", today_count)
    with col_s2:
        st.metric("总操作记录", total)
    with col_s3:
        st.metric("操作类型数", len(type_stats))

    # 日志列表
    if not records:
        st.info("暂无操作日志记录。")
    else:
        for log in records:
            action_type_label = ol.ACTION_TYPE_LABELS.get(log.get("action_type", ""), log.get("action_type", ""))
            status = log.get("status", "success")
            if status == "success":
                status_icon = "✅"
            elif status == "error":
                status_icon = "❌"
            else:
                status_icon = "⚠️"

            with st.container():
                cols = st.columns([1, 2, 3, 1])
                with cols[0]:
                    st.markdown(f"**{log.get('time', '')}**")
                with cols[1]:
                    st.markdown(f"{status_icon} {action_type_label}")
                with cols[2]:
                    st.markdown(log.get("detail", ""))
                with cols[3]:
                    st.markdown(f"`{log.get('operator', '')}`")
                st.markdown("---")

        # 分页控件
        col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns([1, 1, 2, 1, 1])
        with col_p1:
            if st.button("◀ 上一页", disabled=(current_page <= 1), use_container_width=True):
                st.session_state["log_page"] = current_page - 1
                st.rerun()
        with col_p2:
            st.markdown(f"<div style='text-align:center;padding:6px 0;'>第 {current_page}/{total_pages} 页</div>", unsafe_allow_html=True)
        with col_p3:
            # 跳转页码输入
            jump_page = st.number_input("跳转到", min_value=1, max_value=total_pages, value=current_page, step=1, label_visibility="collapsed")
        with col_p4:
            if st.button("跳转", use_container_width=True):
                st.session_state["log_page"] = jump_page
                st.rerun()
        with col_p5:
            if st.button("下一页 ▶", disabled=(current_page >= total_pages), use_container_width=True):
                st.session_state["log_page"] = current_page + 1
                st.rerun()

# ==================== 关闭 content-area ====================
st.markdown('</div>', unsafe_allow_html=True)