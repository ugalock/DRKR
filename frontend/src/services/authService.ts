import axios from 'axios'
import { TokenResponse } from '../types/auth'
import { User } from '../types/user'

export const authService = {
  // Get user profile from backend
  getUserProfile: async (token: string): Promise<User> => {
    const response = await axios.get<User>('/api/users/me', {
      headers: { Authorization: `Bearer ${token}` }
    })
    return response.data
  },

  // Token storage
  getStoredToken: (): string | null => {
    return localStorage.getItem('access_token')
  },

  getStoredRefreshToken: (): string | null => {
    return localStorage.getItem('refresh_token')
  },

  storeTokens: (tokens: TokenResponse): void => {
    localStorage.setItem('access_token', tokens.access_token)
    if (tokens.refresh_token) {
      localStorage.setItem('refresh_token', tokens.refresh_token)
    }
  },

  removeTokens: (): void => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }
}
