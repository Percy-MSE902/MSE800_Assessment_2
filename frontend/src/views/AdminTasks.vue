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

const filters = ref({
  order_no: '',
  cleaner_name: '',
  start_date: '',
  end_date: '',
  status: null as number | null
})

const dateRange = ref<[string, string] | null>(null)

const isAdmin = computed(() => ['admin', 'manager'].includes(userStore.userInfo?.role))

const loadData = async () => {
  if (!isAdmin.value) return
  
  loading.value = true
  try {
    const filterParams: any = {}
    if (filters.value.order_no) filterParams.order_no = filters.value.order_no
    if (filters.value.cleaner_name) filterParams.cleaner_name = filters.value.cleaner_name
    if (filters.value.start_date) filterParams.start_date = filters.value.start_date
    if (filters.value.end_date) filterParams.end_date = filters.value.end_date
    if (filters.value.status !== null) filterParams.status = filters.value.status
    
    const res = await portalService.getAdminTasks(page.value, pageSize.value, filterParams)
    tasks.value = res?.items || []
    total.value = res?.total || 0
    
    if (filters.value.start_date && filters.value.end_date) {
      dateRange.value = [filters.value.start_date, filters.value.end_date]
    }
    
    filters.value.status = filterParams.status ?? filters.value.status
  } catch (e: any) {
    console.error('Failed to load tasks:', e)
    ElMessage.error('Failed to load tasks')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  loadData()
}

const handleReset = () => {
  filters.value = {
    order_no: '',
    cleaner_name: '',
    start_date: '',
    end_date: '',
    status: null
  }
  dateRange.value = null
  page.value = 1
  loadData()
}

const handleDateRangeChange = (val: [string, string] | null) => {
  if (val) {
    filters.value.start_date = val[0]
    filters.value.end_date = val[1]
  } else {
    filters.value.start_date = ''
    filters.value.end_date = ''
  }
  page.value = 1
  loadData()
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

const selectedTask = ref<any>(null)
const dialogVisible = ref(false)

const showDetails = (row: any) => {
  selectedTask.value = row
  dialogVisible.value = true
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="tasks-management">
    <div class="header">
      <h2>Task Management</h2>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="Order No">
          <el-input v-model="filters.order_no" placeholder="Search by order no" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="Cleaner Name">
          <el-input v-model="filters.cleaner_name" placeholder="Search by cleaner" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="filters.status" placeholder="All Status" clearable style="width: 160px">
            <el-option :value="0" label="Pending" />
            <el-option :value="1" label="Assigned" />
            <el-option :value="2" label="In Progress" />
            <el-option :value="3" label="Pending Review" />
            <el-option :value="4" label="Completed" />
            <el-option :value="5" label="Cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="Date Range">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start"
            end-placeholder="End"
            value-format="YYYY-MM-DD"
            @change="handleDateRangeChange"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleReset">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="tasks" v-loading="loading" style="width: 100%" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="order_no" label="Order No" width="160" />
      <el-table-column prop="cleaner_name" label="Cleaner" width="120" />
      <el-table-column prop="service_type" label="Service Type" width="140" />
      <el-table-column prop="guest_name" label="Guest Name" width="120" />
      <el-table-column prop="guest_phone" label="Phone" width="130" />
      <el-table-column prop="property_type" label="Property Type" width="100" />
      <el-table-column prop="address" label="Address" min-width="150" />
      <el-table-column label="Status" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ row.status_text }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="Created" width="140" />
      <el-table-column prop="complete_time" label="Completed" width="140" />
      <el-table-column label="Action" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="showDetails(row)">Details</el-button>
        </template>
      </el-table-column>
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

    <el-dialog v-model="dialogVisible" title="Order Details" width="700px">
      <el-descriptions :column="2" border v-if="selectedTask">
        <el-descriptions-item label="Order No">{{ selectedTask.order_no }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedTask.status)">{{ selectedTask.status_text }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Guest Name">{{ selectedTask.guest_name }}</el-descriptions-item>
        <el-descriptions-item label="Phone">{{ selectedTask.guest_phone }}</el-descriptions-item>
        <el-descriptions-item label="Email">{{ selectedTask.guest_email }}</el-descriptions-item>
        <el-descriptions-item label="Property Type">{{ selectedTask.property_type }}</el-descriptions-item>
        <el-descriptions-item label="Address" :span="2">{{ selectedTask.address }}</el-descriptions-item>
        <el-descriptions-item label="Bedroom">{{ selectedTask.bedroom }}</el-descriptions-item>
        <el-descriptions-item label="Bathroom">{{ selectedTask.bathroom }}</el-descriptions-item>
        <el-descriptions-item label="Living Room">{{ selectedTask.living_room }}</el-descriptions-item>
        <el-descriptions-item label="Kitchen">{{ selectedTask.kitchen }}</el-descriptions-item>
        <el-descriptions-item label="Lawn">{{ selectedTask.lawn }}</el-descriptions-item>
        <el-descriptions-item label="Car Space">{{ selectedTask.car_space }}</el-descriptions-item>
        <el-descriptions-item label="Square Footage">{{ selectedTask.square_footage }}</el-descriptions-item>
        <el-descriptions-item label="Service Type">{{ selectedTask.service_type }}</el-descriptions-item>
        <el-descriptions-item label="Preferred Time">{{ selectedTask.preferred_time }}</el-descriptions-item>
        <el-descriptions-item label="Budget">${{ selectedTask.budget }}</el-descriptions-item>
        <el-descriptions-item label="Cleaner">{{ selectedTask.cleaner_name }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedTask.description }}</el-descriptions-item>
        <el-descriptions-item label="Remarks" :span="2">{{ selectedTask.remarks }}</el-descriptions-item>
        <el-descriptions-item label="Guest Feedback" :span="2">{{ selectedTask.guest_feedback }}</el-descriptions-item>
        <el-descriptions-item label="Rating">{{ selectedTask.rating ? selectedTask.rating + '/5' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="Created">{{ selectedTask.create_time }}</el-descriptions-item>
        <el-descriptions-item label="Completed">{{ selectedTask.complete_time }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<style scoped>
.tasks-management {
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
.filter-card {
  margin-bottom: 20px;
}
.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
