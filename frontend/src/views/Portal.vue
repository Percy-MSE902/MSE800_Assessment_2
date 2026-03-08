<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { portalApi } from '@/api'

const router = useRouter()
const userStore = useUserStore()

const isLoggedIn = computed(() => !!userStore.userInfo)
const userInfo = computed(() => userStore.userInfo)

const searchKeyword = ref('')
const selectedCategory = ref('')
const loading = ref(false)
const services = ref<any[]>([])
const rooms = ref<any[]>([])
const stats = ref({ total_users: 0, total_orders: 0, total_rooms: 0, rating: 4.9 })
const myOrders = ref<any[]>([])

const showOrderDialog = ref(false)
const orderForm = ref({
  service_type_id: 0,
  room_id: 0,
  guest_name: '',
  guest_phone: '',
  scheduled_time: '',
  remarks: ''
})
const selectedService = ref<any>(null)

const testimonials = ref([
  { id: 1, name: 'Ms. Zhang', content: 'Very professional service, the room was cleaned very well. Highly recommended!', rating: 5 },
  { id: 2, name: 'Mr. Li', content: 'Easy to book, the cleaner arrived on time. Very satisfied.', rating: 5 },
  { id: 3, name: 'Boss Wang', content: 'Office cleaning service is excellent, all staff are happy.', rating: 4 },
])

const serviceImages: Record<number, string> = {
  1: 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=400',
  2: 'https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?w=400',
  3: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400',
  4: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=400',
  5: 'https://images.unsplash.com/photo-1527515545081-5db817172677?w=400',
  6: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400',
}

const ads = ref([
  { id: 1, title: 'New User Special', subtitle: '30% off first order', color: '#ff6b6b' },
  { id: 2, title: 'Member Benefits', subtitle: 'Recharge $500 get $100', color: '#4ecdc4' },
])

