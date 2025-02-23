import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService } from '../services/authService'
import { AuthState } from '../types/auth'

interface AuthContextType extends AuthState {
  loginWithProvider: (provider: 'google' | 'github') => void
  logout: () => void
  refreshUserProfile: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    user: null,
    error: null
  })

  const updateAuthState = (updates: Partial<AuthState>) => {
    setAuthState(current => ({ ...current, ...updates }))
  }

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      const token = authService.getStoredToken()
      if (!token) {
        updateAuthState({ isLoading: false })
        return
      }

      try {
        const user = await authService.getUserProfile(token)
        updateAuthState({
          isAuthenticated: true,
          user,
          isLoading: false
        })
      } catch (error) {
        // Try to refresh token if available
        const refreshToken = authService.getStoredRefreshToken()
        if (refreshToken) {
          try {
            const tokens = await authService.refreshToken(refreshToken)
            authService.storeTokens(tokens)
            const user = await authService.getUserProfile(tokens.access_token)
            updateAuthState({
              isAuthenticated: true,
              user,
              isLoading: false
            })
          } catch (refreshError) {
            authService.removeTokens()
            updateAuthState({
              isAuthenticated: false,
              user: null,
              error: 'Session expired',
              isLoading: false
            })
          }
        } else {
          authService.removeTokens()
          updateAuthState({
            isAuthenticated: false,
            user: null,
            error: 'Session expired',
            isLoading: false
          })
        }
      }
    }

    initAuth()
  }, [])

  const loginWithProvider = (provider: 'google' | 'github') => {
    authService.loginWithProvider(provider)
  }

  const logout = () => {
    authService.removeTokens()
    updateAuthState({
      isAuthenticated: false,
      user: null,
      error: null
    })
  }

  const refreshUserProfile = async () => {
    const token = authService.getStoredToken()
    if (!token) return

    try {
      const user = await authService.getUserProfile(token)
      updateAuthState({ user })
    } catch (error) {
      console.error('Failed to refresh user profile:', error)
    }
  }

  return (
    <AuthContext.Provider 
      value={{ 
        ...authState,
        loginWithProvider,
        logout,
        refreshUserProfile
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
