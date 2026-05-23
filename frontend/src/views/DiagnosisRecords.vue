<template>
  <div class="page-container">
    <div class="page-header">
      <h2>患者诊断记录</h2>
      <p>诊断信息管理 · 支持增删改查与知识库同步</p>
    </div>

    <!-- 列表视图 -->
    <template v-if="currentView === 'list'">
      <el-row :gutter="16" class="toolbar">
        <el-col :span="6">
          <el-button type="primary" :icon="Plus" @click="currentView = 'add'">
            新增诊断记录
          </el-button>
        </el-col>
        <el-col :span="18">
          <el-input
            v-model="searchKeyword"
            placeholder="按患者姓名、身份证号、症状或诊断结果搜索..."
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
      </el-row>

      <el-table :data="records" stripe style="width: 100%" v-loading="loading" @row-click="handleRowClick">
        <el-table-column prop="patient_name" label="患者姓名" width="120" />
        <el-table-column prop="diagnosis_result" label="诊断结果" min-width="200" show-overflow-tooltip />
        <el-table-column prop="diagnosis_time" label="诊断时间" width="180" />
        <el-table-column prop="doctor" label="诊断人" width="100" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" :icon="View" @click.stop="viewRecord(row.id)">查看</el-button>
            <el-button size="small" type="primary" :icon="Edit" @click.stop="editRecord(row.id)">编辑</el-button>
            <el-popconfirm title="确定要删除该记录吗？" @confirm.stop="deleteRecord(row.id)">
              <template #reference>
                <el-button size="small" type="danger" :icon="Delete" @click.stop>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && records.length === 0" description="暂无诊断记录" />
    </template>

    <!-- 新增/编辑视图 -->
    <template v-else-if="currentView === 'add' || currentView === 'edit'">
      <el-card shadow="never">
        <template #header>
          <span>{{ currentView === 'add' ? '新增诊断记录' : '编辑诊断记录' }}</span>
        </template>

        <el-form :model="form" label-position="top" ref="formRef">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="👤 患者姓名 *" prop="patient_name" :rules="[{ required: true, message: '请输入患者姓名' }]">
                <el-input v-model="form.patient_name" placeholder="请输入患者姓名" />
              </el-form-item>
              <el-form-item label="🆔 身份证号">
                <el-input v-model="form.id_number" placeholder="18位身份证号（可选）" />
              </el-form-item>
              <el-form-item label="📅 年龄（岁）">
                <el-input-number v-model="form.age" :min="0" :max="150" :step="1" style="width: 100%" />
              </el-form-item>
              <el-form-item label="⚤ 性别">
                <el-select v-model="form.gender" style="width: 100%">
                  <el-option label="男" value="男" />
                  <el-option label="女" value="女" />
                  <el-option label="其他" value="其他" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="🩺 主要症状或体征 *" prop="symptoms" :rules="[{ required: true, message: '请输入主要症状或体征' }]">
                <el-input v-model="form.symptoms" type="textarea" :rows="3" placeholder="例如：咳嗽、发热、胸痛..." />
              </el-form-item>
              <el-form-item label="📋 备注（过敏史或特殊状态）">
                <el-input v-model="form.notes" type="textarea" :rows="3" placeholder="例如：青霉素过敏、肾功能不全..." />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="🔬 进行的检查">
            <el-input v-model="form.examinations" type="textarea" :rows="2" placeholder="例如：血常规、CT、心电图..." />
          </el-form-item>

          <el-form-item label="📝 最终诊断结果 *" prop="diagnosis_result" :rules="[{ required: true, message: '请输入最终诊断结果' }]">
            <el-input v-model="form.diagnosis_result" type="textarea" :rows="2" placeholder="例如：上呼吸道感染、高血压2级..." />
          </el-form-item>

          <el-form-item label="💊 诊断决策（用药等）">
            <el-input v-model="form.treatment_decision" type="textarea" :rows="2" placeholder="例如：阿莫西林 500mg tid × 7天..." />
          </el-form-item>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="🕒 诊断时间">
                <el-input v-model="form.diagnosis_time" placeholder="格式：YYYY-MM-DD HH:mm" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="诊断人">
                <el-input v-model="form.doctor" disabled />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item>
            <el-button type="primary" :icon="Check" :loading="saving" @click="handleSave">
              {{ currentView === 'add' ? '保存记录' : '更新记录' }}
            </el-button>
            <el-button @click="currentView = 'list'">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </template>

    <!-- 详情视图 -->
    <template v-else-if="currentView === 'detail'">
      <el-card shadow="never">
        <template #header>
          <span>👤 患者详情 — {{ detailRecord?.patient_name }}</span>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="患者姓名">{{ detailRecord?.patient_name }}</el-descriptions-item>
          <el-descriptions-item label="身份证号">{{ detailRecord?.id_number || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="年龄">{{ detailRecord?.age }} 岁</el-descriptions-item>
          <el-descriptions-item label="性别">{{ detailRecord?.gender }}</el-descriptions-item>
          <el-descriptions-item label="诊断时间">{{ detailRecord?.diagnosis_time || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="诊断人">{{ detailRecord?.doctor || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="主要症状或体征" :span="2">
            <el-tag type="warning">{{ detailRecord?.symptoms || '无' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="备注（过敏史/特殊状态）" :span="2">
            {{ detailRecord?.notes || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="进行的检查" :span="2">
            {{ detailRecord?.examinations || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="最终诊断结果" :span="2">
            <el-tag type="success" style="white-space: pre-wrap;">{{ detailRecord?.diagnosis_result }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="诊断决策（用药等）" :span="2">
            {{ detailRecord?.treatment_decision || '无' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />
        <el-space>
          <el-button @click="currentView = 'list'">返回列表</el-button>
          <el-button type="primary" :icon="Edit" @click="editRecord(detailRecord?.id)">编辑</el-button>
          <el-popconfirm title="确定要删除该记录吗？" @confirm="deleteRecord(detailRecord?.id)">
            <template #reference>
              <el-button type="danger" :icon="Delete">删除</el-button>
            </template>
          </el-popconfirm>
          <el-button type="success" :icon="Upload" :loading="syncing" @click="syncToKB">
            同步到知识库
          </el-button>
        </el-space>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Plus, Search, View, Edit, Delete, Check, Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { diagnosisApi } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const currentView = ref('list')
const records = ref([])
const loading = ref(false)
const saving = ref(false)
const syncing = ref(false)
const searchKeyword = ref('')
const formRef = ref(null)
const detailRecord = ref(null)

const form = ref({
  patient_name: '',
  id_number: '',
  age: 0,
  gender: '男',
  symptoms: '',
  notes: '',
  examinations: '',
  diagnosis_result: '',
  treatment_decision: '',
  diagnosis_time: new Date().toISOString().slice(0, 16).replace('T', ' '),
  doctor: '',
})

let editingId = null

async function fetchRecords(keyword = '') {
  loading.value = true
  try {
    const res = await diagnosisApi.getRecords(keyword)
    records.value = res.records || []
  } catch (err) {
    console.error('获取记录失败:', err)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  fetchRecords(searchKeyword.value)
}

function resetForm() {
  form.value = {
    patient_name: '',
    id_number: '',
    age: 0,
    gender: '男',
    symptoms: '',
    notes: '',
    examinations: '',
    diagnosis_result: '',
    treatment_decision: '',
    diagnosis_time: new Date().toISOString().slice(0, 16).replace('T', ' '),
    doctor: userStore.workId,
  }
  editingId = null
}

function viewRecord(id) {
  diagnosisApi.getRecord(id).then(res => {
    detailRecord.value = res
    currentView.value = 'detail'
  })
}

function editRecord(id) {
  editingId = id
  diagnosisApi.getRecord(id).then(res => {
    form.value = {
      patient_name: res.patient_name,
      id_number: res.id_number,
      age: res.age,
      gender: res.gender,
      symptoms: res.symptoms,
      notes: res.notes,
      examinations: res.examinations,
      diagnosis_result: res.diagnosis_result,
      treatment_decision: res.treatment_decision,
      diagnosis_time: res.diagnosis_time,
      doctor: res.doctor,
    }
    currentView.value = 'edit'
  })
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (currentView.value === 'add') {
      await diagnosisApi.createRecord(form.value, userStore.workId)
      ElMessage.success('记录已保存')
    } else {
      await diagnosisApi.updateRecord(editingId, form.value, userStore.workId)
      ElMessage.success('记录已更新')
    }
    currentView.value = 'list'
    await fetchRecords()
  } catch (err) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function deleteRecord(id) {
  try {
    await diagnosisApi.deleteRecord(id, userStore.workId)
    ElMessage.success('记录已删除')
    if (currentView.value === 'detail') {
      currentView.value = 'list'
    }
    await fetchRecords()
  } catch (err) {
    ElMessage.error('删除失败')
  }
}

async function syncToKB() {
  if (!detailRecord.value?.id) return
  syncing.value = true
  try {
    const res = await diagnosisApi.syncToKB(detailRecord.value.id, userStore.workId)
    if (res.success) {
      ElMessage.success(res.message)
    } else {
      ElMessage.warning(res.message)
    }
  } catch (err) {
    ElMessage.error('同步失败')
  } finally {
    syncing.value = false
  }
}

function handleRowClick(row) {
  viewRecord(row.id)
}

watch(currentView, (val) => {
  if (val === 'add') {
    resetForm()
  }
})

onMounted(() => {
  fetchRecords()
  resetForm()
})
</script>

<style scoped>
.toolbar {
  margin-bottom: 16px;
}
</style>