const loadData = async () => {
  try {
    loading.value = true
    const [servicesRes, roomsRes, statsRes] = await Promise.all([
      portalApi.getServices(),
      portalApi.getRooms(),
      portalApi.getStats()
    ])
    services.value = servicesRes
    rooms.value = roomsRes
    stats.value = statsRes
    
    if (isLoggedIn.value && userInfo.value?.phone) {
      const ordersRes = await portalApi.getOrders(userInfo.value.phone)
      myOrders.value = ordersRes
    }
  } catch (e: any) {
    console.error('Failed to load data:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

const handleSearch = () => {
  ElMessage.info('搜索功能开发中')
}

const handleCategoryClick = (service: any) => {
  openOrderDialog(service)
}

const openOrderDialog = (service: any) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('Please login first to book service')
    router.push({ path: '/login', query: { redirect: 'portal' } })
    return
  }
  selectedService.value = service
  orderForm.value = {
    service_type_id: service.type_id,
    room_id: rooms.value[0]?.room_id || 0,
    guest_name: userInfo.value?.full_name || userInfo.value?.username || '',
    guest_phone: userInfo.value?.phone || '',
    scheduled_time: '',
    remarks: ''
  }
  showOrderDialog.value = true
}

const handleOrder = (service: any) => {
  openOrderDialog(service)
}

const submitOrder = async () => {
  if (!orderForm.value.guest_name || !orderForm.value.guest_phone) {
    ElMessage.warning('Please fill in name and phone')
    return
  }
  if (!orderForm.value.room_id) {
    ElMessage.warning('Please select a room')
    return
  }
  
  try {
    loading.value = true
    const res = await portalApi.createOrder({
      service_type_id: orderForm.value.service_type_id,
      room_id: orderForm.value.room_id,
      guest_name: orderForm.value.guest_name,
      guest_phone: orderForm.value.guest_phone,
      scheduled_time: orderForm.value.scheduled_time || null,
      remarks: orderForm.value.remarks || null
    })
    
    if (res.success) {
      ElMessage.success(`Booking successful! Order No: ${res.order_no}`)
      showOrderDialog.value = false
      loadData()
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Booking failed, please try again later')
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push({ path: '/login', query: { redirect: 'portal' } })
}

const goToRegister = () => {
  router.push({ path: '/login', query: { mode: 'register', redirect: 'portal' } })
}

const goToDashboard = (path: string) => {
  if (path === 'logout') {
    handleLogout()
  } else {
    router.push(path)
  }
}

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('Logged out successfully')
  router.push('/')
}

const getStatusText = (status: number) => {
  const statusMap: Record<number, string> = {
    0: 'Pending',
    1: 'Accepted',
    2: 'In Progress',
    3: 'Completed',
    4: 'Pending Payment',
    5: 'Cancelled'
  }
  return statusMap[status] || 'Unknown'
}

const getStatusType = (status: number) => {
  const typeMap: Record<number, string> = {
    0: 'warning',
    1: 'primary',
    2: 'info',
    3: 'success',
    4: 'danger',
    5: 'info'
  }
  return typeMap[status] || 'info'
}

const filteredServices = computed(() => {
  if (!searchKeyword.value) return services.value
  const keyword = searchKeyword.value.toLowerCase()
  return services.value.filter(s => 
    s.type_name.toLowerCase().includes(keyword) || 
    (s.description && s.description.toLowerCase().includes(keyword))
  )
})
</script>

<template>
  <div class="portal-page">
    <!-- Header -->
    <header class="portal-header">
      <div class="header-content">
        <div class="logo">
          <el-icon class="logo-icon"><House /></el-icon>
          <span class="logo-text">CleanPro</span>
          <span class="logo-tag">Business</span>
        </div>
        
        <!-- Logged in user menu -->
        <div class="header-actions" v-if="isLoggedIn">
          <el-dropdown trigger="click" @command="goToDashboard">
            <div class="user-menu">
              <el-avatar :size="32" class="user-avatar">
                {{ userInfo?.username?.charAt(0)?.toUpperCase() || 'U' }}
              </el-avatar>
              <span class="username">{{ userInfo?.username || 'User' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="/home">Home</el-dropdown-item>
                <el-dropdown-item command="/orders">My Orders</el-dropdown-item>
                <el-dropdown-item command="/rooms">Room Management</el-dropdown-item>
                <el-dropdown-item command="/staff">Staff Management</el-dropdown-item>
                <el-dropdown-item command="/inventory">Inventory</el-dropdown-item>
                <el-dropdown-item command="/wallet">My Wallet</el-dropdown-item>
                <el-dropdown-item command="/settings">Settings</el-dropdown-item>
                <el-dropdown-item divided command="logout">Logout</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        
        <!-- Login/Register buttons for guests -->
        <div class="header-actions" v-else>
          <el-button text @click="goToLogin">Login</el-button>
          <el-button type="primary" @click="goToRegister">Sign Up</el-button>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <h1>Professional Hotel Cleaning Services</h1>
        <p>One-stop cleaning solutions for hotels, apartments, and offices</p>
        
        <!-- Search Box -->
        <div class="search-box">
          <el-input
            v-model="searchKeyword"
            placeholder="Search for services..."
            size="large"
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" size="large" class="search-btn" @click="handleSearch">
            Search
          </el-button>
        </div>
        
        <div class="hot-keywords">
          <span>Popular:</span>
          <el-tag effect="plain" class="keyword-tag">Room Cleaning</el-tag>
          <el-tag effect="plain" class="keyword-tag">Deep Cleaning</el-tag>
          <el-tag effect="plain" class="keyword-tag">Move-in Cleaning</el-tag>
          <el-tag effect="plain" class="keyword-tag">Bedding Service</el-tag>
        </div>
      </div>
    </section>

    <!-- Categories -->
    <section class="categories-section">
      <div class="section-title">
        <h2>Service Categories</h2>
        <el-button link type="primary">View All</el-button>
      </div>
      <div class="categories-grid">
        <div
          v-for="service in filteredServices"
          :key="service.type_id"
          class="category-card"
          @click="handleCategoryClick(service)"
        >
          <div class="category-image">
            <img :src="serviceImages[service.type_id] || serviceImages[1]" :alt="service.type_name" />
          </div>
          <div class="category-info">
            <h3>{{ service.type_name }}</h3>
            <p>{{ service.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Ads Banner -->
    <section class="ads-section">
      <el-row :gutter="20">
        <el-col :span="12" v-for="ad in ads" :key="ad.id">
          <div class="ad-card" :style="{ backgroundColor: ad.color }">
            <div class="ad-content">
              <h3>{{ ad.title }}</h3>
              <p>{{ ad.subtitle }}</p>
            </div>
          </div>
        </el-col>
      </el-row>
    </section>

    <!-- Hot Services -->
    <section class="services-section">
      <div class="section-title">
        <h2>Popular Services</h2>
        <el-button link type="primary">View More</el-button>
      </div>
      <div class="services-grid">
        <div v-for="service in filteredServices" :key="service.type_id" class="service-card">
          <div class="service-image">
            <img :src="serviceImages[service.type_id] || serviceImages[1]" :alt="service.type_name" />
            <div class="service-badge">Hot</div>
          </div>
          <div class="service-info">
            <h3>{{ service.type_name }}</h3>
            <div class="service-meta">
              <span class="rating">
                <el-icon><Star /></el-icon>
                4.9
              </span>
              <span class="sales">{{ Math.floor(Math.random() * 1000) + 500 }}+ sold</span>
            </div>
            <div class="service-price">
              <span class="price">${{ service.price }}</span>
              <span class="unit">/visit</span>
            </div>
            <el-button type="primary" size="small" class="order-btn" @click="handleOrder(service)">
              Book Now
            </el-button>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials -->
    <section class="testimonials-section">
      <div class="section-title">
        <h2>Customer Reviews</h2>
      </div>
      <div class="testimonials-grid">
        <div v-for="item in testimonials" :key="item.id" class="testimonial-card">
          <div class="testimonial-stars">
            <el-icon v-for="n in item.rating" :key="n" color="#ff9900"><Star /></el-icon>
          </div>
          <p class="testimonial-content">{{ item.content }}</p>
          <div class="testimonial-author">
            <el-avatar :size="36">{{ item.name.charAt(0) }}</el-avatar>
            <span>{{ item.name }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats -->
    <section class="stats-section">
      <div class="stats-content">
        <div class="stat-item">
          <span class="stat-number">{{ stats.total_users > 10000 ? '10,000+' : stats.total_users }}</span>
          <span class="stat-label">服务客户</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ stats.total_rooms > 500 ? '500+' : stats.total_rooms }}</span>
          <span class="stat-label">合作酒店</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ stats.total_orders > 50000 ? '50,000+' : stats.total_orders }}</span>
          <span class="stat-label">完成订单</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ stats.rating }}</span>
          <span class="stat-label">客户评分</span>
        </div>
      </div>
    </section>

    <!-- Order Dialog -->
    <el-dialog v-model="showOrderDialog" title="Book Service" width="500px">
      <el-form :model="orderForm" label-width="100px">
        <el-form-item label="Service Type">
          <el-input :value="selectedService?.type_name" disabled />
        </el-form-item>
        <el-form-item label="Service Price">
          <el-input :value="'$' + selectedService?.price" disabled />
        </el-form-item>
        <el-form-item label="Select Room" required>
          <el-select v-model="orderForm.room_id" placeholder="Select a room" style="width: 100%">
            <el-option
              v-for="room in rooms"
              :key="room.room_id"
              :label="room.room_number + ' - ' + room.room_type"
              :value="room.room_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Contact Name" required>
          <el-input v-model="orderForm.guest_name" placeholder="Enter your name" />
        </el-form-item>
        <el-form-item label="Phone" required>
          <el-input v-model="orderForm.guest_phone" placeholder="Enter your phone number" />
        </el-form-item>
        <el-form-item label="Schedule">
          <el-date-picker
            v-model="orderForm.scheduled_time"
            type="datetime"
            placeholder="Select date and time"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="orderForm.remarks" type="textarea" rows="3" placeholder="Enter any special requests" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showOrderDialog = false">Cancel</el-button>
        <el-button type="primary" :loading="loading" @click="submitOrder">Confirm Booking</el-button>
      </template>
    </el-dialog>

    <!-- Footer -->
    <footer class="portal-footer">
      <div class="footer-content">
        <div class="footer-section">
          <h4>About Us</h4>
          <p>CleanPro is a professional hotel cleaning service platform, committed to providing high-quality cleaning services to our customers.</p>
        </div>
        <div class="footer-section">
          <h4>Contact Us</h4>
          <p>Phone: 400-888-8888</p>
          <p>Email: service@cleanpro.com</p>
          <p>Address: Pudong New District, Shanghai</p>
        </div>
        <div class="footer-section">
          <h4>Follow Us</h4>
          <div class="social-links">
            <el-icon :size="24"><Link /></el-icon>
            <el-icon :size="24"><ChatDotRound /></el-icon>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2024 CleanPro. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.portal-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.portal-header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  font-size: 32px;
  color: #409eff;
}

