import { Routes, Route } from 'react-router-dom'
import { PrivateRoute } from '../components/common/PrivateRoute'

// Pages
import { HomePage } from '../pages/Home/HomePage'
import { LoginPage } from '../pages/Auth/LoginPage'
import { ResearchList } from '../pages/Research/ResearchList'
import { ResearchDetail } from '../pages/Research/ResearchDetail'
import { TagsPage } from '../pages/Tags/TagsPage'
import { OrganizationPage } from '../pages/Organization/OrganizationPage'
import { NotFoundPage } from '../pages/NotFoundPage'
import { UnauthorizedPage } from '../pages/UnauthorizedPage'

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/unauthorized" element={<UnauthorizedPage />} />

      {/* Protected Routes */}
      <Route
        path="/research"
        element={
          <PrivateRoute>
            <ResearchList />
          </PrivateRoute>
        }
      />
      <Route
        path="/research/:id"
        element={
          <PrivateRoute>
            <ResearchDetail />
          </PrivateRoute>
        }
      />
      <Route
        path="/tags"
        element={
          <PrivateRoute>
            <TagsPage />
          </PrivateRoute>
        }
      />
      <Route
        path="/organization"
        element={
          <PrivateRoute 
            requiredRoles={['admin', 'owner']} 
            requiredOrgRoles={['admin', 'owner']}
          >
            <OrganizationPage />
          </PrivateRoute>
        }
      />

      {/* 404 Route */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
