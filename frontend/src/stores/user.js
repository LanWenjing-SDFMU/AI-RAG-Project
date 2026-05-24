import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const workId = ref(localStorage.getItem('work_id') || '')
  const role = ref(localStorage.getItem('role') || '')

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => role.value === 'admin')

  function setLogin(t, w, r = 'doctor') {
    token.value = t
    workId.value = w
    role.value = r
    localStorage.setItem('token', t)
    localStorage.setItem('work_id', w)
    localStorage.setItem('role', r)
  }

  function logout() {
    token.value = ''
    workId.value = ''
    role.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('work_id')
    localStorage.removeItem('role')
  }

  return { token, workId, role, isLoggedIn, isAdmin, setLogin, logout }
})
