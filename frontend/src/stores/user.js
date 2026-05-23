import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const workId = ref(localStorage.getItem('work_id') || '')

  const isLoggedIn = computed(() => !!token.value)

  function setLogin(t, w) {
    token.value = t
    workId.value = w
    localStorage.setItem('token', t)
    localStorage.setItem('work_id', w)
  }

  function logout() {
    token.value = ''
    workId.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('work_id')
  }

  return { token, workId, isLoggedIn, setLogin, logout }
})
