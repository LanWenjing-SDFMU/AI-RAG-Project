<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-title">基层医生医疗辅助系统</div>
      <div class="login-subtitle">医生/管理员登录</div>

      <el-alert
        v-if="message"
        :title="message"
        :type="messageType"
        show-icon
        :closable="true"
        class="login-message"
      />

      <el-tabs v-model="activeTab" class="login-tabs" @tab-change="clearMessage">
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            label-position="top"
            size="large"
          >
            <el-form-item label="工号" prop="work_id">
              <el-input
                v-model="loginForm.work_id"
                placeholder="请输入工号"
                :prefix-icon="User"
              />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                class="login-btn"
                :loading="loading"
                @click="handleLogin"
              >
                登 录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            label-position="top"
            size="large"
          >
            <el-form-item label="工号" prop="work_id">
              <el-input
                v-model="registerForm.work_id"
                placeholder="请输入工号"
                :prefix-icon="User"
              />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码（至少4位）"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                class="login-btn"
                :loading="loading"
                @click="handleRegister"
              >
                注 册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const message = ref('')
const messageType = ref('info')

const loginFormRef = ref(null)
const registerFormRef = ref(null)

const loginForm = reactive({
  work_id: '',
  password: '',
})

const registerForm = reactive({
  work_id: '',
  password: '',
  confirmPassword: '',
})

const loginRules = {
  work_id: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const registerRules = {
  work_id: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, message: '密码长度不能少于4位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次密码输入不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

function clearMessage() {
  message.value = ''
}

async function handleLogin() {
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await authApi.login(loginForm)
    userStore.setLogin(res.access_token, res.work_id)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (err) {
    message.value = err.response?.data?.detail || '登录失败'
    messageType.value = 'error'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  const valid = await registerFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authApi.register({
      work_id: registerForm.work_id,
      password: registerForm.password,
    })
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.work_id = registerForm.work_id
    registerForm.work_id = ''
    registerForm.password = ''
    registerForm.confirmPassword = ''
  } catch (err) {
    message.value = err.response?.data?.detail || '注册失败'
    messageType.value = 'error'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
      rgba(26, 58, 107, 0.55),
      rgba(42, 82, 152, 0.55)
    ),
    url('/login-bg.jpg.png') center/cover no-repeat;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 12px;
  padding: 40px 36px 32px;
  width: 420px;
  max-width: 92vw;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2);
}

.login-title {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  color: #1a3a6b;
  margin-bottom: 6px;
  letter-spacing: 2px;
}

.login-subtitle {
  text-align: center;
  font-size: 13px;
  color: #97a8be;
  margin-bottom: 24px;
}

.login-message {
  margin-bottom: 16px;
}

.login-tabs {
  margin-bottom: 8px;
}

.login-btn {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  font-weight: 600;
}
</style>
