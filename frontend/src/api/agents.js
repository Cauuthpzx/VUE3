import client from './client'

export const agentsApi = {
  list() {
    return client.get('/agents')
  },

  create(data) {
    return client.post('/agents', data)
  },

  update(id, data) {
    return client.patch(`/agents/${id}`, data)
  },

  delete(id) {
    return client.delete(`/agents/${id}`)
  },

  login(id) {
    return client.post(`/agents/${id}/login`)
  },

  checkCookie(id) {
    return client.post(`/agents/${id}/check-cookie`)
  },

  clearData(id) {
    return client.delete(`/agents/${id}/data`)
  },
}
