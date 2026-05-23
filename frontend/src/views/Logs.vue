<template>
  <div class="page-container">
    <div class="page-header">
      <h2>操作日志</h2>
      <p>系统操作记录 · 支持筛选与搜索</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value">{{ stats.today_count }}</div>
          <div class="stat-label">今日操作次数</div>
        </el-card>
      </el-col>
      <el-col :span="18">
        <el-card shadow="never" class="stat-card">
          <div class="type-tags">
            <el-tag
              v-for="item in stats.type_stats"
              :key="item.type"
              size="small"
              :type="tagType(item.type)"
              class="type-tag"
            >
              {{ actionTypeLabel(item.type) }}: {{ item.count }}
            </el-tag>
          </div>
          <div class="stat-label">各操作类型统计</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选工具栏 -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-select
            v-model="filters.action_type"
            placeholder="操作类型"
            clearable
            style="width: 100%"
            @change="handleFilterChange"
          >
            <el-option
              v-for="(label, key) in actionTypes"
              :key="key"
              :label="label"
              :value="key"
            />
          </el-select>
        </el-col>
        <el-col :span="12">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索操作详情或操作人..."
            clearable
            :prefix-icon="Search"
            @input="handleFilterChange"
          />
        </el-col>
        <el-col :span="6" style="text-align: right">
          <el-button :icon="Refresh" @click="refreshLogs">刷新</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 日志表格 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="logs" stripe style="width: 100%" v-loading="loading" empty-text="暂无操作日志">
        <el-table-column prop="time" label="操作时间" width="180" />
        <el-table-column label="操作类型" width="140">
          <template #default="{ row }">
            <el-tag :type="tagType(row.action_type)" size="small">
              {{ actionTypeLabel(row.action_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="操作详情" min-width="300" show-overflow-tooltip />
        <el-table-column prop="operator" label="操作人" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="pagination.total > 0">
        <el-pagination
          v-model:current-page="pagination.page"
          :page-size="pagination.page_size"
          :total="pagination.total"
          layout="total, prev, pager, next, jumper"
          background
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import { logApi } from '@/api'

const loading = ref(false)
const logs = ref([])
const actionTypes = ref({})

const filters = reactive({
  action_type: '',
  keyword: '',
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
})

const stats = reactive({
  today_count: 0,
  type_stats: [],
})

const TAG_TYPE_MAP = {
  login: '',
  logout: 'info',
  register: 'success',
  upload: 'warning',
  kb_delete: 'danger',
  diagnosis: 'primary',
  drug_safety: 'warning',
  record_crud: '',
  pdf_export: 'success',
  qa_chat: 'primary',
}

function tagType(actionType) {
  return TAG_TYPE_MAP[actionType] || ''
}

function actionTypeLabel(type) {
  return actionTypes.value[type] || type
}

async function fetchLogs() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
    }
    if (filters.action_type) {
      params.action_type = filters.action_type
    }
    if (filters.keyword) {
      params.keyword = filters.keyword
    }
    const res = await logApi.getList(params)
    logs.value = res.records || []
    pagination.total = res.total || 0
    pagination.page = res.page || 1
  } catch (e) {
    console.error('获取日志列表失败:', e)
    logs.value = []
  } finally {
    loading.value = false
  }
}

async function fetchStats() {
  try {
    const res = await logApi.getStats()
    stats.today_count = res.today_count || 0
    stats.type_stats = res.type_stats || []
  } catch (e) {
    console.error('获取日志统计失败:', e)
  }
}

async function fetchActionTypes() {
  try {
    const res = await logApi.getActionTypes()
    actionTypes.value = res || {}
  } catch (e) {
    console.error('获取操作类型失败:', e)
  }
}

function handleFilterChange() {
  pagination.page = 1
  fetchLogs()
}

function handlePageChange(page) {
  pagination.page = page
  fetchLogs()
}

function refreshLogs() {
  filters.action_type = ''
  filters.keyword = ''
  pagination.page = 1
  fetchLogs()
  fetchStats()
}

onMounted(() => {
  fetchLogs()
  fetchStats()
  fetchActionTypes()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 4px;
  font-size: 1.3rem;
  color: #303133;
}

.page-header p {
  margin: 0;
  font-size: 0.85rem;
  color: #909399;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  border-radius: 8px;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #409EFF;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.8rem;
  color: #909399;
  margin-top: 4px;
}

.type-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 4px;
}

.type-tag {
  font-size: 0.75rem;
}

.filter-card {
  margin-bottom: 16px;
  border-radius: 8px;
}

.table-card {
  border-radius: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px 0 0;
}
</style>
