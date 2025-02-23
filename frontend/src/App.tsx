import { Routes, Route, Link } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { AppRoutes } from './routes'

const App = () => {
  const { isAuthenticated, isLoading, user } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="text-xl font-bold text-gray-900">
                DRKR
              </Link>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link
                  to="/research"
                  className="text-gray-900 hover:text-gray-500 px-3 py-2 rounded-md"
                >
                  Research
                </Link>
                <Link
                  to="/tags"
                  className="text-gray-900 hover:text-gray-500 px-3 py-2 rounded-md"
                >
                  Tags
                </Link>
              </div>
            </div>
            <div className="flex items-center">
              {isAuthenticated ? (
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    {user?.picture_url && (
                      <img 
                        src={user.picture_url} 
                        alt={user.display_name || user.email}
                        className="h-8 w-8 rounded-full"
                      />
                    )}
                    <span className="text-sm text-gray-700">
                      {user?.display_name || user?.email}
                    </span>
                  </div>
                  <Link
                    to="/profile"
                    className="text-gray-900 hover:text-gray-500 px-3 py-2 rounded-md"
                  >
                    Profile
                  </Link>
                </div>
              ) : (
                <Link
                  to="/login"
                  className="text-gray-900 hover:text-gray-500 px-3 py-2 rounded-md"
                >
                  Login
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <AppRoutes />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            © {new Date().getFullYear()} DRKR. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
