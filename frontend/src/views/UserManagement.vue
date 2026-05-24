<template>
  <div class="user-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <span class="page-desc">查看和管理所有注册医生用户</span>
    </div>

    <el-card shadow="never" class="user-table-card">
      <el-table
        :data="userList"
        v-loading="loading"
        stripe
        style="width: 100%"
        empty-text="暂无用户数据"
      >
        <el-table-column prop="work_id" label="工号" width="180" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
              {{ row.role === 'admin' ? '管理员' : '医生' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" min-width="200" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-popconfirm
              title="确定要删除该用户吗？"
              confirm-button-text="确认删除"
              cancel-button-text="取消"
              @confirm="handleDelete(row.work_id)"
            >
              <template #reference>
                <el-button
                  type="danger"
                  size="small"
                  :disabled="row.work_id === currentUserId"
                  :icon="Delete"
                >
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { userApi } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const userList = ref([])
const currentUserId = ref(userStore.workId)

async function fetchUsers() {
  loading.value = true
  try {
    const res = await userApi.getList()
    if (res && res.users) {
      userList.value = res.users
    } else {
      userList.value = []
    }
  } catch (e) {
    ElMessage.error('获取用户列表失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDelete(workId) {
  try {
    await userApi.deleteUser(workId)
    ElMessage.success(`用户 ${workId} 已删除`)
    await fetchUsers()
  } catch (e) {
    const msg = e.response?.data?.detail || '删除用户失败'
    ElMessage.error(msg)
    console.error(e)
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management {
  padding: 24px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 6px;
  font-size: 1.3rem;
  color: #303133;
}

.page-desc {
  font-size: 0.85rem;
  color: #909399;
}

.user-table-card {
  border-radius: 8px;
}
</style>
