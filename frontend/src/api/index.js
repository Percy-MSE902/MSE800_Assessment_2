import request from './request'

export { request }

export const authApi = {
  login: (data) => request.post('/api/auth/login', data, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

export const userApi = {
  list: () => request.get('/api/user/'),
  get: (id) => request.get(`/api/user/${id}`),
  create: (data) => request.post('/api/user/', data),
  update: (id, data) => request.put(`/api/user/${id}`, data),
  delete: (id) => request.delete(`/api/user/${id}`),
  getByRole: (role) => request.get(`/api/user/role/${role}`)
}

export const roomApi = {
  list: () => request.get('/api/room/'),
  get: (id) => request.get(`/api/room/${id}`),
  create: (data) => request.post('/api/room/', data),
  update: (id, data) => request.put(`/api/room/${id}`, data),
  delete: (id) => request.delete(`/api/room/${id}`),
  getAvailable: () => request.get('/api/room/available/list'),
  updateStatus: (id, status) => request.put(`/api/room/${id}/status`, null, { params: { status } }),
  paginated: (params) => request.post('/api/room/paginated', params)
}

export const serviceOrderApi = {
  list: () => request.get('/api/service-order/'),
  get: (id) => request.get(`/api/service-order/${id}`),
  create: (data) => request.post('/api/service-order/', data),
  update: (id, data) => request.put(`/api/service-order/${id}`, data),
  delete: (id) => request.delete(`/api/service-order/${id}`),
  assign: (orderId, staffId) => request.post(`/api/service-order/assign/${orderId}`, null, { params: { staff_id: staffId } }),
  start: (orderId) => request.post(`/api/service-order/start/${orderId}`),
  complete: (orderId) => request.post(`/api/service-order/complete/${orderId}`),
  cancel: (orderId, reason) => request.post(`/api/service-order/cancel/${orderId}`, { reason }),
  rate: (orderId, rating, comment) => request.post(`/api/service-order/rate/${orderId}`, { rating, comment }, {
    headers: { 'Content-Type': 'application/json' }
  }),
  paginated: (params) => request.post('/api/service-order/paginated', params)
}

export const inventoryApi = {
  list: () => request.get('/api/inventory/'),
  get: (id) => request.get(`/api/inventory/${id}`),
  create: (data) => request.post('/api/inventory/', data),
  update: (id, data) => request.put(`/api/inventory/${id}`, data),
  delete: (id) => request.delete(`/api/inventory/${id}`),
  restock: (id, quantity) => request.post(`/api/inventory/restock/${id}`, null, { params: { quantity } }),
  getLowStock: () => request.get('/api/inventory/low-stock/list'),
  paginated: (params) => request.post('/api/inventory/paginated', params)
}

export const walletApi = {
  get: () => request.get('/api/wallet/'),
  recharge: (data) => request.post('/api/wallet/recharge', data),
  transactions: () => request.get('/api/wallet/transactions'),
  pay: (orderId) => request.post(`/api/wallet/pay/${orderId}`),
  settle: (orderId) => request.post(`/api/wallet/settle/${orderId}`),
  getCleanerEarnings: () => request.get('/api/wallet/cleaner-earnings')
}

export const serviceTypeApi = {
  list: () => request.get('/api/service-type/'),
  get: (id) => request.get(`/api/service-type/${id}`),
  create: (data) => request.post('/api/service-type/', data),
  update: (id, data) => request.put(`/api/service-type/${id}`, data),
  delete: (id) => request.delete(`/api/service-type/${id}`)
}

export const orderPhotoApi = {
  getByOrder: (orderId) => request.get(`/api/order-photo/order/${orderId}`),
  create: (data) => request.post('/api/order-photo/', data),
  delete: (photoId) => request.delete(`/api/order-photo/${photoId}`),
  reorder: (photoIds) => request.post('/api/order-photo/reorder', { photo_ids: photoIds })
}

export const notificationApi = {
  list: (params) => request.get('/api/notification/paginated', { params }),
  getUnreadCount: () => request.get('/api/notification/unread-count'),
  markAsRead: (id) => request.post(`/api/notification/${id}/read`),
  markAllAsRead: () => request.post('/api/notification/read-all'),
  delete: (id) => request.delete(`/api/notification/${id}`),
}

export const portalApi = {
  getServices: () => request.get('/api/portal/services'),
  getRooms: () => request.get('/api/portal/rooms'),
  createOrder: (data) => request.post('/api/portal/order', data),
  getOrders: (phone) => request.get(`/api/portal/orders/${phone}`),
  getStats: () => request.get('/api/portal/stats'),
}
