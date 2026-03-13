import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Portal',
    component: () => import('@/views/Portal.vue'),
    meta: { title: 'CleanPro - Professional Cleaning Services' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: 'Login' }
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: 'Home', requiresAuth: true }
  },
  {
    path: '/my-tasks',
    name: 'MyTasks',
    component: () => import('@/views/MyTasks.vue'),
    meta: { title: 'My Tasks', requiresAuth: true }
  },
  {
    path: '/cleaner-tasks',
    name: 'CleanerTasks',
    component: () => import('@/views/CleanerTasks.vue'),
    meta: { title: 'My Tasks', requiresAuth: true }
  },
  {
    path: '/my-orders',
    name: 'MyOrders',
    component: () => import('@/views/MyOrders.vue'),
    meta: { title: 'My Orders', requiresAuth: true }
  },
  {
    path: '/my-requirements',
    name: 'CustomerRequirements',
    component: () => import('@/views/CustomerRequirements.vue'),
    meta: { title: 'My Requirements', requiresAuth: true }
  },
  {
    path: '/my-bookings',
    name: 'CustomerBookings',
    component: () => import('@/views/CustomerBookings.vue'),
    meta: { title: 'My Bookings', requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'TaskManagement',
    component: () => import('@/views/TaskManagement.vue'),
    meta: { title: 'Task Management', requiresAuth: true }
  },
  {
    path: '/admin-requirements',
    name: 'AdminRequirements',
    component: () => import('@/views/AdminRequirements.vue'),
    meta: { title: 'Requirements Management', requiresAuth: true }
  },
  {
    path: '/admin-tasks',
    name: 'AdminTasks',
    component: () => import('@/views/AdminTasks.vue'),
    meta: { title: 'Task Management', requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/Users.vue'),
    meta: { title: 'User Management', requiresAuth: true }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('@/views/Orders.vue'),
    meta: { title: 'Order Management', requiresAuth: true }
  },
  {
    path: '/rooms',
    name: 'Rooms',
    component: () => import('@/views/Rooms.vue'),
    meta: { title: 'Room Management', requiresAuth: true }
  },
  {
    path: '/staff',
    name: 'Staff',
    component: () => import('@/views/Staff.vue'),
    meta: { title: 'Staff Management', requiresAuth: true }
  },
  {
    path: '/inventory',
    name: 'Inventory',
    component: () => import('@/views/Inventory.vue'),
    meta: { title: 'Inventory Management', requiresAuth: true }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/Reports.vue'),
    meta: { title: 'Reports', requiresAuth: true }
  },
  {
    path: '/wallet',
    name: 'Wallet',
    component: () => import('@/views/Wallet.vue'),
    meta: { title: 'My Wallet', requiresAuth: true }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('@/views/Notifications.vue'),
    meta: { title: 'Notifications', requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: 'Settings', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path === '/login' && token) {
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    if (userInfo.role === 'admin' || userInfo.role === 'manager') {
      next('/home')
    } else if (['staff', 'cleaner', 'employee'].includes(userInfo.role)) {
      next('/cleaner-tasks')
    } else if (userInfo.role === 'guest') {
      next('/my-requirements')
    } else {
      next('/')
    }
  } else if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
