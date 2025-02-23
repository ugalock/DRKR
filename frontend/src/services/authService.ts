import axios from 'axios'
import { TokenResponse } from '../types/auth'
import { UserProfile } from '../types/user'

const AUTH0_DOMAIN = import.meta.env.VITE_AUTH0_DOMAIN
const AUTH0_CLIENT_ID = import.meta.env.VITE_AUTH0_CLIENT_ID
const AUTH0_CALLBACK_URL = import.meta.env.VITE_AUTH0_CALLBACK_URL

export const authService = {
  // Initialize Auth0 login
  loginWithProvider: (provider: 'google' | 'github') => {
    const params = new URLSearchParams({
      client_id: AUTH0_CLIENT_ID,
      redirect_uri: AUTH0_CALLBACK_URL,
      response_type: 'code',
      scope: 'openid profile email offline_access',
      connection: provider,
    })
    
    window.location.href = `https://${AUTH0_DOMAIN}/authorize?${params.toString()}`
  },

  // Handle OAuth callback
  handleCallback: async (code: string): Promise<TokenResponse> => {
    const response = await axios.post<TokenResponse>('/api/callback', { code })
    return response.data
  },

  // Get user profile from backend
  getUserProfile: async (token: string): Promise<UserProfile> => {
    const response = await axios.get<UserProfile>('/api/users/me', {
      headers: { Authorization: `Bearer ${token}` }
    })
    return response.data
  },

  // Refresh token
  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await axios.post<TokenResponse>('/api/auth/refresh', {
      refresh_token: refreshToken
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
