import client from './client'

export const agentsApi = {
  list(signal) {
    return client.get('/agents', { signal })
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

  login(id, signal) {
    return client.post(`/agents/${id}/login`, null, { signal })
  },

  checkCookie(id, signal) {
    return client.post(`/agents/${id}/check-cookie`, null, { signal })
  },

  checkAllCookies(signal) {
    return client.post('/agents/check-cookies', null, { signal })
  },

  clearData(id) {
    return client.delete(`/agents/${id}/data`)
  },
}
