<template>
  <div class="page-container">
    <div class="page-header">
      <h2>用药安全核查</h2>
      <p>基于知识库的药物安全信息检索与核查</p>
    </div>

    <el-card shadow="never">
      <el-form :model="form" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="💊 药物名称 *" required>
              <el-input
                v-model="form.drug_name"
                placeholder="例如：阿司匹林、布洛芬"
              />
            </el-form-item>
            <el-form-item label="👤 患者年龄（岁）">
              <el-input-number
                v-model="form.age"
                :min="0"
                :max="150"
                :step="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="⚠️ 过敏史">
              <el-input
                v-model="form.allergy"
                placeholder="例如：青霉素过敏"
              />
            </el-form-item>
            <el-form-item label="📋 备注">
              <el-input
                v-model="form.notes"
                placeholder="例如：肾功能不全、妊娠状态"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button
            type="primary"
            :icon="Search"
            :loading="loading"
            @click="handleCheck"
            style="width: 100%"
          >
            核查
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 核查结果 -->
    <el-card v-if="result" shadow="never" class="result-card">
      <template #header>
        <span>📋 核查结果</span>
      </template>
      <div class="markdown-content" v-html="renderedResult"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { drugSafetyApi } from '@/api'
import { useUserStore } from '@/stores/user'
import { marked } from 'marked'

const userStore = useUserStore()

const form = ref({
  drug_name: '',
  age: 0,
  allergy: '',
  notes: '',
})

const loading = ref(false)
const result = ref('')

const renderedResult = computed(() => {
  if (!result.value) return ''
  return marked(result.value)
})

async function handleCheck() {
  if (!form.value.drug_name.trim()) {
    ElMessage.warning('请填写药物名称')
    return
  }

  loading.value = true
  try {
    const res = await drugSafetyApi.check(form.value, userStore.workId)
    result.value = res.result
  } catch (err) {
    ElMessage.error('核查失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.result-card {
  margin-top: 16px;
}
</style>
