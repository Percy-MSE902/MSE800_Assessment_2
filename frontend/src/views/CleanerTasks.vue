<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { portalService } from '@/services'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const tasks = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const selectedStatus = ref<number | null>(null)

const cleanerId = computed(() => userStore.userInfo?.id)
const isCleaner = computed(() => ['staff', 'cleaner', 'employee'].includes(userStore.userInfo?.role))

const statusOptions = [
  { value: null, label: 'All Tasks' },
  { value: 0, label: 'Pending', type: 'warning' },
  { value: 1, label: 'Assigned', type: 'success' },
  { value: 2, label: 'In Progress', type: 'primary' },
  { value: 4, label: 'Completed', type: 'success' }
]

const loadData = async () => {
  if (!cleanerId.value || !isCleaner.value) return
  
  loading.value = true
  try {
    const res = await portalService.getCleanerTasks(cleanerId.value, selectedStatus.value, page.value, pageSize.value)
    tasks.value = res?.items || []
    total.value = res?.total || 0
  } catch (e: any) {
    console.error('Failed to load tasks:', e)
    ElMessage.error('Failed to load tasks')
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
    4: 'success'
  }
  return types[status] || 'info'
}

const filterByStatus = (status: number | null) => {
  selectedStatus.value = status
  page.value = 1
  loadData()
}

const getStatusCounts = computed(() => {
  const counts: Record<number, number> = { 0: 0, 1: 0, 2: 0, 4: 0 }
  tasks.value.forEach(task => {
    if (counts[task.status] !== undefined) {
      counts[task.status]++
    }
  })
  return counts
})

const pendingCount = computed(() => tasks.value.filter(t => t.status === 0).length)
const inProgressCount = computed(() => tasks.value.filter(t => t.status === 2).length)
const completedCount = computed(() => tasks.value.filter(t => t.status === 4).length)

onMounted(() => {
  if (isCleaner.value) {
    loadData()
  }
})
</script>

<template>
  <div class="cleaner-tasks">
    <div class="header">
      <h2>My Tasks</h2>
      <el-button type="primary" @click="loadData" :loading="loading">Refresh</el-button>
    </div>

    <div class="stats-cards" v-if="isCleaner">
      <el-card class="stat-card">
        <div class="stat-value">{{ pendingCount }}</div>
        <div class="stat-label">Pending</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-value">{{ inProgressCount }}</div>
        <div class="stat-label">In Progress</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-value">{{ completedCount }}</div>
        <div class="stat-label">Completed</div>
      </el-card>
    </div>

    <div class="status-tabs">
      <el-button 
        v-for="status in statusOptions" 
        :key="status.value"
        :type="selectedStatus === status.value ? 'primary' : 'default'"
        @click="filterByStatus(status.value)"
      >
        {{ status.label }}
        <el-badge v-if="status.value !== null" :value="getStatusCounts[status.value]" :max="99" />
      </el-button>
    </div>

    <el-table :data="tasks" v-loading="loading" style="width: 100%" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="order_no" label="Order No" width="180" />
      <el-table-column prop="service_type" label="Service" width="140" />
      <el-table-column prop="guest_name" label="Guest" width="100" />
      <el-table-column prop="guest_phone" label="Phone" width="130" />
      <el-table-column prop="property_type" label="Property" width="100" />
      <el-table-column prop="address" label="Address" min-width="150" />
      <el-table-column label="Bedroom" width="80">
        <template #default="{ row }">
          {{ row.bedroom }}
        </template>
      </el-table-column>
      <el-table-column label="Bathroom" width="80">
        <template #default="{ row }">
          {{ row.bathroom }}
        </template>
      </el-table-column>
      <el-table-column label="Budget" width="80">
        <template #default="{ row }">
          ${{ row.budget }}
        </template>
      </el-table-column>
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

    <el-empty v-if="!loading && tasks.length === 0 && isCleaner" description="No tasks found" />
    <el-empty v-if="!isCleaner" description="You don't have access to this page" />
  </div>
</template>

<style scoped>
.cleaner-tasks {
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
.status-tabs {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
