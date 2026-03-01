import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, userApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    const formData = new URLSearchParams()
    formData.append('grant_type', 'password')
    formData.append('username', username)
    formData.append('password', password)

    const res = await authApi.login(formData)
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)
    
    // Fetch user info from backend
    try {
      const users = await userApi.list()
      const currentUser = users.find(u => u.username === username)
      if (currentUser) {
        userInfo.value = { 
          id: currentUser.id,
          username: currentUser.username, 
          role: currentUser.role 
        }
      } else {
        // Fallback: decode JWT to get username
        const payload = JSON.parse(atob(res.access_token.split('.')[1]))
        userInfo.value = { username: payload.sub, role: 'guest' }
      }
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    } catch (e) {
      console.error('Failed to fetch user info:', e)
      // Fallback: decode JWT
      const payload = JSON.parse(atob(res.access_token.split('.')[1]))
      userInfo.value = { username: payload.sub, role: 'guest' }
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    }
    
    return res
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    login,
    logout
  }
})
