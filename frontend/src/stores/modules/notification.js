import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationApi } from '@/api'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])
  const unreadCount = ref(0)

  const unreadNotifications = computed(() => 
    notifications.value.filter(notification => !notification.read)
  )

  async function fetchNotifications(params) {
    try {
      const response = await notificationApi.list(params)
      notifications.value = response.items || response
      return response
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
      throw error
    }
  }

  async function fetchUnreadCount() {
    try {
      const response = await notificationApi.getUnreadCount()
      unreadCount.value = response.count || response
      return response
    } catch (error) {
      console.error('Failed to fetch unread count:', error)
      throw error
    }
  }

  async function markAsRead(id) {
    try {
      await notificationApi.markAsRead(id)
      const notification = notifications.value.find(n => n.id === id)
      if (notification) {
        notification.read = true
      }
      unreadCount.value = Math.max(0, unreadCount.value - 1)
      return true
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
      throw error
    }
  }

  async function markAllAsRead() {
    try {
      await notificationApi.markAllAsRead()
      notifications.value.forEach(notification => {
        notification.read = true
      })
      unreadCount.value = 0
      return true
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error)
      throw error
    }
  }

  async function deleteNotification(id) {
    try {
      await notificationApi.delete(id)
      const index = notifications.value.findIndex(n => n.id === id)
      if (index !== -1) {
        notifications.value.splice(index, 1)
        // 如果删除的通知是未读的，减少未读计数
        const notification = notifications.value.find(n => n.id === id)
        if (notification && !notification.read) {
          unreadCount.value = Math.max(0, unreadCount.value - 1)
        }
      }
      return true
    } catch (error) {
      console.error('Failed to delete notification:', error)
      throw error
    }
  }

  function addNotification(notification) {
    notifications.value.unshift(notification)
    if (!notification.read) {
      unreadCount.value += 1
    }
  }

  function clearNotifications() {
    notifications.value = []
    unreadCount.value = 0
  }

  return {
    notifications,
    unreadCount,
    unreadNotifications,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    addNotification,
    clearNotifications
  }
})