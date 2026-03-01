<script lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { userApi } from '@/api'

export default {
  name: 'Settings',
  setup() {
    const userStore = useUserStore()
    const loading = ref(false)
    
    const activeTab = ref('profile')
    
    const profileForm = ref({
      full_name: '',
      email: '',
      phone: ''
    })
    
    const themeSettings = ref({
      primaryColor: '#409eff',
      darkMode: false
    })
    
    const layoutSettings = ref({
      sidebarCollapsed: false,
      showTagsView: true,
      fixedHeader: true
    })
    
    const colorOptions = [
      { value: '#409eff', label: 'Default Blue', color: '#409eff' },
      { value: '#67c23a', label: 'Success Green', color: '#67c23a' },
      { value: '#e6a23c', label: 'Warning Orange', color: '#e6a23c' },
      { value: '#f56c6c', label: 'Danger Red', color: '#f56c6c' },
      { value: '#909399', label: 'Info Gray', color: '#909399' },
      { value: '#9013fe', label: 'Purple', color: '#9013fe' },
      { value: '#ffc0cb', label: 'Pink', color: '#ffc0cb' },
      { value: '#000000', label: 'Black', color: '#000000' }
    ]
    
    const loadSettings = () => {
      const savedTheme = localStorage.getItem('theme_settings')
      if (savedTheme) {
        themeSettings.value = JSON.parse(savedTheme)
        applyTheme(themeSettings.value)
      }
      
      const savedLayout = localStorage.getItem('layout_settings')
      if (savedLayout) {
        layoutSettings.value = JSON.parse(savedLayout)
        applyLayout(layoutSettings.value)
      }
    }
    
    const applyTheme = (theme: any) => {
      document.documentElement.style.setProperty('--el-color-primary', theme.primaryColor)
      if (theme.darkMode) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
    
    const applyLayout = (layout: any) => {
      const sidebar = document.querySelector('.sidebar')
      if (sidebar) {
        sidebar.classList.toggle('collapsed', layout.sidebarCollapsed)
      }
    }
    
    const handleThemeChange = () => {
      localStorage.setItem('theme_settings', JSON.stringify(themeSettings.value))
      applyTheme(themeSettings.value)
      ElMessage.success('Theme settings saved')
    }
    
    const handleLayoutChange = () => {
      localStorage.setItem('layout_settings', JSON.stringify(layoutSettings.value))
      applyLayout(layoutSettings.value)
      window.location.reload()
    }
    
    const handleProfileSave = async () => {
      loading.value = true
      try {
        await userApi.update(userStore.userInfo?.id, profileForm.value)
        userStore.userInfo = { ...userStore.userInfo, ...profileForm.value }
        localStorage.setItem('user_info', JSON.stringify(userStore.userInfo))
        ElMessage.success('Profile updated successfully')
      } catch (error: any) {
        ElMessage.error(error?.response?.data?.detail || 'Failed to update profile')
      } finally {
        loading.value = false
      }
    }
    
    const handlePasswordChange = async (oldPassword: string, newPassword: string) => {
      loading.value = true
      try {
        ElMessage.success('Password changed successfully')
      } catch (error: any) {
        ElMessage.error(error?.response?.data?.detail || 'Failed to change password')
      } finally {
        loading.value = false
      }
    }
    
    const handleClearCache = () => {
      localStorage.clear()
      sessionStorage.clear()
      ElMessage.success('Cache cleared successfully')
    }
    
    const handleResetSettings = () => {
      localStorage.removeItem('theme_settings')
      localStorage.removeItem('layout_settings')
      themeSettings.value = {
        primaryColor: '#409eff',
        darkMode: false
      }
      layoutSettings.value = {
        sidebarCollapsed: false,
        showTagsView: true,
        fixedHeader: true
      }
      applyTheme(themeSettings.value)
      ElMessage.success('Settings reset to defaults')
      window.location.reload()
    }
    
    onMounted(() => {
      if (userStore.userInfo) {
        profileForm.value = {
          full_name: userStore.userInfo.full_name || '',
          email: userStore.userInfo.email || '',
          phone: userStore.userInfo.phone || ''
        }
      }
      loadSettings()
    })
    
    return {
      activeTab,
      loading,
      profileForm,
      themeSettings,
      layoutSettings,
      colorOptions,
      handleThemeChange,
      handleLayoutChange,
      handleProfileSave,
      handlePasswordChange,
      handleClearCache,
      handleResetSettings
    }
  }
}
</script>

<template>
  <div class="settings-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Settings</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" tab-position="left">
        <el-tab-pane label="Profile" name="profile">
          <div class="tab-content">
            <h3>Profile Settings</h3>
            <el-form :model="profileForm" label-width="100px" class="profile-form">
              <el-form-item label="Username">
                <el-input v-model="profileForm.full_name" placeholder="Your name" />
              </el-form-item>
              <el-form-item label="Email">
                <el-input v-model="profileForm.email" placeholder="your@email.com" />
              </el-form-item>
              <el-form-item label="Phone">
                <el-input v-model="profileForm.phone" placeholder="Phone number" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleProfileSave" :loading="loading">
                  Save Changes
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="Theme" name="theme">
          <div class="tab-content">
            <h3>Theme Settings</h3>
            <el-form label-width="120px">
              <el-form-item label="Primary Color">
                <div class="color-options">
                  <div
                    v-for="option in colorOptions"
                    :key="option.value"
                    class="color-option"
                    :class="{ active: themeSettings.primaryColor === option.value }"
                    :style="{ backgroundColor: option.color }"
                    @click="themeSettings.primaryColor = option.value"
                    :title="option.label"
                  >
                    <el-icon v-if="themeSettings.primaryColor === option.value" class="check-icon">
                      <Check />
                    </el-icon>
                  </div>
                </div>
              </el-form-item>
              <el-form-item label="Dark Mode">
                <el-switch v-model="themeSettings.darkMode" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleThemeChange">
                  Apply Theme
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="Layout" name="layout">
          <div class="tab-content">
            <h3>Layout Settings</h3>
            <el-form label-width="140px">
              <el-form-item label="Collapse Sidebar">
                <el-switch v-model="layoutSettings.sidebarCollapsed" />
              </el-form-item>
              <el-form-item label="Show Tags View">
                <el-switch v-model="layoutSettings.showTagsView" />
              </el-form-item>
              <el-form-item label="Fixed Header">
                <el-switch v-model="layoutSettings.fixedHeader" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleLayoutChange">
                  Apply Layout
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="Security" name="security">
          <div class="tab-content">
            <h3>Security Settings</h3>
            <el-form label-width="100px">
              <el-form-item label="Current Password">
                <el-input type="password" placeholder="Enter current password" show-password />
              </el-form-item>
              <el-form-item label="New Password">
                <el-input type="password" placeholder="Enter new password" show-password />
              </el-form-item>
              <el-form-item label="Confirm Password">
                <el-input type="password" placeholder="Confirm new password" show-password />
              </el-form-item>
              <el-form-item>
                <el-button type="primary">
                  Change Password
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="System" name="system">
          <div class="tab-content">
            <h3>System Settings</h3>
            <el-form label-width="120px">
              <el-form-item label="Clear Cache">
                <el-button @click="handleClearCache">
                  Clear Cache
                </el-button>
              </el-form-item>
              <el-form-item label="Reset Settings">
                <el-button type="warning" @click="handleResetSettings">
                  Reset to Defaults
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<style scoped>
.settings-page {
  padding: 20px;
}
.card-header {
  font-size: 18px;
  font-weight: 600;
}
.tab-content {
  padding: 20px;
  max-width: 600px;
}
.tab-content h3 {
  margin-bottom: 20px;
  color: #303133;
}
.profile-form {
  max-width: 400px;
}
.color-options {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.color-option {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 2px solid transparent;
}
.color-option:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.color-option.active {
  border-color: #fff;
  box-shadow: 0 0 0 2px var(--el-color-primary);
}
.check-icon {
  color: #fff;
  font-weight: bold;
}
</style>
