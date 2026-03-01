<script lang="ts">
import { ref, onMounted, computed } from 'vue'
import { roomApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

export default {
  name: 'Rooms',
  setup() {
    const userStore = useUserStore()
    const loading = ref(false)
    const roomList = ref([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(20)
    const dialogVisible = ref(false)
    const formData = ref({
      room_number: '',
      floor: 1,
      room_type: 'Single',
      capacity: 2,
      price: 0,
      description: ''
    })
    
    const filters = ref({
      room_number: '',
      room_type: '',
      status: '',
      floor: ''
    })
    
    const canAddRoom = computed(() => userStore.userInfo?.role === 'admin')
    const canChangeStatus = computed(() => ['admin', 'cleaner'].includes(userStore.userInfo?.role))
    
    const statusOptions = [
      { value: 0, label: 'Available', color: 'success' },
      { value: 1, label: 'Occupied', color: 'danger' },
      { value: 2, label: 'Cleaning', color: 'warning' },
      { value: 3, label: 'Pending Check', color: 'primary' },
      { value: 4, label: 'Maintenance', color: 'info' }
    ]
    
    const roomTypes = ['Single', 'Double', 'Suite', 'Deluxe Suite']
    
    const fetchRooms = async () => {
      loading.value = true
      try {
        const filterParams: any = {}
        if (filters.value.room_number) filterParams.room_number = filters.value.room_number
        if (filters.value.room_type) filterParams.room_type = filters.value.room_type
        if (filters.value.status !== '' && filters.value.status !== null) filterParams.status = filters.value.status
        if (filters.value.floor) filterParams.floor = filters.value.floor
        
        const res = await roomApi.paginated({
          page: currentPage.value,
          page_size: pageSize.value,
          filters: filterParams
        })
        roomList.value = res?.items || []
        total.value = res?.total || 0
      } catch (error) {
        console.error('Failed to fetch rooms:', error)
      } finally {
        loading.value = false
      }
    }
    
    const handleFilter = () => {
      currentPage.value = 1
      fetchRooms()
    }
    
    const handleReset = () => {
      filters.value = { room_number: '', room_type: '', status: '', floor: '' }
      currentPage.value = 1
      fetchRooms()
    }
    
    const handlePageChange = (page: number) => {
      currentPage.value = page
      fetchRooms()
    }
    
    const handleSizeChange = (size: number) => {
      pageSize.value = size
      currentPage.value = 1
      fetchRooms()
    }
    
    const handleAdd = () => {
      formData.value = { room_number: '', floor: 1, room_type: 'Single', capacity: 2, price: 0, description: '' }
      dialogVisible.value = true
    }
    
    const handleSubmit = async () => {
      try {
        await roomApi.create(formData.value)
        ElMessage.success('Created successfully')
        dialogVisible.value = false
        fetchRooms()
      } catch (error) {
        ElMessage.error('Failed to create')
      }
    }
    
    const handleUpdateStatus = async (row: any, status: number) => {
      try {
        await roomApi.updateStatus(row.room_id, status)
        ElMessage.success('Status updated')
        fetchRooms()
      } catch (error) {
        ElMessage.error('Update failed')
      }
    }
    
    const getStatusType = (status: number) => {
      return statusOptions.find(s => s.value === status)?.color || 'info'
    }
    
    const getStatusLabel = (status: number) => {
      return statusOptions.find(s => s.value === status)?.label || 'Unknown'
    }
    
    onMounted(() => {
      fetchRooms()
    })
    
    return {
      roomList,
      loading,
      total,
      currentPage,
      pageSize,
      dialogVisible,
      formData,
      filters,
      canAddRoom,
      canChangeStatus,
      statusOptions,
      roomTypes,
      handleAdd,
      handleSubmit,
      handleUpdateStatus,
      handleFilter,
      handleReset,
      handlePageChange,
      handleSizeChange,
      getStatusType,
      getStatusLabel
    }
  }
}
</script>

<template>
  <div class="rooms-page">
    <el-card shadow="hover" class="filter-card">
      <template #header>
        <span>Filter Rooms</span>
      </template>
      <el-row :gutter="16">
        <el-col :span="5">
          <el-input v-model="filters.room_number" placeholder="Room No" clearable @keyup.enter="handleFilter" />
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.room_type" placeholder="Room Type" clearable style="width: 100%">
            <el-option v-for="t in roomTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 100%">
            <el-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-input v-model="filters.floor" placeholder="Floor" clearable type="number" />
        </el-col>
        <el-col :span="5">
          <el-button type="primary" @click="handleFilter">Search</el-button>
          <el-button @click="handleReset">Reset</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="hover" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>Room List ({{ total }})</span>
          <el-button v-if="canAddRoom" type="primary" @click="handleAdd">Add Room</el-button>
        </div>
      </template>

      <el-table :data="roomList" v-loading="loading" style="width: 100%">
        <el-table-column prop="room_number" label="Room No" width="100" />
        <el-table-column prop="floor" label="Floor" width="80" />
        <el-table-column prop="room_type" label="Type" width="120" />
        <el-table-column prop="capacity" label="Capacity" width="80" />
        <el-table-column prop="price" label="Price" width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Action" width="150">
          <template #default="{ row }">
            <el-dropdown v-if="canChangeStatus" @command="(cmd) => handleUpdateStatus(row, cmd)">
              <el-button type="primary" link>Change Status</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="opt in statusOptions" :key="opt.value" :command="opt.value">
                    {{ opt.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100, 500]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" title="Add Room" width="500px" destroy-on-close>
      <el-form :model="formData" label-width="80px">
        <el-form-item label="Room No">
          <el-input v-model="formData.room_number" placeholder="e.g., 1001" clearable></el-input>
        </el-form-item>
        <el-form-item label="Floor">
          <el-input-number v-model="formData.floor" :min="1" :max="500" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Type">
          <el-select v-model="formData.room_type" style="width: 100%">
            <el-option v-for="t in roomTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="Capacity">
          <el-input-number v-model="formData.capacity" :min="1" :max="10" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Price">
          <el-input-number v-model="formData.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="formData.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSubmit">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.filter-card {
  margin-bottom: 0;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
