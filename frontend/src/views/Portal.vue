<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { portalApi } from '@/api'

const router = useRouter()
const userStore = useUserStore()

const isLoggedIn = computed(() => !!userStore.userInfo)
const userInfo = computed(() => userStore.userInfo)
const isCleaner = computed(() => ['staff', 'cleaner', 'employee'].includes(userStore.userInfo?.role))
const activeTaskTab = ref('applications')

const getStatusType = (status: number) => {
  const types = ['warning', 'success', 'danger', 'info']
  return types[status] || 'info'
}

const getStatusText = (status: number) => {
  const texts = ['Pending', 'Accepted', 'Rejected', 'Completed']
  return texts[status] || 'Unknown'
}

const searchKeyword = ref('')
const selectedCategory = ref('')
const loading = ref(false)
const services = ref<any[]>([])
const rooms = ref<any[]>([])
const stats = ref({ total_users: 0, total_orders: 0, total_rooms: 0, rating: 4.9 })
const companyInfo = ref<any>({
  about_us: '',
  phone: '',
  email: '',
  address: '',
  facebook: '',
  twitter: '',
  instagram: ''
})
const myOrders = ref<any[]>([])
const myTasks = ref<any[]>([])
const myApplications = ref<any[]>([])
const myCompletedOrders = ref<any[]>([])

const showOrderDialog = ref(false)
const showCleanerDialog = ref(false)
const showServiceDetailDialog = ref(false)
const serviceDetail = ref<any>(null)
const showReviewDetailDialog = ref(false)
const selectedReview = ref<any>(null)
const reviewsOffset = ref(0)
const reviewsLimit = 6
const hasMoreReviews = ref(false)
const orderForm = ref({
  service_type_id: 0,
  room_id: 0,
  guest_name: '',
  guest_phone: '',
  scheduled_time: '',
  remarks: '',
  cleaner_id: null as number | null
})
const selectedService = ref<any>(null)
const cleaners = ref<any[]>([])
const cleanerSearch = ref('')
const cleanerSort = ref('')
const selectedCleaner = ref<any>(null)
const requirements = ref<any[]>([])
const showRequirementDialog = ref(false)
const showApplyDialog = ref(false)
const requirementForm = ref({
  guest_name: '',
  guest_phone: '',
  guest_email: '',
  property_type: 'House',
  bedroom: 2,
  bathroom: 1,
  living_room: 1,
  kitchen: 1,
  lawn: 0,
  car_space: 0,
  square_footage: null,
  service_type_name: '',
  preferred_time: '',
  budget: null,
  description: ''
})
const selectedRequirement = ref<any>(null)
const applications = ref<any[]>([])
const applyForm = ref({
  requirement_id: 0,
  cleaner_id: 0,
  cleaner_name: '',
  offered_price: null,
  message: ''
})

const testimonials = ref<any[]>([
  { id: 1, name: 'Ms. Zhang', content: 'Very professional service, the room was cleaned very well. Highly recommended!', rating: 5 },
  { id: 2, name: 'Mr. Li', content: 'Easy to book, the cleaner arrived on time. Very satisfied.', rating: 5 },
  { id: 3, name: 'Boss Wang', content: 'Office cleaning service is excellent, all staff are happy.', rating: 4 },
])

const serviceImages: Record<number, string> = {
  1: 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=400',
  2: 'https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?w=400',
  3: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400',
  4: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=400',
  5: 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=400',
  6: 'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=400',
  7: 'https://images.unsplash.com/photo-1558904541-efa843a96f01?w=400',
  8: 'https://images.unsplash.com/photo-1527515545081-5db817172677?w=400',
  9: 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400',
  10: 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400',
  11: 'https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=400',
  12: 'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=400',
  13: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400',
  14: 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=400',
  15: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400',
}

const ads = ref([
  { id: 1, title: 'New User Special', subtitle: '30% off first order', color: '#ff6b6b' },
  { id: 2, title: 'Member Benefits', subtitle: 'Recharge $500 get $100', color: '#4ecdc4' },
])

const displayedCleaners = computed(() => {
  return cleaners.value.slice(0, 4)
})

const displayedRequirements = computed(() => {
  return requirements.value.slice(0, 8)
})

