// frontend/src/App.tsx
import { useEffect, useRef, useState } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { useApi } from './hooks/useApi';
import { useAuth } from './hooks/useAuth';
import { HomePage } from './pages/Home';
import ResearchJobsPage from './pages/Research/jobs';
import CreateResearchJobPage from './pages/Research/create';
import ResearchDetailPage from './pages/Research/detail';
import ResearchEntriesPage from './pages/Research/entries';
import OrganizationListPage from './pages/Organization/list';
import OrganizationDetailPage from './pages/Organization/detail';
import InviteAcceptPage from './pages/Organization/invite';
import Footer from './components/common/Footer';

// Create a separate component for the authenticated routes to use useNavigate
const AuthenticatedApp = () => {
  const { isAuthenticated, getIdTokenClaims, logout } = useAuth();
  const { api } = useApi();
  const navigate = useNavigate();
  const location = useLocation();

  const profileFetchedRef = useRef(false);
  const isFetchingRef = useRef(false);
  
  useEffect(() => {
    const handleAuth = async () => {
      if (isAuthenticated && !profileFetchedRef.current && !isFetchingRef.current) {
        try {
          isFetchingRef.current = true;
          const idToken = await getIdTokenClaims();
          await api.get('/api/users/me/' + idToken?.__raw);
          profileFetchedRef.current = true;
          
          // Only navigate to /home if we're at the root path
          if (location.pathname === '/') {
            navigate('/home');
          }
        } catch (error) {
          logout();
        } finally {
          isFetchingRef.current = false;
        }
      } else if (!isAuthenticated && profileFetchedRef.current) {
        profileFetchedRef.current = false;
      }
    };
    
    handleAuth();
  }, [isAuthenticated, api, getIdTokenClaims, navigate]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/home" element={<HomePage />} />
        <Route path="/research/jobs" element={<ResearchJobsPage />} />
        <Route path="/research/create-job" element={<CreateResearchJobPage />} />
        <Route path="/research/entries" element={<ResearchEntriesPage />} />
        <Route path="/research/:id" element={<ResearchDetailPage />} />
        <Route path="/organizations" element={<OrganizationListPage />} />
        <Route path="/organizations/:id" element={<OrganizationDetailPage />} />
        <Route path="/invites/:token/accept" element={<InviteAcceptPage />} />
        <Route path="*" element={<Navigate to="/home" replace />} />
      </Routes>
    </div>
  );
};

const App = () => {
  const { loginWithRedirect, isAuthenticated, isLoading } = useAuth();
  const [isRedirecting, setIsRedirecting] = useState(false);

  useEffect(() => {
    const handleAuth = async () => {
      if (!isLoading && !isAuthenticated) {
        setIsRedirecting(true);
        await loginWithRedirect();
        setIsRedirecting(false);
      }
    };
    handleAuth();
  }, [isLoading, isAuthenticated]);

  if (isLoading || isRedirecting) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900" />
        <Footer />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <button 
          onClick={() => loginWithRedirect()}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Login
        </button>
        <Footer />
      </div>
    );
  }

  return (
    <AuthenticatedApp />
  );
};

export default App;
