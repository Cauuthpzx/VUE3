import client from './client'

export const authApi = {
  login(credentials) {
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    return client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },

  register(data) {
    return client.post('/auth/register', data)
  },

  refresh() {
    return client.post('/auth/refresh')
  },

  logout() {
    return client.post('/auth/logout')
  },

  me() {
    return client.get('/users/me')
  },
}