const loadData = async () => {
  try {
    loading.value = true
    console.log('Loading portal data...')
    
    const servicesRes = await portalApi.getServices()
    console.log('Services:', servicesRes)
    services.value = servicesRes
    
    const roomsRes = await portalApi.getRooms()
    console.log('Rooms:', roomsRes)
    rooms.value = roomsRes
    
    const statsRes = await portalApi.getStats()
    console.log('Stats:', statsRes)
    stats.value = statsRes
    
    const companyInfoRes = await portalApi.getCompanyInfo()
    console.log('Company Info:', companyInfoRes)
    companyInfo.value = companyInfoRes
    
    const reviewsRes = await portalApi.getReviews(6)
    console.log('Reviews:', reviewsRes)
    if (reviewsRes && reviewsRes.length > 0) {
      testimonials.value = reviewsRes.map((r: any) => ({
        id: r.id,
        name: r.guest_name,
        content: r.comment,
        rating: r.rating,
        service: r.service_type_name,
        date: r.create_time
      }))
      hasMoreReviews.value = reviewsRes.length >= reviewsLimit
    }
    
    const cleanersRes = await portalApi.getCleaners()
    console.log('Cleaners:', cleanersRes)
    cleaners.value = cleanersRes
    
    const requirementsRes = await portalApi.getRequirements({ limit: 50 })
    console.log('Requirements:', requirementsRes)
    requirements.value = requirementsRes
    
    // Load cleaner tasks if logged in as cleaner
    if (isLoggedIn.value && isCleaner.value && userInfo.value?.id) {
      try {
        const tasksRes = await portalApi.getCleanerTasks(userInfo.value.id)
        console.log('My Tasks:', tasksRes)
        myTasks.value = tasksRes || []
        
        const appsRes = await portalApi.getCleanerApplications(userInfo.value.id)
        console.log('My Applications:', appsRes)
        myApplications.value = appsRes || []
      } catch (e) {
        console.error('Failed to load cleaner tasks:', e)
      }
    }
    
    console.log('All data loaded successfully')
  } catch (e: any) {
    console.error('Failed to load data:', e)
    ElMessage.error('Failed to load data: ' + (e?.message || e?.response?.data?.detail || 'Unknown error'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

const loadCleaners = async () => {
  try {
    const params: any = {}
    if (cleanerSearch.value) {
      params.search = cleanerSearch.value
    }
    if (cleanerSort.value) {
      params.sort_by = cleanerSort.value
    }
    const res = await portalApi.getCleaners(params)
    cleaners.value = res
  } catch (e) {
    console.error('Failed to load cleaners:', e)
  }
}

const submitRequirement = async () => {
  if (!requirementForm.value.guest_name || !requirementForm.value.guest_phone) {
    ElMessage.warning('Please fill in name and phone')
    return
  }
  
  try {
    loading.value = true
    const res = await portalApi.createRequirement(requirementForm.value)
    if (res.success) {
      ElMessage.success('Requirement posted successfully!')
      showRequirementDialog.value = false
      loadData()
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Failed to post requirement')
  } finally {
    loading.value = false
  }
}

const viewApplications = async (requirement: any) => {
  selectedRequirement.value = requirement
  try {
    const res = await portalApi.getApplications(requirement.id)
    applications.value = res
    showApplyDialog.value = true
  } catch (e) {
    console.error('Failed to load applications:', e)
  }
}

const openApplyForm = (requirement: any) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('Please login first')
    router.push({ path: '/login', query: { redirect: 'portal' } })
    return
  }
  if (!isCleaner.value) {
    ElMessage.warning('Only cleaners can apply for jobs')
    return
  }
  selectedRequirement.value = requirement
  applyForm.value = {
    requirement_id: requirement.id,
    cleaner_id: userInfo.value?.id || 0,
    cleaner_name: userInfo.value?.full_name || userInfo.value?.username || '',
    offered_price: requirement.budget || null,
    message: ''
  }
  showApplyDialog.value = true
}

const submitApplication = async () => {
  if (!applyForm.value.cleaner_name || !applyForm.value.offered_price) {
    ElMessage.warning('Please fill in your name and offer price')
    return
  }
  
  try {
    loading.value = true
    const res = await portalApi.applyForRequirement(applyForm.value)
    if (res.success) {
      ElMessage.success('Application submitted successfully!')
      showApplyDialog.value = false
      applyForm.value = {
        requirement_id: 0,
        cleaner_id: 0,
        cleaner_name: '',
        offered_price: null,
        message: ''
      }
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Failed to apply')
  } finally {
    loading.value = false
  }
}

const openCleanerSelection = async (service: any) => {
  if (!service && !selectedService.value) {
    ElMessage.warning('Please select a service type first')
    return
  }
  if (service) {
    selectedService.value = service
  }
  await loadCleaners()
  showCleanerDialog.value = true
}

const selectCleaner = (cleaner: any) => {
  if (!selectedService.value) {
    ElMessage.warning('Please select a service first')
    return
  }
  selectedCleaner.value = cleaner
  orderForm.value.cleaner_id = cleaner.id
  showCleanerDialog.value = false
  openOrderDialog(selectedService.value)
}

const handleSearch = () => {
  ElMessage.info('搜索功能开发中')
}

const handleCategoryClick = async (service: any) => {
  try {
    loading.value = true
    const detail = await portalApi.getServiceDetail(service.type_id)
    serviceDetail.value = detail
    showServiceDetailDialog.value = true
  } catch (e: any) {
    console.error('Failed to load service detail:', e)
    ElMessage.error('Failed to load service details')
  } finally {
    loading.value = false
  }
}

const handleBookNow = (service: any) => {
  showServiceDetailDialog.value = false
  openOrderDialog(service)
}

const loadMoreReviews = async () => {
  try {
    loading.value = true
    reviewsOffset.value += reviewsLimit
    const moreReviews = await portalApi.getReviews(reviewsLimit, reviewsOffset.value)
    
    if (moreReviews && moreReviews.length > 0) {
      const newReviews = moreReviews.map((r: any) => ({
        id: r.id,
        name: r.guest_name,
        content: r.comment,
        rating: r.rating,
        service: r.service_type_name,
        date: r.create_time
      }))
      testimonials.value = [...testimonials.value, ...newReviews]
      hasMoreReviews.value = moreReviews.length >= reviewsLimit
    } else {
      hasMoreReviews.value = false
    }
  } catch (e: any) {
    console.error('Failed to load more reviews:', e)
  } finally {
    loading.value = false
  }
}

const viewReviewDetail = async (review: any) => {
  selectedReview.value = review
  showReviewDetailDialog.value = true
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
    remarks: '',
    cleaner_id: selectedCleaner.value?.id || null
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
      remarks: orderForm.value.remarks || null,
      cleaner_id: orderForm.value.cleaner_id || null
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

    <!-- Our Professional Cleaners -->
    <section class="cleaners-section">
      <div class="section-title">
        <h2>Our Professional Cleaners</h2>
        <el-button type="primary" @click="openCleanerSelection">View All Cleaners</el-button>
      </div>
      <div class="cleaners-grid">
        <div 
          v-for="cleaner in displayedCleaners" 
          :key="cleaner.id" 
          class="cleaner-profile-card"
          @click="selectCleaner(cleaner)"
        >
          <el-avatar :size="80" class="profile-avatar">
            {{ cleaner.full_name?.charAt(0) || 'C' }}
          </el-avatar>
          <div class="profile-name">{{ cleaner.full_name }}</div>
          <div class="profile-stars">
            <el-rate 
              v-for="n in cleaner.star_level" 
              :key="n" 
              :model-value="1" 
              disabled 
              :max="1"
              style="margin-right: 2px"
            />
            <span class="star-text">{{ cleaner.star_level }} Star</span>
          </div>
          <div class="profile-stats">
            <div class="stat">
              <span class="stat-num">{{ cleaner.total_orders }}+</span>
              <span class="stat-label">Orders</span>
            </div>
            <div class="stat">
              <span class="stat-num">{{ cleaner.total_rating }}</span>
              <span class="stat-label">Rating</span>
            </div>
          </div>
          <el-button type="primary" size="small">Book Now</el-button>
        </div>
      </div>
    </section>

    <!-- Customer Requirements -->
    <section class="requirements-section">
      <div class="section-title">
        <h2>Customer Cleaning Requirements</h2>
        <el-button type="primary" @click="showRequirementDialog = true">Post Your Requirement</el-button>
      </div>
      <div class="requirements-grid">
        <div v-for="req in displayedRequirements" :key="req.id" class="requirement-card">
          <div class="req-header">
            <el-tag type="success">{{ req.property_type }}</el-tag>
            <span class="req-time">{{ req.create_time?.split('T')[0] }}</span>
          </div>
          <div class="req-details">
            <div class="detail-row">
              <span class="label">Bedroom:</span>
              <span class="value">{{ req.bedroom }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Bathroom:</span>
              <span class="value">{{ req.bathroom }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Living Room:</span>
              <span class="value">{{ req.living_room }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Kitchen:</span>
              <span class="value">{{ req.kitchen }}</span>
            </div>
            <div class="detail-row" v-if="req.lawn">
              <span class="label">Lawn:</span>
              <span class="value">{{ req.lawn }}</span>
            </div>
            <div class="detail-row" v-if="req.car_space">
              <span class="label">Car Space:</span>
              <span class="value">{{ req.car_space }}</span>
            </div>
            <div class="detail-row" v-if="req.square_footage">
              <span class="label">Area:</span>
              <span class="value">{{ req.square_footage }} sqft</span>
            </div>
          </div>
          <div class="req-service">
            <el-tag>{{ req.service_type_name }}</el-tag>
          </div>
          <div class="req-footer">
            <div class="budget">
              <span class="price">${{ req.budget }}</span>
              <span class="time">{{ req.preferred_time }}</span>
            </div>
            <div class="req-actions">
              <el-button type="primary" size="small" @click="viewApplications(req)">
                View Applications ({{ req.applications_count || 0 }})
              </el-button>
              <el-button v-if="isLoggedIn && isCleaner" type="success" size="small" @click="openApplyForm(req)">
                Apply Now
              </el-button>
            </div>
          </div>
        </div>
      </div>
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
        <div v-for="item in testimonials" :key="item.id" class="testimonial-card" @click="viewReviewDetail(item)">
          <div class="testimonial-stars">
            <el-icon v-for="n in item.rating" :key="n" color="#ff9900"><Star /></el-icon>
          </div>
          <p class="testimonial-content">{{ item.content }}</p>
          <div class="testimonial-author">
            <el-avatar :size="36">{{ item.name?.charAt(0) || 'G' }}</el-avatar>
            <span>{{ item.name }}</span>
            <span v-if="item.service" class="review-service">{{ item.service }}</span>
          </div>
        </div>
      </div>
      <div v-if="hasMoreReviews" class="view-more-reviews">
        <el-button type="primary" link @click="loadMoreReviews" :loading="loading">
          View More Reviews <el-icon><ArrowDown /></el-icon>
        </el-button>
      </div>
    </section>

    <!-- Review Detail Dialog -->
    <el-dialog v-model="showReviewDetailDialog" title="Review Details" width="500px">
      <div v-if="selectedReview" class="review-detail">
        <div class="review-detail-header">
          <el-avatar :size="60">{{ selectedReview.name?.charAt(0) || 'G' }}</el-avatar>
          <div class="review-detail-info">
            <h3>{{ selectedReview.name }}</h3>
            <div class="review-detail-stars">
              <el-rate v-model="selectedReview.rating" disabled :max="5" />
              <span class="rating-value">{{ selectedReview.rating }}.0</span>
            </div>
          </div>
        </div>
        <div class="review-detail-service">
          <el-tag v-if="selectedReview.service" type="info">{{ selectedReview.service }}</el-tag>
          <el-tag v-if="selectedReview.date" type="success">{{ selectedReview.date }}</el-tag>
        </div>
        <div class="review-detail-comment">
          <h4>Comment</h4>
          <p>{{ selectedReview.content }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="showReviewDetailDialog = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Stats -->
    <section class="stats-section">
      <div class="stats-content">
        <div class="stat-item">
          <span class="stat-number">{{ stats.total_users > 10000 ? '10,000+' : stats.total_users }}</span>
          <span class="stat-label">Total Users</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ stats.total_rooms > 500 ? '500+' : stats.total_rooms }}</span>
          <span class="stat-label">Partner Hotels</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ stats.total_orders > 50000 ? '50,000+' : stats.total_orders }}</span>
          <span class="stat-label">Completed Orders</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ stats.rating }}</span>
          <span class="stat-label">Customer Rating</span>
        </div>
      </div>
    </section>

    <!-- Cleaner Selection Dialog -->
    <el-dialog v-model="showCleanerDialog" title="Select Your Cleaner" width="700px">
      <div class="cleaner-filters">
        <el-input
          v-model="cleanerSearch"
          placeholder="Search by name..."
          clearable
          style="width: 200px; margin-right: 10px"
          @clear="loadCleaners"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="cleanerSort"
          placeholder="Sort by"
          style="width: 180px; margin-right: 10px"
          @change="loadCleaners"
        >
          <el-option label="Default" value="" />
          <el-option label="Rating (High to Low)" value="rating_desc" />
          <el-option label="Rating (Low to High)" value="rating_asc" />
          <el-option label="Most Orders" value="orders_desc" />
          <el-option label="Least Orders" value="orders_asc" />
        </el-select>
        <el-button type="primary" @click="loadCleaners">Search</el-button>
      </div>
      <div class="cleaner-list" style="margin-top: 15px">
        <div 
          v-for="cleaner in cleaners" 
          :key="cleaner.id" 
          class="cleaner-card"
          @click="selectCleaner(cleaner)"
        >
          <el-avatar :size="60" class="cleaner-avatar">
            {{ cleaner.full_name?.charAt(0) || 'C' }}
          </el-avatar>
          <div class="cleaner-info">
            <div class="cleaner-name">{{ cleaner.full_name }}</div>
            <div class="cleaner-stats">
              <el-rate 
                :model-value="cleaner.star_level" 
                disabled 
                :max="5"
                size="small"
              />
              <span class="orders-count">{{ cleaner.total_orders }} orders</span>
              <span class="rating-score">{{ cleaner.total_rating }} rating</span>
            </div>
          </div>
        </div>
        <el-empty v-if="cleaners.length === 0" description="No cleaners found" />
      </div>
    </el-dialog>

    <!-- Post Requirement Dialog -->
    <el-dialog v-model="showRequirementDialog" title="Post Your Cleaning Requirement" width="600px">
      <el-form :model="requirementForm" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Your Name" required>
              <el-input v-model="requirementForm.guest_name" placeholder="Enter your name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Phone" required>
              <el-input v-model="requirementForm.guest_phone" placeholder="Enter your phone" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Email">
              <el-input v-model="requirementForm.guest_email" placeholder="Enter your email" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Property Type">
              <el-select v-model="requirementForm.property_type" style="width: 100%">
                <el-option label="House" value="House" />
                <el-option label="Apartment" value="Apartment" />
                <el-option label="Villa" value="Villa" />
                <el-option label="Townhouse" value="Townhouse" />
                <el-option label="Studio" value="Studio" />
                <el-option label="Condo" value="Condo" />
                <el-option label="Penthouse" value="Penthouse" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="Bedroom">
              <el-input-number v-model="requirementForm.bedroom" :min="0" :max="10" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Bathroom">
              <el-input-number v-model="requirementForm.bathroom" :min="0" :max="10" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Living Room">
              <el-input-number v-model="requirementForm.living_room" :min="0" :max="10" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="Kitchen">
              <el-input-number v-model="requirementForm.kitchen" :min="0" :max="5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Lawn">
              <el-input-number v-model="requirementForm.lawn" :min="0" :max="5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Car Space">
              <el-input-number v-model="requirementForm.car_space" :min="0" :max="5" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Square Footage">
              <el-input-number v-model="requirementForm.square_footage" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Budget ($)">
              <el-input-number v-model="requirementForm.budget" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Service Type">
              <el-select v-model="requirementForm.service_type_name" style="width: 100%">
                <el-option label="Regular Cleaning" value="Regular Cleaning" />
                <el-option label="Deep Cleaning" value="Deep Cleaning" />
                <el-option label="Move-in Cleaning" value="Move-in Cleaning" />
                <el-option label="Move-out Cleaning" value="Move-out Cleaning" />
                <el-option label="Office Cleaning" value="Office Cleaning" />
                <el-option label="Post-Construction" value="Post-Construction" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Preferred Time">
              <el-select v-model="requirementForm.preferred_time" style="width: 100%">
                <el-option label="Weekday Morning" value="Weekday Morning" />
                <el-option label="Weekday Afternoon" value="Weekday Afternoon" />
                <el-option label="Weekday Evening" value="Weekday Evening" />
                <el-option label="Weekend Morning" value="Weekend Morning" />
                <el-option label="Weekend Afternoon" value="Weekend Afternoon" />
                <el-option label="Weekend Evening" value="Weekend Evening" />
                <el-option label="Flexible" value="Flexible" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Description">
          <el-input v-model="requirementForm.description" type="textarea" rows="3" placeholder="Any special requirements..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRequirementDialog = false">Cancel</el-button>
        <el-button type="primary" :loading="loading" @click="submitRequirement">Submit</el-button>
      </template>
    </el-dialog>

    <!-- Applications Dialog -->
    <el-dialog v-model="showApplyDialog" title="Cleaner Applications" width="700px">
      <!-- Apply Form (when user is applying) -->
      <div v-if="applyForm.requirement_id && isLoggedIn && isCleaner" class="apply-form">
        <h3>Submit Your Application</h3>
        <el-form :model="applyForm" label-width="120px">
          <el-form-item label="Requirement ID">
            <el-input v-model="applyForm.requirement_id" disabled />
          </el-form-item>
          <el-form-item label="Your Name">
            <el-input v-model="applyForm.cleaner_name" disabled />
          </el-form-item>
          <el-form-item label="Offer Price ($)" required>
            <el-input-number v-model="applyForm.offered_price" :min="1" :precision="2" />
          </el-form-item>
          <el-form-item label="Message">
            <el-input v-model="applyForm.message" type="textarea" rows="3" placeholder="Introduce yourself and your experience..." />
          </el-form-item>
        </el-form>
      </div>
      <!-- Applications List (when viewing) -->
      <div v-else>
        <div v-if="applications.length === 0" class="no-applications">
          No applications yet. Be the first to apply!
        </div>
        <div class="applications-list">
          <div v-for="app in applications" :key="app.id" class="application-card">
            <div class="app-cleaner">
              <el-avatar :size="50">{{ app.cleaner_name?.charAt(0) || 'C' }}</el-avatar>
              <div class="app-cleaner-info">
                <div class="name">{{ app.cleaner_name }}</div>
                <div class="stats">
                  <el-rate :model-value="app.star_level || 1" disabled :max="5" size="small" />
                  <span>{{ app.total_orders || 0 }} orders</span>
                  <span>{{ app.total_rating || 5.0 }} rating</span>
                </div>
              </div>
            </div>
            <div class="app-offer">
              <div class="price">${{ app.offered_price }}</div>
              <div class="message">{{ app.message }}</div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showApplyDialog = false; applyForm = { requirement_id: 0, cleaner_id: 0, cleaner_name: '', offered_price: null, message: '' }">Close</el-button>
        <el-button v-if="applyForm.requirement_id && isLoggedIn && isCleaner" type="primary" :loading="loading" @click="submitApplication">Submit Application</el-button>
      </template>
    </el-dialog>

    <!-- Service Detail Dialog -->
    <el-dialog v-model="showServiceDetailDialog" :title="serviceDetail?.type_name || 'Service Details'" width="700px">
      <div v-if="serviceDetail" class="service-detail">
        <div class="service-header">
          <div class="service-price">
            <span class="price">${{ serviceDetail.price }}</span>
            <span class="unit">/ visit</span>
          </div>
          <div class="service-time">
            <el-icon><Clock /></el-icon>
            <span>{{ serviceDetail.standard_time }} minutes</span>
          </div>
        </div>
        
        <div class="service-description">
          <h3>Description</h3>
          <p>{{ serviceDetail.description || 'Professional cleaning service tailored to your needs.' }}</p>
        </div>
        
        <div class="service-features">
          <h3>Service Features</h3>
          <ul>
            <li v-for="(feature, index) in serviceDetail.features" :key="index">
              <el-icon><Check /></el-icon>
              {{ feature }}
            </li>
          </ul>
        </div>
        
        <div class="service-process">
          <h3>Service Process</h3>
          <el-steps :active="5" finish-status="success" align-center>
            <el-step v-for="(step, index) in serviceDetail.process_steps" :key="index" :title="step" />
          </el-steps>
        </div>
        
        <div class="service-precautions">
          <h3>Precautions</h3>
          <ul>
            <li v-for="(precaution, index) in serviceDetail.precautions" :key="index">
              <el-icon><Warning /></el-icon>
              {{ precaution }}
            </li>
          </ul>
        </div>
      </div>
      <template #footer>
        <el-button @click="showServiceDetailDialog = false">Close</el-button>
        <el-button type="primary" @click="handleBookNow(serviceDetail)">Book Now</el-button>
      </template>
    </el-dialog>

    <!-- Order Dialog -->
    <el-dialog v-model="showOrderDialog" title="Book Service" width="500px">
      <el-form :model="orderForm" label-width="100px">
        <el-form-item label="Service Type">
          <el-input :value="selectedService?.type_name" disabled />
        </el-form-item>
        <el-form-item label="Service Price">
          <el-input :value="'$' + selectedService?.price" disabled />
        </el-form-item>
        <el-form-item label="Select Cleaner">
          <div v-if="selectedCleaner" class="selected-cleaner">
            <el-avatar :size="40">{{ selectedCleaner.full_name?.charAt(0) || 'C' }}</el-avatar>
            <div class="cleaner-detail">
              <span class="name">{{ selectedCleaner.full_name }}</span>
              <el-rate :model-value="selectedCleaner.star_level" disabled :max="5" size="small" />
            </div>
            <el-button link type="primary" @click="openCleanerSelection(selectedService)">Change</el-button>
          </div>
          <el-button v-else type="primary" link @click="openCleanerSelection(selectedService)">
            Select a cleaner
          </el-button>
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
          <p>{{ companyInfo.about_us || 'CleanPro is a professional hotel cleaning service platform, committed to providing high-quality cleaning services to our customers.' }}</p>
        </div>
        <div class="footer-section">
          <h4>Contact Us</h4>
          <p>Phone: {{ companyInfo.phone || '400-888-8888' }}</p>
          <p>Email: {{ companyInfo.email || 'service@cleanpro.com' }}</p>
          <p>Address: {{ companyInfo.address || 'Pudong New District, Shanghai' }}</p>
        </div>
        <div class="footer-section">
          <h4>Follow Us</h4>
          <div class="social-links">
            <a v-if="companyInfo.facebook" :href="companyInfo.facebook" target="_blank"><el-icon :size="24"><Link /></el-icon></a>
            <a v-if="companyInfo.twitter" :href="companyInfo.twitter" target="_blank"><el-icon :size="24"><ChatDotRound /></el-icon></a>
            <span v-if="!companyInfo.facebook && !companyInfo.twitter" class="social-placeholder">Coming soon</span>
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
  padding: 60px 24px;
  background: #fff;
}

.categories-section .categories-grid {
  max-width: 1200px;
  margin: 0 auto;
}

.services-section .services-grid {
  max-width: 1200px;
  margin: 0 auto;
}

.testimonials-section .section-title {
  text-align: center;
  margin-bottom: 40px;
}

.testimonials-section h2 {
  font-size: 32px;
  color: #303133;
  margin: 0 0 16px 0;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.my-tasks-section {
  padding: 60px 24px;
  background: #f5f7fa;
  max-width: 1400px;
  margin: 0 auto;
}

.my-tasks-section .section-title {
  text-align: center;
  margin-bottom: 32px;
}

.my-tasks-section h2 {
  font-size: 32px;
  color: #303133;
  margin: 0 0 16px 0;
}

.tasks-tabs {
  max-width: 1200px;
  margin: 0 auto;
  background: #fff;
  border-radius: 12px;
  padding: 24px;
}

.no-tasks {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.task-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
}

.task-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.task-card.completed {
  border-left: 4px solid #67c23a;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.task-time {
  font-size: 12px;
  color: #909399;
}

.task-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.task-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
}

.task-description p {
  margin: 4px 0;
}

.task-price {
  font-size: 20px;
  font-weight: bold;
  color: #ff6b6b;
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

.cleaner-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.cleaner-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.cleaner-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.cleaner-card:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.cleaner-avatar {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
}

.cleaner-info {
  flex: 1;
}

.cleaner-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.cleaner-stats {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.orders-count, .rating-score {
  color: #67c23a;
}

.selected-cleaner {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cleaner-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cleaner-detail .name {
  font-weight: 500;
}

.ad-content h3 {
  font-size: 24px;
  margin-bottom: 8px;
}

.ad-content p {
  font-size: 16px;
  opacity: 0.9;
}

.cleaners-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 24px;
}

.cleaners-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.cleaner-profile-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: all 0.3s;
  cursor: pointer;
}

.cleaner-profile-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(64,158,255,0.15);
}

.profile-avatar {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  margin-bottom: 12px;
}

.profile-name {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.profile-stars {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-bottom: 12px;
}

.star-text {
  font-size: 12px;
  color: #ff9900;
  margin-left: 4px;
}

.profile-stats {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 16px;
}

.profile-stats .stat {
  text-align: center;
}

.profile-stats .stat-num {
  display: block;
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
}

.profile-stats .stat-label {
  font-size: 12px;
  color: #909399;
}

.requirements-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 24px;
  background: #f9f9f9;
}

.requirements-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.requirement-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: all 0.3s;
}

.requirement-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.req-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.req-time {
  font-size: 12px;
  color: #909399;
}

.req-details {
  margin-bottom: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 4px 0;
}

.detail-row .label {
  color: #909399;
}

.detail-row .value {
  font-weight: 500;
  color: #303133;
}

.req-service {
  margin-bottom: 12px;
}

.req-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.req-actions {
  display: flex;
  gap: 8px;
}

.apply-form {
  padding: 10px;
}

.apply-form h3 {
  margin: 0 0 16px 0;
  color: #303133;
}

.budget .price {
  font-size: 20px;
  font-weight: bold;
  color: #ff6b6b;
}

.budget .time {
  font-size: 12px;
  color: #909399;
  display: block;
}

.no-applications {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.applications-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.application-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.app-cleaner {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-cleaner-info .name {
  font-weight: 500;
  margin-bottom: 4px;
}

.app-cleaner-info .stats {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #909399;
}

.app-offer {
  text-align: right;
}

.app-offer .price {
  font-size: 20px;
  font-weight: bold;
  color: #67c23a;
}

.app-offer .message {
  font-size: 12px;
  color: #909399;
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

.testimonial-author .review-service {
  color: #909399;
  font-size: 12px;
  font-weight: 400;
  margin-left: auto;
}

.testimonial-card {
  cursor: pointer;
}

.view-more-reviews {
  text-align: center;
  margin-top: 24px;
}

.review-detail {
  padding: 10px;
}

.review-detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.review-detail-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #303133;
}

.review-detail-stars {
  display: flex;
  align-items: center;
  gap: 8px;
}

.review-detail-stars .rating-value {
  color: #ff9900;
  font-weight: bold;
}

.review-detail-service {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.review-detail-comment h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #606266;
}

.review-detail-comment p {
  margin: 0;
  color: #303133;
  line-height: 1.6;
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
  
  .cleaners-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .requirements-grid {
    grid-template-columns: 1fr;
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

.service-detail {
  padding: 0 10px;
}

.service-detail .service-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.service-detail .service-price .price {
  font-size: 32px;
  font-weight: bold;
  color: #ff6b6b;
}

.service-detail .service-price .unit {
  font-size: 14px;
  color: #909399;
  margin-left: 4px;
}

.service-detail .service-time {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 14px;
}

.service-detail h3 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 12px;
}

.service-detail .service-description {
  margin-bottom: 20px;
}

.service-detail .service-description p {
  color: #606266;
  line-height: 1.6;
}

.service-detail .service-features {
  margin-bottom: 20px;
}

.service-detail .service-features ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.service-detail .service-features li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  color: #606266;
}

.service-detail .service-features li .el-icon {
  color: #67c23a;
}

.service-detail .service-process {
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.service-detail .service-precautions {
  margin-bottom: 10px;
}

.service-detail .service-precautions ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.service-detail .service-precautions li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  color: #e6a23c;
}
</style>
