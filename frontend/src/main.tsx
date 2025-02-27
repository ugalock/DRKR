// frontend/src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './services/queryClient'
import { Auth0Provider, LocalStorageCache } from '@auth0/auth0-react'
import App from './App'
import './index.css'

const AUTH0_DOMAIN = import.meta.env.VITE_AUTH0_DOMAIN
const AUTH0_CLIENT_ID = import.meta.env.VITE_AUTH0_CLIENT_ID
const AUTH0_CALLBACK_URL = import.meta.env.VITE_AUTH0_CALLBACK_URL
const API_URL = import.meta.env.VITE_API_URL

const cache = new LocalStorageCache()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <Auth0Provider
          domain={AUTH0_DOMAIN}
          clientId={AUTH0_CLIENT_ID}
          authorizationParams={{
            redirect_uri: AUTH0_CALLBACK_URL,
            scope: "openid profile email offline_access",
            audience: API_URL,
            prompt: "login",
            display: "popup",
          }}
          useRefreshTokens={true}
          cache={cache}
        >
          <App />
        </Auth0Provider>
      </QueryClientProvider>
    </BrowserRouter>
  </React.StrictMode>
)
