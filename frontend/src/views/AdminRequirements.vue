<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { portalService } from '@/services'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const requirements = ref<any[]>([])
const cleaners = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const filters = ref({
  guest_name: '',
  guest_phone: '',
  property_type: '',
  service_type: '',
  start_date: '',
  end_date: ''
})

const dateRange = ref<[string, string] | null>(null)

const showAssignDialog = ref(false)
const selectedRequirement = ref<any>(null)
const selectedCleanerId = ref<any>(null)
const assignLoading = ref(false)

const isAdmin = computed(() => ['admin', 'manager'].includes(userStore.userInfo?.role))

const statusOptions = [
  { value: 0, label: 'Pending', type: 'warning' },
  { value: 1, label: 'Assigned', type: 'success' },
  { value: 2, label: 'In Progress', type: 'primary' },
  { value: 3, label: 'Completed', type: 'info' }
]

const propertyTypes = ['House', 'Apartment', 'Villa', 'Condo', 'Townhouse', 'Studio']

const loadData = async () => {
  if (!isAdmin.value) return
  
  loading.value = true
  try {
    const filterParams: any = {}
    if (filters.value.guest_name) filterParams.guest_name = filters.value.guest_name
    if (filters.value.guest_phone) filterParams.guest_phone = filters.value.guest_phone
    if (filters.value.property_type) filterParams.property_type = filters.value.property_type
    if (filters.value.service_type) filterParams.service_type = filters.value.service_type
    if (filters.value.start_date) filterParams.start_date = filters.value.start_date
    if (filters.value.end_date) filterParams.end_date = filters.value.end_date
    
    const [reqRes, cleanerRes] = await Promise.all([
      portalService.getAdminRequirements(null, page.value, pageSize.value, filterParams),
      portalService.getAdminCleaners()
    ])
    requirements.value = reqRes?.items || []
    total.value = reqRes?.total || 0
    cleaners.value = cleanerRes || []
  } catch (e: any) {
    console.error('Failed to load data:', e)
    ElMessage.error('Failed to load data')
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
    guest_name: '',
    guest_phone: '',
    property_type: '',
    service_type: '',
    start_date: '',
    end_date: ''
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
  const types: Record<number, string> = { 0: 'warning', 1: 'success', 2: 'primary', 3: 'info' }
  return types[status] || 'info'
}

const getStatusLabel = (status: number) => {
  const labels: Record<number, string> = { 0: 'Pending', 1: 'Assigned', 2: 'In Progress', 3: 'Completed' }
  return labels[status] || 'Unknown'
}

const openAssignDialog = (req: any) => {
  selectedRequirement.value = req
  selectedCleanerId.value = req.assigned_cleaner_id || null
  showAssignDialog.value = true
}

const confirmAssign = async () => {
  if (!selectedRequirement.value || !selectedCleanerId.value) {
    ElMessage.warning('Please select a cleaner')
    return
  }
  
  assignLoading.value = true
  try {
    await portalService.assignRequirementToCleaner(selectedRequirement.value.id, selectedCleanerId.value)
    ElMessage.success('Cleaner assigned successfully')
    showAssignDialog.value = false
    loadData()
  } catch (e: any) {
    console.error('Failed to assign:', e)
    ElMessage.error(e?.response?.data?.detail || 'Failed to assign cleaner')
  } finally {
    assignLoading.value = false
  }
}

const handleHide = async (req: any) => {
  try {
    await ElMessageBox.confirm(`Are you sure you want to hide this requirement?`, 'Confirm', {
      confirmButtonText: 'Yes',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })
    
    await portalService.hideRequirement(req.id)
    ElMessage.success('Requirement hidden successfully')
    loadData()
  } catch (e: any) {
    if (e !== 'cancel') {
      console.error('Failed to hide:', e)
      ElMessage.error('Failed to hide requirement')
    }
  }
}

const handleDelete = async (req: any) => {
  try {
    await ElMessageBox.confirm(`Are you sure you want to permanently delete this requirement? This action cannot be undone.`, 'Confirm Delete', {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })
    
    await portalService.deleteRequirement(req.id)
    ElMessage.success('Requirement deleted successfully')
    loadData()
  } catch (e: any) {
    if (e !== 'cancel') {
      console.error('Failed to delete:', e)
      ElMessage.error('Failed to delete requirement')
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="requirements-management">
    <div class="header">
      <h2>Requirements Management</h2>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="Guest Name">
          <el-input v-model="filters.guest_name" placeholder="Search by name" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="Phone">
          <el-input v-model="filters.guest_phone" placeholder="Search by phone" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="Property Type">
          <el-select v-model="filters.property_type" placeholder="Select" clearable style="width: 140px">
            <el-option v-for="p in propertyTypes" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="Service Type">
          <el-input v-model="filters.service_type" placeholder="Search by service" clearable @keyup.enter="handleSearch" />
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

    <el-table :data="requirements" v-loading="loading" style="width: 100%" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="guest_name" label="Guest Name" width="120" />
      <el-table-column prop="guest_phone" label="Phone" width="130" />
      <el-table-column prop="property_type" label="Property Type" width="100" />
      <el-table-column label="Details" min-width="150">
        <template #default="{ row }">
          <div>{{ row.bedroom }}BR/{{ row.bathroom }}BA</div>
        </template>
      </el-table-column>
      <el-table-column prop="service_type_name" label="Service" width="120" />
      <el-table-column prop="budget" label="Budget" width="80">
        <template #default="{ row }">
          ${{ row.budget }}
        </template>
      </el-table-column>
      <el-table-column prop="preferred_time" label="Preferred Time" width="120" />
      <el-table-column label="Status" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Assigned" width="120">
        <template #default="{ row }">
          {{ row.accepted_cleaner_name || 'Not Assigned' }}
        </template>
      </el-table-column>
      <el-table-column label="Applications" width="90">
        <template #default="{ row }">
          {{ row.applications_count }}
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="Created" width="140" />
      <el-table-column label="Actions" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="openAssignDialog(row)">Assign</el-button>
          <el-button size="small" type="warning" @click="handleHide(row)">Hide</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">Delete</el-button>
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

    <el-dialog v-model="showAssignDialog" title="Assign Cleaner" width="400px">
      <div v-if="selectedRequirement">
        <p><strong>Requirement #{{ selectedRequirement.id }}</strong></p>
        <p>{{ selectedRequirement.guest_name }} - {{ selectedRequirement.property_type }}</p>
        <p>Service: {{ selectedRequirement.service_type_name }} - ${{ selectedRequirement.budget }}</p>
      </div>
      
      <el-form label-width="100px" style="margin-top: 20px">
        <el-form-item label="Select Cleaner">
          <el-select v-model="selectedCleanerId" placeholder="Choose cleaner" style="width: 100%">
            <el-option
              v-for="cleaner in cleaners"
              :key="cleaner.id"
              :label="cleaner.full_name || cleaner.username"
              :value="cleaner.id"
            >
              <span>{{ cleaner.full_name || cleaner.username }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                Pending: {{ cleaner.pending_tasks }} | Completed: {{ cleaner.completed_tasks }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAssignDialog = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAssign" :loading="assignLoading">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.requirements-management {
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