.logo-text {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.logo-tag {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(64, 158, 255, 0.1);
  transition: all 0.3s;
}

.user-menu:hover {
  background: rgba(64, 158, 255, 0.2);
}

.user-avatar {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
}

.username {
  color: #409eff;
  font-weight: 500;
}

.hero-section {
  background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 50%, #3d7ab5 100%);
  padding: 80px 24px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  width: 600px;
  height: 600px;
  background: rgba(255,255,255,0.05);
  border-radius: 50%;
  top: -200px;
  right: -100px;
}

.hero-section::after {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  background: rgba(255,255,255,0.03);
  border-radius: 50%;
  bottom: -100px;
  left: -100px;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.hero-content h1 {
  color: #fff;
  font-size: 42px;
  margin-bottom: 16px;
}

.hero-content p {
  color: rgba(255,255,255,0.9);
  font-size: 18px;
  margin-bottom: 40px;
}

.search-box {
  display: flex;
  gap: 8px;
  max-width: 600px;
  margin: 0 auto 24px;
}

.search-input {
  flex: 1;
}

.search-btn {
  width: 100px;
}

.hot-keywords {
  color: rgba(255,255,255,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.keyword-tag {
  cursor: pointer;
  background: rgba(255,255,255,0.2);
  border: none;
  color: #fff;
}

.keyword-tag:hover {
  background: rgba(255,255,255,0.3);
}

.categories-section,
.services-section,
.testimonials-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 24px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.section-title h2 {
  font-size: 24px;
  color: #303133;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.category-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(64,158,255,0.15);
}

.category-image {
  width: 100%;
  height: 120px;
  overflow: hidden;
}

.category-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.category-card:hover .category-image img {
  transform: scale(1.1);
}

.category-info {
  padding: 12px;
  text-align: center;
}

.category-info h3 {
  font-size: 14px;
  margin-bottom: 4px;
  color: #303133;
}

.category-info p {
  font-size: 11px;
  color: #909399;
}

.ads-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 40px;
}

.ad-card {
  border-radius: 12px;
  padding: 32px;
  color: #fff;
  cursor: pointer;
  transition: transform 0.3s;
}

.ad-card:hover {
  transform: scale(1.02);
}

.ad-content h3 {
  font-size: 24px;
  margin-bottom: 8px;
}

.ad-content p {
  font-size: 16px;
  opacity: 0.9;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.service-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: all 0.3s;
}

.service-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.service-image {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.service-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.service-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: #ff6b6b;
  color: #fff;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
}

.service-info {
  padding: 16px;
}

.service-info h3 {
  font-size: 16px;
  margin-bottom: 8px;
  color: #303133;
}

.service-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 12px;
  color: #909399;
}

.rating {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #ff9900;
}

.service-price {
  margin-bottom: 12px;
}

.price {
  font-size: 20px;
  color: #ff6b6b;
  font-weight: bold;
}

.unit {
  font-size: 12px;
  color: #909399;
}

.order-btn {
  width: 100%;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.testimonial-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.testimonial-stars {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
}

.testimonial-content {
  color: #606266;
  line-height: 1.8;
  margin-bottom: 16px;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.testimonial-author span {
  color: #303133;
  font-weight: 500;
}

.stats-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 24px;
}

.stats-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
  color: #fff;
}

.stat-number {
  display: block;
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.portal-footer {
  background: #303133;
  color: #fff;
  padding: 60px 24px 20px;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
}

.footer-section h4 {
  font-size: 18px;
  margin-bottom: 16px;
}

.footer-section p {
  color: #909399;
  line-height: 2;
}

.social-links {
  display: flex;
  gap: 16px;
}

.footer-bottom {
  max-width: 1200px;
  margin: 40px auto 0;
  padding-top: 20px;
  border-top: 1px solid #404040;
  text-align: center;
  color: #909399;
}

@media (max-width: 768px) {
  .categories-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .services-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .testimonials-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-content {
    flex-wrap: wrap;
    gap: 32px;
  }
  
  .footer-content {
    grid-template-columns: 1fr;
  }
}
</style>
