import { UserProfile } from './user'

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  refresh_token?: string
}

export interface AuthState {
  isAuthenticated: boolean
  isLoading: boolean
  user: UserProfile | null
  error: string | null
} 