<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { portalService } from '@/services'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const activeTab = ref('requirements')
const myRequirements = ref<any[]>([])
const myOrders = ref<any[]>([])

const userInfo = computed(() => userStore.userInfo)
const isGuest = computed(() => userInfo.value?.role === 'guest' || !userInfo.value?.role)

const statusMap: Record<number, { label: string; type: string }> = {
  0: { label: 'Pending', type: 'warning' },
  1: { label: 'Assigned', type: 'success' },
  2: { label: 'In Progress', type: 'primary' },
  3: { label: 'Completed', type: 'info' },
  4: { label: 'Cancelled', type: 'danger' }
}

const loadMyData = async () => {
  if (!userInfo.value?.phone && userInfo.value?.role !== 'guest') return
  
  loading.value = true
  try {
    const phone = userInfo.value?.phone || ''
    
    const [reqRes, ordersRes] = await Promise.all([
      portalService.getRequirementsByPhone(phone),
      portalService.getOrdersByPhone(phone)
    ])
    
    myRequirements.value = reqRes || []
    myOrders.value = ordersRes || []
  } catch (e: any) {
    console.error('Failed to load data:', e)
  } finally {
    loading.value = false
  }
}

const getStatusInfo = (status: number) => {
  return statusMap[status] || { label: 'Unknown', type: 'info' }
}

onMounted(() => {
  loadMyData()
})
</script>

<template>
  <div class="my-orders-page">
    <div class="page-header">
      <h2>My Orders</h2>
      <p class="subtitle">View your requirements and bookings</p>
    </div>

    <el-tabs v-model="activeTab" class="order-tabs">
      <el-tab-pane label="My Requirements" name="requirements">
        <el-card class="order-card">
          <el-table :data="myRequirements" v-loading="loading" stripe>
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
            <el-table-column label="Status" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusInfo(row.status || 0).type">
                  {{ getStatusInfo(row.status || 0).label }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="Created" width="150">
              <template #default="{ row }">
                {{ row.create_time?.split('T')[0] }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loading && myRequirements.length === 0" description="No requirements posted yet" />
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="My Bookings" name="bookings">
        <el-card class="order-card">
          <el-table :data="myOrders" v-loading="loading" stripe>
            <el-table-column prop="order_no" label="Order No" width="180" />
            <el-table-column label="Service Type" width="150">
              <template #default="{ row }">
                <el-tag>{{ row.service_type_name || 'Service' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="room_number" label="Room" width="100" />
            <el-table-column label="Price" width="100">
              <template #default="{ row }">
                <span class="price">${{ row.actual_price || row.price || 0 }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Status" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusInfo(row.status).type">
                  {{ getStatusInfo(row.status).label }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Created" width="150">
              <template #default="{ row }">
                {{ row.create_time?.split('T')[0] }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loading && myOrders.length === 0" description="No bookings yet" />
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.my-orders-page {
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

.order-tabs {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.order-card {
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
</style>
