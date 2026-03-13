<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { portalService } from '@/services'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const requirements = ref<any[]>([])
const cleaners = ref<any[]>([])
const activeTab = ref('requirements')

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

const loadData = async () => {
  if (!isAdmin.value) return
  
  loading.value = true
  try {
    const [reqRes, cleanerRes] = await Promise.all([
      portalService.getAdminRequirements(null, 100),
      portalService.getAdminCleaners()
    ])
    requirements.value = reqRes || []
    cleaners.value = cleanerRes || []
  } catch (e: any) {
    console.error('Failed to load data:', e)
    ElMessage.error('Failed to load data')
  } finally {
    loading.value = false
  }
}

const getStatusType = (status: number) => {
  const types = ['warning', 'success', 'primary', 'info']
  return types[status] || 'info'
}

const getStatusLabel = (status: number) => {
  const labels = ['Pending', 'Assigned', 'In Progress', 'Completed']
  return labels[status] || 'Unknown'
}

const openAssignDialog = (req: any) => {
  selectedRequirement.value = req
  selectedCleanerId.value = req.accepted_cleaner_id || null
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

const viewApplications = (req: any) => {
  ElMessage.info(`This requirement has ${req.applications_count} applications`)
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="task-management">
    <div class="page-header">
      <h2>Task Management</h2>
      <p class="subtitle">Manage customer requirements and assign cleaners</p>
    </div>
    
    <el-tabs v-model="activeTab" class="management-tabs">
      <el-tab-pane label="Customer Requirements" name="requirements">
        <el-card class="data-card">
          <el-table :data="requirements" v-loading="loading" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column label="Property" width="120">
              <template #default="{ row }">
                <el-tag>{{ row.property_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Details" min-width="180">
              <template #default="{ row }">
                <div class="detail-cell">
                  <span>{{ row.bedroom }} Bed / {{ row.bathroom }} Bath</span>
                  <span v-if="row.square_footage">{{ row.square_footage }} sqft</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="budget" label="Budget" width="100">
              <template #default="{ row }">
                <span class="price">${{ row.budget }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="preferred_time" label="Preferred Time" width="130" />
            <el-table-column label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="applications_count" label="Applications" width="100">
              <template #default="{ row }">
                <el-badge :value="row.applications_count" :max="99" />
              </template>
            </el-table-column>
            <el-table-column label="Assigned To" width="140">
              <template #default="{ row }">
                <span v-if="row.accepted_cleaner_name">{{ row.accepted_cleaner_name }}</span>
                <span v-else class="not-assigned">Not assigned</span>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="180" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="openAssignDialog(row)">
                  Assign Cleaner
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="Cleaner Workloads" name="cleaners">
        <el-card class="data-card">
          <el-table :data="cleaners" v-loading="loading" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column label="Cleaner" min-width="150">
              <template #default="{ row }">
                <div class="cleaner-info">
                  <span class="name">{{ row.full_name }}</span>
                  <span class="username">@{{ row.username }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="Rating" width="150">
              <template #default="{ row }">
                <el-rate v-model="row.star_level" disabled :max="5" />
                <span class="rating-value">{{ row.total_rating }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="total_orders" label="Total Orders" width="100" />
            <el-table-column prop="pending_tasks" label="Pending" width="80">
              <template #default="{ row }">
                <el-tag type="warning">{{ row.pending_tasks }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="completed_tasks" label="Completed" width="100">
              <template #default="{ row }">
                <el-tag type="success">{{ row.completed_tasks }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Workload" width="150">
              <template #default="{ row }">
                <el-progress 
                  :percentage="row.total_orders > 0 ? Math.round(row.completed_tasks / row.total_orders * 100) : 0" 
                  :status="row.pending_tasks > 5 ? 'exception' : ''"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- Assign Dialog -->
    <el-dialog 
      v-model="showAssignDialog" 
      title="Assign Cleaner to Requirement" 
      width="500px"
      destroy-on-close
    >
      <div v-if="selectedRequirement" class="assign-dialog-content">
        <div class="requirement-info">
          <h4>Requirement #{{ selectedRequirement.id }}</h4>
          <p>{{ selectedRequirement.property_type }} - Budget: ${{ selectedRequirement.budget }}</p>
          <p>{{ selectedRequirement.bedroom }} Bed / {{ selectedRequirement.bathroom }} Bath</p>
        </div>
        
        <el-form label-width="120px">
          <el-form-item label="Select Cleaner" required>
            <el-select 
              v-model="selectedCleanerId" 
              placeholder="Choose a cleaner"
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="cleaner in cleaners"
                :key="cleaner.id"
                :label="`${cleaner.full_name} (${cleaner.pending_tasks} pending, ${cleaner.completed_tasks} completed)`"
                :value="cleaner.id"
              >
                <div class="cleaner-option">
                  <span>{{ cleaner.full_name }}</span>
                  <span class="cleaner-stats">
                    Pending: {{ cleaner.pending_tasks }} | Completed: {{ cleaner.completed_tasks }}
                  </span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showAssignDialog = false">Cancel</el-button>
        <el-button type="primary" :loading="assignLoading" @click="confirmAssign">
          Confirm Assignment
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.task-management {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
}

.management-tabs {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.data-card {
  margin-top: 16px;
}

.detail-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}

.price {
  color: #ff6b6b;
  font-weight: bold;
}

.not-assigned {
  color: #909399;
  font-style: italic;
}

.cleaner-info {
  display: flex;
  flex-direction: column;
}

.cleaner-info .name {
  font-weight: 500;
}

.cleaner-info .username {
  font-size: 12px;
  color: #909399;
}

.rating-value {
  margin-left: 8px;
  color: #ff9900;
  font-weight: bold;
}

.assign-dialog-content {
  padding: 10px;
}

.requirement-info {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.requirement-info h4 {
  margin: 0 0 8px 0;
}

.requirement-info p {
  margin: 4px 0;
  color: #606266;
}

.cleaner-option {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.cleaner-stats {
  font-size: 12px;
  color: #909399;
}
</style>
