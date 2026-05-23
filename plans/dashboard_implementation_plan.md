# 首页数据可视化仪表盘 — 分步实施计划

## 数据源分析

| 数据源 | 位置 | 可用数据 |
|--------|------|----------|
| Chroma 向量库 | `chroma_db/` | 文档片段总数、各 source 文件分布 |
| 诊断记录 | `diagnosis_records.json` | 患者姓名、诊断结果、诊断时间、诊断人 |
| 聊天历史 | `chat_history/*.json` | 各会话的消息数量、最后活跃时间 |
| 用户数据 | `users.json` | 注册用户数 |
| 上传记录 | `session_state.upload_history` | 上传文件名、结果、时间戳（仅当前会话） |

---

## 分步实施计划

### 第一步：数据采集模块 — `dashboard_data.py`（新建）

**目标**：创建一个独立的数据采集模块，从各数据源提取统计信息。

**功能**：
1. `get_kb_stats()` — 从 Chroma 获取知识库统计
   - 总文档片段数
   - 按 source 文件分组的文档数
   - 各文件的上传时间分布
2. `get_diagnosis_stats()` — 从 `diagnosis_records.json` 获取诊断统计
   - 总诊断记录数
   - 按诊断结果分组的疾病分布
   - 按日期分组的诊断趋势
   - 按诊断人分组的统计
3. `get_chat_stats()` — 从 `chat_history/` 获取对话统计
   - 总对话数
   - 各会话的消息数
4. `get_user_stats()` — 从 `users.json` 获取用户统计
   - 注册用户总数

**输出**：返回字典格式的统计数据，供首页调用。

**依赖**：无新增依赖，使用 `os`、`json`、`collections.Counter`

---

### 第二步：首页布局重构 — 修改 `app_qa.py` 首页分支

**目标**：将首页从"欢迎卡片 + 3个统计数字"升级为"欢迎区 + 图表仪表盘"。

**新布局结构**：

```
┌─────────────────────────────────────────┐
│           欢迎标题 + 系统描述              │  ← 保留现有欢迎卡片
│         "智能临床决策支持系统"              │
├──────────┬──────────┬──────────┬─────────┤
│ 知识库    │ 诊断记录   │ 注册用户   │ 对话数   │  ← 4个关键指标卡片
│ 片段数    │ 总数      │ 数        │         │
├──────────┴──────────┴──────────┴─────────┤
│  ┌─────────────────────────────────────┐  │
│  │  诊断记录趋势图（折线图）              │  │  ← 近7天/30天诊断数量变化
│  │  ▁▃▅▇▅▃▁                            │  │
│  └─────────────────────────────────────┘  │
├──────────┬──────────────────────────────┤
│ 疾病分布   │  知识库文件分布               │  ← 两个饼图并排
│ 饼图      │  饼图                        │
│ (Top 8)  │  (各source占比)              │
└──────────┴──────────────────────────────┘
```

---

### 第三步：图表渲染

**方案选择**：使用 Streamlit 原生图表（无需额外安装依赖）

| 图表类型 | Streamlit API | 数据 |
|----------|---------------|------|
| 关键指标 | `st.metric()` | 4个核心数字 |
| 诊断趋势 | `st.line_chart()` | 按日期的诊断记录数 |
| 疾病分布 | `st.bar_chart()` | 诊断结果频次（Top 8） |
| 知识库分布 | `st.bar_chart()` | 各 source 文件的片段数 |

**备选方案**（如需更美观的图表）：`streamlit-echarts`
- 安装：`pip install streamlit-echarts`
- 优势：支持饼图、更丰富的样式
- 劣势：需要额外安装依赖

---

### 第四步：CSS 样式适配

在首页的 `<style>` 块中新增仪表盘相关样式：
- `.dashboard-metrics` — 指标卡片网格容器
- `.metric-card` — 单个指标卡片（与现有 `.home-stat-card` 风格统一）
- `.chart-container` — 图表容器（白色背景、圆角、阴影）
- `.chart-title` — 图表标题

---

## 详细实施步骤（按执行顺序）

### Step 1：创建 `dashboard_data.py`

