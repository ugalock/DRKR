import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { UserProfile } from '../../types/user'

interface PrivateRouteProps {
  children: React.ReactNode
  requiredRoles?: Array<UserProfile['default_role']>
  requiredOrgRoles?: Array<NonNullable<UserProfile['org_memberships'][number]['role']>>
}

export const PrivateRoute = ({ 
  children, 
  requiredRoles = [], 
  requiredOrgRoles = [] 
}: PrivateRouteProps) => {
  const { isAuthenticated, user } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    // Redirect to login page with return url
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Check for required global roles
  if (requiredRoles.length > 0 && !requiredRoles.includes(user?.default_role ?? 'user')) {
    return <Navigate to="/unauthorized" replace />
  }

  // Check for required organization roles
  // TODO: Organization auth checks need to be specific to the organization
  if (requiredOrgRoles.length > 0 && 
      (!user?.org_memberships || !requiredOrgRoles.includes(user.org_memberships[0].role))) {
    return <Navigate to="/unauthorized" replace />
  }

  return <>{children}</>
} 