// frontend/src/hooks/useAuth.ts
import { useAuth0 } from '@auth0/auth0-react';
import { useCallback, useRef } from 'react';
import { authService } from '../services/authService'

export const useAuth = () => {
    const auth0 = useAuth0();
    // Ref to track if we've already fetched the profile in the current auth session
    const profileFetchedRef = useRef(false);

    const getUserProfile = useCallback(async () => {
        if (!auth0.isAuthenticated) {
            profileFetchedRef.current = false;
            return [];
        } else if (profileFetchedRef.current) {
            return [];
        } else {
            const token = await auth0.getAccessTokenSilently();
            const profile = await authService.getUserProfile(token);
            profileFetchedRef.current = true;
            return profile;
        }
    }, [auth0.isAuthenticated, auth0.isLoading, auth0.getAccessTokenSilently]);

    // // Auto-fetch user profile once when authenticated
    // useEffect(() => {
    //     const fetchProfileOnce = async () => {
    //         // Only fetch if authenticated and we haven't fetched yet
    //         if (auth0.isAuthenticated && !auth0.isLoading && !profileFetchedRef.current) {
    //             profileFetchedRef.current = true;
    //             await getUserProfile();
    //         }
    //     };

    //     fetchProfileOnce();
        
    //     // Reset the flag when user logs out
    //     if (!auth0.isAuthenticated && !auth0.isLoading) {
    //         profileFetchedRef.current = false;
    //     }
    // }, [auth0.isAuthenticated, auth0.isLoading, getUserProfile]);

    return {
        ...auth0, // Spread all standard Auth0 properties
        getUserProfile, // Add your custom function
    };
};
