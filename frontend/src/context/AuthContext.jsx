// =================================================================
// FILE: frontend/src/context/AuthContext.jsx (SECURE VERSION)
// =================================================================
import { createContext, useState, useContext, useMemo, useEffect } from 'react';
import axiosInstance from '../api/axiosInstance';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Initialize user state to null. No more localStorage!
  const [user, setUser] = useState(null);
  // Add a loading state to prevent UI flashes before session is checked
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // This function will check if a user session exists on the backend.
    const checkUserSession = async () => {
      try {
        // We make a request to get the CSRF token first. This ensures the
        // csrf_token cookie is set before we make any state-changing requests.
        // The backend sends it with HttpOnly=False so JS can't read it, but the browser
        // will store it and our axios interceptor will handle the rest.
        await axiosInstance.get('/api/csrf-token');

        // Now, check if the user is actually logged in.
        // The '/api/user/profile' endpoint is protected. If the user has a valid
        // session cookie, this request will succeed and return user data.
        // If not, it will fail with a 401 Unauthorized error.
        const response = await axiosInstance.get('/api/user/profile');

        // If the request was successful, we have a logged-in user.
        setUser(response.data);
      } catch (error) {
        // A 401 error is expected if the user is not logged in.
        // We can safely ignore it and the user state will remain null.
        if (error.response && error.response.status !== 401) {
          console.error("An unexpected error occurred while checking user session:", error);
        }
      } finally {
        // The session check is complete, so we can stop loading.
        setLoading(false);
      }
    };

    checkUserSession();
  }, []); // The empty dependency array ensures this runs only once on mount.

  const login = async (email, password) => {
    // On login, the backend sets the session cookie.
    const response = await axiosInstance.post('/api/login', { email, password });
    // We update the user state with the data from the server.
    setUser(response.data.user);
    return response.data;
  };

  const logout = async () => {
    try {
      // Tell the backend to destroy the session.
      await axiosInstance.post('/api/logout');
    } catch (error) {
      console.error("Server logout failed, but logging out client-side anyway.", error);
    } finally {
      // Always clear the user state on the client.
      setUser(null);
    }
  };

  const updateUser = (newUserData) => {
    // This function is used to update the user state after a profile update.
    setUser(newUserData);
  };

  // useMemo ensures the context value object is not recreated on every render.
  const value = useMemo(() => ({ user, login, logout, updateUser, loading }), [user, loading]);

  // We don't render the children until the initial session check is complete.
  // This prevents showing a logged-out state flicker to a logged-in user.
  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}