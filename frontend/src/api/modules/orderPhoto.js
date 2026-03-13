import request from '../request'

export const orderPhotoApi = {
  getByOrder: (orderId) => request.get(`/order-photo/order/${orderId}`),
  create: (data) => request.post('/order-photo/', data),
  reorder: (data) => request.post('/order-photo/reorder', data),
  delete: (photoId) => request.delete(`/order-photo/${photoId}`)
}