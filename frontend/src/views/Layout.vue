<template>
  <el-container class="layout-container">
    <!-- 顶部横幅 -->
    <el-header class="top-banner">
      <div class="banner-content">
        <h1 class="banner-title">基层医生医疗辅助系统</h1>
        <p class="banner-subtitle">基于检索增强生成（RAG）技术 · 助力便捷精准医疗</p>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
        <div class="sidebar-header">
          <div class="user-info" v-if="userStore.workId">
            <div class="user-label">当前用户</div>
            <div class="user-name">{{ userStore.workId }}</div>
          </div>
        </div>

        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          router
        >
          <!-- ====== 医生 & 管理员 通用菜单 ====== -->
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/diagnosis-assist">
            <el-icon><Search /></el-icon>
            <span>鉴别诊断辅助</span>
          </el-menu-item>
          <el-menu-item index="/chat">
            <el-icon><ChatDotSquare /></el-icon>
            <span>智能临床问答</span>
          </el-menu-item>
          <el-menu-item index="/drug-safety">
            <el-icon><WarningFilled /></el-icon>
            <span>用药安全核查</span>
          </el-menu-item>
          <el-menu-item index="/diagnosis-records">
            <el-icon><Document /></el-icon>
            <span>患者诊断记录</span>
          </el-menu-item>

          <!-- ====== 管理员专属菜单 ====== -->
          <template v-if="userStore.isAdmin">
            <el-divider class="menu-divider" />
            <el-menu-item index="/knowledge-base">
              <el-icon><FolderOpened /></el-icon>
              <span>知识库管理</span>
            </el-menu-item>
            <el-menu-item index="/users">
              <el-icon><UserFilled /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="/logs">
              <el-icon><List /></el-icon>
              <span>操作日志</span>
            </el-menu-item>
          </template>
        </el-menu>

        <div class="sidebar-footer">
          <el-button text class="logout-btn" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span v-if="!isCollapse">退出登录</span>
          </el-button>
        </div>
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { logApi } from '@/api'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isCollapse = ref(false)

const activeMenu = computed(() => route.path)

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    // 记录退出日志
    try {
      await logApi.getList({ page: 1, page_size: 1 })
    } catch (_) {}
    userStore.logout()
    router.push('/login')
  } catch {
    // 取消退出
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.top-banner {
  height: auto !important;
  background: linear-gradient(135deg, #1a3a6b 0%, #2a5298 50%, #3a6ab8 100%);
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  z-index: 1000;
}

.banner-title {
  color: #fff;
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0 0 4px;
  letter-spacing: 2px;
}

.banner-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  margin: 0;
  letter-spacing: 1px;
}

.main-container {
  flex: 1;
  overflow: hidden;
}

.sidebar {
  background-color: #304156;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  overflow: hidden;
}

.sidebar-header {
  padding: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.user-info {
  background: rgba(64, 158, 255, 0.1);
  border-radius: 6px;
  padding: 8px 12px;
  border-left: 3px solid #409EFF;
}

.user-label {
  font-size: 11px;
  color: #97a8be;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.el-menu {
  border-right: none;
  flex: 1;
}

.menu-divider {
  margin: 4px 12px;
  border-color: rgba(255, 255, 255, 0.08);
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.logout-btn {
  width: 100%;
  color: #bfcbd9 !important;
  justify-content: center;
}

.logout-btn:hover {
  color: #fff !important;
  background-color: #263445 !important;
}

.main-content {
  background: #f0f2f5;
  padding: 0;
  overflow-y: auto;
}
</style>
