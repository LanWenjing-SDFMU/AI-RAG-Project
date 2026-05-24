import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页', roles: ['doctor', 'admin'] },
      },
      {
        path: 'knowledge-base',
        name: 'KnowledgeBase',
        component: () => import('@/views/KnowledgeBase.vue'),
        meta: { title: '知识库管理', roles: ['admin'] },
      },
      {
        path: 'diagnosis-assist',
        name: 'DiagnosisAssist',
        component: () => import('@/views/DiagnosisAssist.vue'),
        meta: { title: '鉴别诊断辅助', roles: ['doctor', 'admin'] },
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('@/views/Chat.vue'),
        meta: { title: '智能临床问答', roles: ['doctor', 'admin'] },
      },
      {
        path: 'drug-safety',
        name: 'DrugSafety',
        component: () => import('@/views/DrugSafety.vue'),
        meta: { title: '用药安全核查', roles: ['doctor', 'admin'] },
      },
      {
        path: 'diagnosis-records',
        name: 'DiagnosisRecords',
        component: () => import('@/views/DiagnosisRecords.vue'),
        meta: { title: '患者诊断记录', roles: ['doctor', 'admin'] },
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/UserManagement.vue'),
        meta: { title: '用户管理', roles: ['admin'] },
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('@/views/Logs.vue'),
        meta: { title: '操作日志', roles: ['admin'] },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role') || ''

  // 未登录且需要认证 → 跳转登录
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  // 已登录访问登录页 → 跳转首页
  if (to.path === '/login' && token) {
    next('/dashboard')
    return
  }

  // 角色检查：如果路由指定了 roles，检查当前用户角色是否在允许列表中
  if (to.meta.roles && token) {
    if (!to.meta.roles.includes(role)) {
      ElMessage.error('无权限访问该页面')
      next('/dashboard')
      return
    }
  }

  next()
})

export default router
