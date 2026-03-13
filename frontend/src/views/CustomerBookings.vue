<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { portalService } from '@/services'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const bookings = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const userId = computed(() => userStore.userInfo?.id)
const isGuest = computed(() => userStore.userInfo?.role === 'guest' || !userStore.userInfo?.role)

const loadData = async () => {
  if (!userId.value) return
  
  loading.value = true
  try {
    const res = await portalService.getCustomerBookings(userId.value, page.value, pageSize.value)
    bookings.value = res?.items || []
    total.value = res?.total || 0
  } catch (e: any) {
    console.error('Failed to load bookings:', e)
    ElMessage.error('Failed to load bookings')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (newPage: number) => {
  page.value = newPage
  loadData()
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  page.value = 1
  loadData()
}

const getStatusType = (status: number) => {
  const types: Record<number, string> = { 
    0: 'warning', 
    1: 'success', 
    2: 'primary', 
    3: 'info',
    4: 'success',
    5: 'danger'
  }
  return types[status] || 'info'
}

const pendingCount = computed(() => bookings.value.filter(b => b.status === 0).length)
const completedCount = computed(() => bookings.value.filter(b => b.status === 4).length)

onMounted(() => {
  if (isGuest.value && userId.value) {
    loadData()
  }
})
</script>

<template>
  <div class="customer-bookings">
    <div class="header">
      <h2>My Bookings</h2>
      <el-button type="primary" @click="loadData" :loading="loading">Refresh</el-button>
    </div>

    <div class="stats-cards" v-if="isGuest">
      <el-card class="stat-card">
        <div class="stat-value">{{ pendingCount }}</div>
        <div class="stat-label">Pending</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-value">{{ completedCount }}</div>
        <div class="stat-label">Completed</div>
      </el-card>
    </div>

    <el-table :data="bookings" v-loading="loading" style="width: 100%" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="order_no" label="Order No" width="180" />
      <el-table-column prop="service_type" label="Service Type" width="140" />
      <el-table-column prop="room_no" label="Room" width="80" />
      <el-table-column prop="assigned_staff" label="Assigned Staff" width="130" />
      <el-table-column label="Status" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ row.status_text }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="Created" width="140" />
      <el-table-column prop="complete_time" label="Completed" width="140" />
    </el-table>

    <el-pagination
      class="pagination"
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 50, 100]"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
    />

    <el-empty v-if="!loading && bookings.length === 0 && isGuest" description="No bookings found" />
    <el-empty v-if="!isGuest" description="You don't have access to this page" />
  </div>
</template>

<style scoped>
.customer-bookings {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header h2 {
  margin: 0;
}
.stats-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}
.stat-card {
  flex: 1;
  text-align: center;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}
.stat-label {
  color: #606266;
  margin-top: 5px;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
