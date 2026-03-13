import request from '../request'

export const serviceTypeApi = {
  list: () => request.get('/service-type/'),
  get: (typeId) => request.get(`/service-type/${typeId}`),
  create: (data) => request.post('/service-type/', data),
  update: (typeId, data) => request.put(`/service-type/${typeId}`, data),
  delete: (typeId) => request.delete(`/service-type/${typeId}`)
}