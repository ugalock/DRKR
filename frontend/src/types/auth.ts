import { Auth0ContextInterface } from '@auth0/auth0-react'
import { UserProfile } from './user'

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  refresh_token?: string
}

export interface AuthState extends Auth0ContextInterface {
  getUserProfile: (token: string) => Promise<UserProfile>
} 