<template>
  <div class="page-container">
    <div class="page-header">
      <h2>首页</h2>
      <p>欢迎使用</p>
    </div>

    <el-skeleton :loading="loading" animated :count="4">
      <template #default>
        <!-- 4个关键指标 -->
        <el-row :gutter="16" class="metrics-row">
          <el-col :span="6" v-for="metric in metrics" :key="metric.label">
            <el-card shadow="never" class="metric-card">
              <div class="metric-value">{{ metric.value }}</div>
              <div class="metric-label">{{ metric.label }}</div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 诊断趋势 -->
        <el-card shadow="never" class="chart-card" v-if="diagTrendData.length > 0">
          <template #header>
            <span class="chart-title">诊断记录趋势</span>
          </template>
          <div ref="trendChartRef" style="height: 300px"></div>
        </el-card>

        <!-- 疾病分布 + 知识库文件分布 -->
        <el-row :gutter="16">
          <el-col :span="12">
            <el-card shadow="never" class="chart-card">
              <template #header>
                <span class="chart-title">诊断结果分布（Top 8）</span>
              </template>
              <div v-if="diseaseData.length > 0" ref="diseaseChartRef" style="height: 300px"></div>
              <el-empty v-else description="暂无诊断记录" />
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="never" class="chart-card">
              <template #header>
                <span class="chart-title">知识库文件分布</span>
              </template>
              <div v-if="sourceData.length > 0" ref="sourceChartRef" style="height: 300px"></div>
              <el-empty v-else description="暂无知识库数据" />
            </el-card>
          </el-col>
        </el-row>
      </template>
    </el-skeleton>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { dashboardApi } from '@/api'

const loading = ref(true)
const metrics = ref([])
const diagTrendData = ref([])
const diseaseData = ref([])
const sourceData = ref([])

const trendChartRef = ref(null)
const diseaseChartRef = ref(null)
const sourceChartRef = ref(null)

async function fetchData() {
  try {
    const res = await dashboardApi.getStats()
    const { kb_stats, diag_stats, chat_stats, user_stats } = res

    metrics.value = [
      { label: '知识库片段数', value: kb_stats.total_chunks },
      { label: '诊断记录数', value: diag_stats.total_records },
      { label: '注册用户数', value: user_stats.total_users },
      { label: '对话会话数', value: chat_stats.total_sessions },
    ]

    diagTrendData.value = diag_stats.daily_trend || []
    diseaseData.value = diag_stats.disease_distribution || []
    sourceData.value = kb_stats.source_distribution || []
  } catch (err) {
    console.error('获取仪表盘数据失败:', err)
  } finally {
    // 先关闭骨架屏，让 DOM 渲染出来
    loading.value = false
    // 再等 DOM 更新后渲染图表
    await nextTick()
    renderCharts()
  }
}

function renderCharts() {
  // 使用简单的 div 柱状图替代 ECharts（避免额外依赖）
  renderBarChart('trendChartRef', diagTrendData.value, 'date', 'count', '#409EFF')
  renderBarChart('diseaseChartRef', diseaseData.value, 'name', 'count', '#67c23a')
  renderBarChart('sourceChartRef', sourceData.value, 'name', 'count', '#e6a23c')
}

function renderBarChart(refName, data, labelKey, valueKey, color) {
  const el = refName === 'trendChartRef' ? trendChartRef.value
    : refName === 'diseaseChartRef' ? diseaseChartRef.value
    : sourceChartRef.value

  if (!el || !data.length) return

  const maxVal = Math.max(...data.map(d => d[valueKey]), 1)
  const barHeight = Math.max(20, Math.min(40, 300 / data.length))

  let html = '<div style="display:flex;flex-direction:column;gap:4px;">'
  data.forEach(item => {
    const pct = (item[valueKey] / maxVal * 100).toFixed(1)
    const label = item[labelKey].length > 15 ? item[labelKey].slice(0, 15) + '...' : item[labelKey]
    html += `
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="width:80px;font-size:12px;color:#5a6a7e;text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${item[labelKey]}">${label}</span>
        <div style="flex:1;background:#f0f2f5;border-radius:4px;height:${barHeight}px;overflow:hidden;">
          <div style="width:${pct}%;background:${color};height:100%;border-radius:4px;transition:width 0.6s ease;display:flex;align-items:center;justify-content:flex-end;padding-right:6px;min-width:30px;">
            <span style="color:#fff;font-size:11px;font-weight:600;">${item[valueKey]}</span>
          </div>
        </div>
      </div>
    `
  })
  html += '</div>'
  el.innerHTML = html
}

onMounted(fetchData)
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(
      rgba(26, 58, 107, 0.45),
      rgba(42, 82, 152, 0.45)
    ),
    url('/login-bg.jpg.png') center/cover no-repeat fixed;
}

.metrics-row {
  margin-bottom: 16px;
}

.metric-card {
  text-align: center;
}

.metric-value {
  font-size: 1.6rem;
  font-weight: 700;
  color: #409EFF;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 0.8rem;
  color: #5a6a7e;
}

.chart-card {
  margin-bottom: 16px;
}

.chart-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #304156;
}
</style>
