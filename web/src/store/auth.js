import { create } from 'zustand'

export const useAuthStore = create((set) => ({
  token: null,
  userId: null,
  user: null,

  setAuth: (token, userId, user) => {
    localStorage.setItem('testigo_token', token)
    localStorage.setItem('testigo_user_id', userId)
    set({ token, userId, user })
  },

  logout: () => {
    localStorage.removeItem('testigo_token')
    localStorage.removeItem('testigo_user_id')
    set({ token: null, userId: null, user: null })
  },

  loadToken: () => {
    const token = localStorage.getItem('testigo_token')
    if (token) {
      set({ token })
    }
  }
}))