```python
"""
首页仪表盘数据采集模块
从各数据源提取统计信息，供首页可视化展示
"""
import os
import json
from collections import Counter
from datetime import datetime, timedelta

# 文件路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIAGNOSIS_FILE = os.path.join(BASE_DIR, "diagnosis_records.json")
CHAT_HISTORY_DIR = os.path.join(BASE_DIR, "chat_history")
USERS_FILE = os.path.join(BASE_DIR, "users.json")


def get_kb_stats(vector_store=None) -> dict:
    """
    获取知识库统计信息
    Args:
        vector_store: Chroma 向量库对象（可选），如果为 None 则返回默认值
    Returns:
        dict: {total_chunks, source_distribution: [{name, count}, ...]}
    """
    stats = {
        "total_chunks": 0,
        "source_distribution": [],
    }
    if vector_store is None:
        return stats
    try:
        # 从 Chroma 获取所有文档的元数据
        collection_data = vector_store._collection.get()
        metadatas = collection_data.get("metadatas", [])
        stats["total_chunks"] = len(metadatas)
        
        # 按 source 分组统计
        source_counter = Counter()
        for meta in metadatas:
            source = meta.get("source", "未知")
            source_counter[source] += 1
        
        stats["source_distribution"] = [
            {"name": name, "count": count}
            for name, count in source_counter.most_common()
        ]
    except Exception:
        pass
    return stats


def get_diagnosis_stats() -> dict:
    """
    获取诊断记录统计信息
    Returns:
        dict: {total_records, disease_distribution, daily_trend, doctor_distribution}
    """
    stats = {
        "total_records": 0,
        "disease_distribution": [],      # 诊断结果分布
        "daily_trend": [],               # 每日诊断数趋势
        "doctor_distribution": [],       # 按诊断人统计
    }
    
    try:
        if not os.path.exists(DIAGNOSIS_FILE):
            return stats
        
        with open(DIAGNOSIS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return stats
            records = json.loads(content)
        
        stats["total_records"] = len(records)
        
        # 诊断结果分布
        disease_counter = Counter()
        # 每日趋势
        date_counter = Counter()
        # 诊断人统计
        doctor_counter = Counter()
        
        for rec in records:
            diagnosis = rec.get("diagnosis_result", "未记录")
            disease_counter[diagnosis] += 1
            
            create_time = rec.get("create_time", "")
            if create_time:
                date_key = create_time[:10]  # "2026-05-20"
                date_counter[date_key] += 1
            
            doctor = rec.get("doctor", "未记录")
            doctor_counter[doctor] += 1
        
        stats["disease_distribution"] = [
            {"name": name, "count": count}
            for name, count in disease_counter.most_common(8)  # Top 8
        ]
        
        # 按日期排序
        sorted_dates = sorted(date_counter.items())
        stats["daily_trend"] = [
            {"date": date, "count": count}
            for date, count in sorted_dates
        ]
        
        stats["doctor_distribution"] = [
            {"name": name, "count": count}
            for name, count in doctor_counter.most_common()
        ]
    except Exception:
        pass
    
    return stats


def get_chat_stats() -> dict:
    """
    获取聊天历史统计信息
    Returns:
        dict: {total_sessions, total_messages}
    """
    stats = {
        "total_sessions": 0,
        "total_messages": 0,
    }
    
    try:
        if not os.path.exists(CHAT_HISTORY_DIR):
            return stats
        
        session_files = [f for f in os.listdir(CHAT_HISTORY_DIR) if f.endswith(".json")]
        stats["total_sessions"] = len(session_files)
        
        total_msgs = 0
        for fname in session_files:
            fpath = os.path.join(CHAT_HISTORY_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    msgs = json.load(f)
                    total_msgs += len(msgs)
            except Exception:
                pass
        
        stats["total_messages"] = total_msgs
    except Exception:
        pass
    
    return stats


def get_user_stats() -> dict:
    """
    获取用户统计信息
    Returns:
        dict: {total_users}
    """
    stats = {"total_users": 0}
    
    try:
        if not os.path.exists(USERS_FILE):
            return stats
        
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
        
        stats["total_users"] = len(users)
    except Exception:
        pass
    
    return stats
```

### Step 2：修改 `app_qa.py` 首页分支

**修改位置**：`app_qa.py` 第 771-881 行（`if page == "首页":` 分支）

**修改内容**：
1. 在文件顶部导入 `dashboard_data` 模块
2. 在首页分支中：
   a. 调用 `dashboard_data.get_kb_stats(vector_store)` 等函数获取数据
   b. 保留现有的欢迎卡片（标题 + 描述）
   c. 在欢迎卡片下方新增"4个关键指标"行（使用 `st.metric()` 或自定义 HTML）
   d. 新增"诊断记录趋势图"（使用 `st.line_chart()`）
   e. 新增"疾病分布"和"知识库文件分布"两个并排图表（使用 `st.bar_chart()`）
3. 在首页 `<style>` 中新增仪表盘 CSS 样式

### Step 3：重启验证

1. 重启 Streamlit 应用
2. 检查首页是否正常显示所有图表
3. 验证数据是否正确（诊断记录数、知识库片段数等）

---

## 代码修改清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `RagProject/dashboard_data.py` | **新建** | 数据采集模块 |
| `RagProject/app_qa.py` | **修改** | 首页分支重构 + 导入新模块 |

---

## 预期效果

实施完成后，首页将展示：
1. **欢迎卡片** — 保留现有设计（标题 + 描述 + 背景图）
2. **4个关键指标** — 知识库片段数、诊断记录数、注册用户数、对话数
3. **诊断趋势折线图** — 展示每日诊断记录数量变化
4. **疾病分布柱状图** — Top 8 诊断结果频次
5. **知识库文件分布柱状图** — 各 source 文件的片段数占比

所有图表使用 Streamlit 原生 API，无需额外安装依赖。
