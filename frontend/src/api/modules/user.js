import request from '../request'

export const userApi = {
  list: () => request.get('/user/'),
  get: (id) => request.get(`/user/${id}`),
  create: (data) => request.post('/user/', data),
  update: (id, data) => request.put(`/user/${id}`, data),
  delete: (id) => request.delete(`/user/${id}`),
  getByRole: (role) => request.get(`/user/role/${role}`)
}