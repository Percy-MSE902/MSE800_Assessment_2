<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { inventoryApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const inventoryList = ref([])

const canManage = computed(() => userStore.userInfo?.role === 'admin')

const categoryOptions = ['Textiles', 'Toiletries', 'Cleaning', 'Others']
const dialogVisible = ref(false)
const formData = ref({
  id: null,
  name: '',
  category: '',
  quantity: 0,
  min_stock: 0,
  unit: ''
})

const fetchInventory = async () => {
  loading.value = true
  try {
    const res = await inventoryApi.list()
    inventoryList.value = res || []
  } catch (error) {
    console.error('Failed to fetch inventory:', error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  formData.value = { id: null, name: '', category: '', quantity: 0, min_stock: 0, unit: '' }
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  formData.value = { ...row }
  dialogVisible.value = true
}

const handleRestock = async (row: any) => {
  try {
    await inventoryApi.restock(row.item_id, 10)
    ElMessage.success('Restocked successfully')
    fetchInventory()
  } catch (error) {
    ElMessage.error('Failed to restock')
  }
}

const getStockStatus = (row: any) => {
  if (row.quantity <= row.min_stock) return 'danger'
  if (row.quantity <= row.min_stock * 1.5) return 'warning'
  return 'success'
}

const handleSubmit = async () => {
  try {
    if (formData.value.id) {
      await inventoryApi.update(formData.value.id, formData.value)
      ElMessage.success('Updated successfully')
    } else {
      await inventoryApi.create(formData.value)
      ElMessage.success('Created successfully')
    }
    dialogVisible.value = false
    fetchInventory()
  } catch (error) {
    ElMessage.error('Operation failed')
  }
}

onMounted(() => {
  fetchInventory()
})
</script>

<template>
  <div class="inventory-page">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :lg="6" v-for="item in inventoryList" :key="item.item_id">
        <el-card shadow="hover" class="inventory-card">
          <div class="inventory-header">
            <span class="inventory-name">{{ item.item_name }}</span>
            <el-tag :type="getStockStatus(item)" size="small">
              {{ item.quantity <= item.min_stock ? 'Low Stock' : 'Normal' }}
            </el-tag>
          </div>
          <div class="inventory-info">
            <div class="info-row">
              <span class="label">Category</span>
              <span class="value">{{ item.category }}</span>
            </div>
            <div class="info-row">
              <span class="label">Quantity</span>
              <span class="value highlight">{{ item.quantity }} {{ item.unit }}</span>
            </div>
            <div class="info-row">
              <span class="label">Min Stock</span>
              <span class="value">{{ item.min_stock }} {{ item.unit }}</span>
            </div>
          </div>
          <div class="inventory-actions" v-if="canManage">
            <el-button type="primary" size="small" @click="handleEdit(item)">Edit</el-button>
            <el-button type="success" size="small" @click="handleRestock(item)">Restock</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>Inventory List</span>
          <el-button v-if="canManage" type="primary" @click="handleAdd">Add Item</el-button>
        </div>
      </template>

      <el-table :data="inventoryList" v-loading="loading" style="width: 100%">
        <el-table-column prop="item_id" label="ID" width="60" />
        <el-table-column prop="item_name" label="Item Name" width="120" />
        <el-table-column prop="category" label="Category" width="120" />
        <el-table-column prop="quantity" label="Quantity" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.quantity <= row.min_stock ? '#f56c6c' : '#67c23a' }">
              {{ row.quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="min_stock" label="Min Stock" width="100" />
        <el-table-column prop="unit" label="Unit" width="80" />
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStockStatus(row)">
              {{ row.quantity <= row.min_stock ? 'Low Stock' : 'Normal' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Action" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">Edit</el-button>
            <el-button type="success" link @click="handleRestock(row)">Restock</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="Inventory Item" width="500px" destroy-on-close>
      <el-form :model="formData" label-width="80px">
        <el-form-item label="Name">
          <el-input v-model="formData.name" placeholder="Item name" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="formData.category" placeholder="Select category" style="width: 100%">
            <el-option v-for="c in categoryOptions" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="Quantity">
          <el-input-number v-model="formData.quantity" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Min Stock">
          <el-input-number v-model="formData.min_stock" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Unit">
          <el-input v-model="formData.unit" placeholder="e.g., piece/bottle" />
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
.inventory-card {
  margin-bottom: 16px;
  border-radius: 12px;
}
.inventory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.inventory-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
.inventory-info {
  margin-bottom: 16px;
}
.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}
.info-row:last-child { border-bottom: none; }
.info-row .label { color: #909399; font-size: 14px; }
.info-row .value { color: #303133; font-weight: 500; }
.info-row .value.highlight { color: #409eff; font-size: 16px; }
.inventory-actions { display: flex; gap: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
