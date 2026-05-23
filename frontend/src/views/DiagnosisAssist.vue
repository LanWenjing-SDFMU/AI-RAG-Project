<template>
  <div class="page-container">
    <div class="page-header">
      <h2>鉴别诊断辅助</h2>
      <p>基于知识库的症状分析与鉴别诊断建议</p>
    </div>

    <el-card shadow="never">
      <el-form :model="form" label-position="top">
        <el-form-item label="🩺 主要症状或体征">
          <el-input
            v-model="form.symptoms"
            type="textarea"
            :rows="4"
            placeholder="例如：咳嗽、发热、胸痛、呼吸困难..."
          />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="👤 年龄（岁）">
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
            <el-form-item label="👤 性别">
              <el-select v-model="form.gender" style="width: 100%">
                <el-option label="未指定" value="未指定" />
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button
            type="primary"
            :icon="Search"
            :loading="loading"
            @click="handleGenerate"
            style="width: 100%"
          >
            生成鉴别诊断
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 诊断结果 -->
    <el-card v-if="result" shadow="never" class="result-card">
      <template #header>
        <span>📊 鉴别诊断结果</span>
        <el-tag type="info" style="margin-left: 8px;">基于知识库检索结果</el-tag>
      </template>
      <div class="markdown-content" v-html="renderedResult"></div>

      <el-divider />

      <el-button
        v-if="pdfBytes"
        type="success"
        :icon="Download"
        @click="downloadPdf"
      >
        导出诊断报告 (PDF)
      </el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { diagnosisAssistApi } from '@/api'
import { useUserStore } from '@/stores/user'
import { marked } from 'marked'

const userStore = useUserStore()

const form = ref({
  symptoms: '',
  age: 0,
  gender: '未指定',
})

const loading = ref(false)
const result = ref('')
const pdfBytes = ref('')

const renderedResult = computed(() => {
  if (!result.value) return ''
  return marked(result.value)
})

async function handleGenerate() {
  if (!form.value.symptoms.trim()) {
    ElMessage.warning('请至少输入一个症状或体征')
    return
  }

  loading.value = true
  try {
    const res = await diagnosisAssistApi.generate(form.value, userStore.workId)
    result.value = res.result
    pdfBytes.value = res.pdf_bytes || ''
  } catch (err) {
    ElMessage.error('生成鉴别诊断失败')
  } finally {
    loading.value = false
  }
}

function downloadPdf() {
  if (!pdfBytes.value) return
  const byteCharacters = atob(pdfBytes.value)
  const byteNumbers = new Array(byteCharacters.length)
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i)
  }
  const byteArray = new Uint8Array(byteNumbers)
  const blob = new Blob([byteArray], { type: 'application/pdf' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `诊断报告_${new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')}.pdf`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.result-card {
  margin-top: 16px;
}
</style>
