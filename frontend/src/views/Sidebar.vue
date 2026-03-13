<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const userInfo = computed(() => userStore.userInfo)

const isAdmin = computed(() => ['admin', 'manager'].includes(userInfo.value?.role))
const isCleaner = computed(() => ['staff', 'cleaner', 'employee'].includes(userInfo.value?.role))
const isGuest = computed(() => userInfo.value?.role === 'guest' || !userInfo.value?.role)

const adminMenuItems = ref([
  { path: '/home', title: 'Dashboard', icon: 'HomeFilled' },
  { path: '/admin-requirements', title: 'Requirements', icon: 'Document' },
  { path: '/admin-tasks', title: 'Task Management', icon: 'List' },
  { path: '/orders', title: 'Orders', icon: 'Document' },
  { path: '/rooms', title: 'Rooms', icon: 'House' },
  { path: '/staff', title: 'Staff', icon: 'User' },
  { path: '/users', title: 'Users', icon: 'UserFilled' },
  { path: '/inventory', title: 'Inventory', icon: 'Box' },
  { path: '/wallet', title: 'Wallet', icon: 'Wallet' },
  { path: '/reports', title: 'Reports', icon: 'DataAnalysis' },
  { path: '/notifications', title: 'Notifications', icon: 'Bell' },
  { path: '/settings', title: 'Settings', icon: 'Setting' }
])

const cleanerMenuItems = ref([
  { path: '/cleaner-tasks', title: 'My Tasks', icon: 'List' },
  { path: '/orders', title: 'Orders', icon: 'Document' },
  { path: '/wallet', title: 'Wallet', icon: 'Wallet' },
  { path: '/notifications', title: 'Notifications', icon: 'Bell' },
  { path: '/settings', title: 'Settings', icon: 'Setting' }
])

const guestMenuItems = ref([
  { path: '/my-requirements', title: 'My Requirements', icon: 'Document' },
  { path: '/my-bookings', title: 'My Bookings', icon: 'Calendar' },
  { path: '/my-orders', title: 'My Orders', icon: 'Document' },
  { path: '/wallet', title: 'Wallet', icon: 'Wallet' },
  { path: '/notifications', title: 'Notifications', icon: 'Bell' },
  { path: '/settings', title: 'Settings', icon: 'Setting' }
])

const menuItems = computed(() => {
  if (isAdmin.value) return adminMenuItems.value
  if (isCleaner.value) return cleanerMenuItems.value
  return guestMenuItems.value
})

const go = (path) => {
  router.push(path)
}

const isActive = (path) => {
  return route.path === path
}
</script>

<template>
  <aside class="sidebar">
    <h2 class="logo">Admin</h2>
    <ul>
      <li 
        v-for="item in menuItems" 
        :key="item.path"
        :class="{ active: isActive(item.path) }"
      >
        <a @click.prevent="go(item.path)">{{ item.title }}</a>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 220px;
  background: #1e293b;
  color: white;
  padding: 20px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
}
.sidebar ul {
  list-style: none;
  padding: 0;
}
.sidebar li {
  margin: 8px 0;
}
.sidebar li a {
  display: block;
  padding: 12px 16px;
  color: #94a3b8;
  text-decoration: none;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}
.sidebar li a:hover {
  background: #334155;
  color: white;
}
.sidebar li.active a {
  background: #3b82f6;
  color: white;
  font-weight: bold;
}
.sidebar .logo {
  margin: 0 0 24px 0;
  padding: 0 16px;
  font-size: 20px;
}
</style>
