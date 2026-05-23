<template>
  <div class="page-container">
    <div class="page-header">
      <h2>知识库管理</h2>
      <p>智能临床知识管理 · 支持文本向量化与去重上传</p>
    </div>

    <!-- 上传区域 -->
    <el-card shadow="never" class="upload-card">
      <el-row :gutter="16" align="middle">
        <el-col :span="18">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :show-file-list="true"
            :limit="1"
            accept=".txt,.pdf,.docx,.md"
            :on-change="handleFileChange"
          >
            <el-button type="primary" :icon="Upload">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持 TXT / PDF / DOCX / MD 格式，文件内容将作为知识库检索来源</div>
            </template>
          </el-upload>
        </el-col>
        <el-col :span="6">
          <el-button
            type="success"
            :icon="UploadFilled"
            :loading="uploading"
            :disabled="!selectedFile"
            @click="handleUpload"
            style="width: 100%"
          >
            上传到知识库
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 文件详情 -->
    <el-card v-if="selectedFile" shadow="never" class="file-detail-card">
      <template #header>
        <span>文件详情</span>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="文件名">{{ selectedFile.name }}</el-descriptions-item>
        <el-descriptions-item label="文件格式">.{{ selectedFile.name.split('.').pop() }}</el-descriptions-item>
        <el-descriptions-item label="文件大小">{{ (selectedFile.size / 1024).toFixed(2) }} KB</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 上传记录 -->
    <el-card shadow="never" class="history-card">
      <template #header>
        <span>最近上传记录</span>
      </template>
      <el-timeline v-if="uploadHistory.length > 0">
        <el-timeline-item
          v-for="(item, index) in uploadHistory"
          :key="index"
          :timestamp="item.time"
          :type="item.status === 'success' ? 'success' : item.status === 'warning' ? 'warning' : 'danger'"
        >
          {{ item.file }} – {{ item.message }}
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无上传记录" />
    </el-card>

    <!-- 知识库文档管理 -->
    <el-card shadow="never" class="doc-list-card">
      <template #header>
        <span>知识库文档管理</span>
        <el-tag type="info" style="margin-left: 8px;">共 {{ documents.length }} 个文档</el-tag>
      </template>

      <el-table :data="documents" stripe style="width: 100%" v-loading="docLoading">
        <el-table-column prop="source" label="文档名称" min-width="200" />
        <el-table-column prop="chunk_count" label="片段数" width="100" align="center" />
        <el-table-column prop="create_time" label="上传时间" width="180" />
        <el-table-column prop="operator" label="操作人" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-popconfirm
              title="确定要删除该文档吗？"
              confirm-button-text="确认删除"
              @confirm="handleDeleteDoc(row.source)"
            >
              <template #reference>
                <el-button type="danger" size="small" :icon="Delete">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!docLoading && documents.length === 0" description="知识库中暂无文档" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, UploadFilled, Delete } from '@element-plus/icons-vue'
import { kbApi } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const uploadRef = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)
const uploadHistory = ref([])
const documents = ref([])
const docLoading = ref(false)

function handleFileChange(file) {
  selectedFile.value = file.raw
}

async function handleUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  try {
    const res = await kbApi.uploadFile(selectedFile.value, userStore.workId)
    if (res.success) {
      ElMessage.success(res.message)
      uploadHistory.value.unshift({
        file: selectedFile.value.name,
        message: res.message,
        status: 'success',
        time: new Date().toLocaleString(),
      })
      await fetchDocuments()
    } else {
      ElMessage.warning(res.message)
      uploadHistory.value.unshift({
        file: selectedFile.value.name,
        message: res.message,
        status: 'warning',
        time: new Date().toLocaleString(),
      })
    }
    selectedFile.value = null
    uploadRef.value?.clearFiles()
  } catch (err) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

async function fetchDocuments() {
  docLoading.value = true
  try {
    const res = await kbApi.getDocuments()
    documents.value = res.documents || []
  } catch (err) {
    console.error('获取文档列表失败:', err)
  } finally {
    docLoading.value = false
  }
}

async function handleDeleteDoc(sourceName) {
  try {
    const res = await kbApi.deleteDocument(sourceName, userStore.workId)
    if (res.success) {
      ElMessage.success(res.message)
      await fetchDocuments()
    } else {
      ElMessage.error(res.message)
    }
  } catch (err) {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchDocuments)
</script>

<style scoped>
.upload-card {
  margin-bottom: 16px;
}

.file-detail-card {
  margin-bottom: 16px;
}

.history-card {
  margin-bottom: 16px;
}

.doc-list-card {
  margin-bottom: 16px;
}
</style>
