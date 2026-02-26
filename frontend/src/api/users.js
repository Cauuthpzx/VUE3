import client from './client'

export const usersApi = {
  list(params = {}) {
    return client.get('/users/', { params })
  },
  get(id) {
    return client.get(`/users/${id}`)
  },
  update(id, data) {
    return client.patch(`/users/${id}`, data)
  },
  delete(id) {
    return client.delete(`/users/${id}`)
  },
}
