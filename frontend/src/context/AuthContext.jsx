// =================================================================
// FILE: AuthContext.jsx (FULL, PERSISTENT, AND OPTIMIZED VERSION)
// PURPOSE: Manages global user authentication state.
// =================================================================

import { createContext, useState, useContext, useMemo, useEffect } from 'react';

// 1. Create the context itself
const AuthContext = createContext(null);

// 2. Create the Provider component
export function AuthProvider({ children }) {
  // Initialize state by trying to read from localStorage first
  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem('user');
    try {
      // If a user is found in localStorage, parse it from JSON text to an object
      return storedUser ? JSON.parse(storedUser) : null;
    } catch (error) {
      console.error("Failed to parse user from localStorage", error);
      // If parsing fails (e.g., corrupted data), return null
      return null;
    }
  });

  // This useEffect hook synchronizes the 'user' state with localStorage
  useEffect(() => {
    if (user) {
      // When user logs in, save their data to localStorage as a JSON string
      localStorage.setItem('user', JSON.stringify(user));
    } else {
      // When user logs out, remove their data from localStorage
      localStorage.removeItem('user');
    }
  }, [user]); // This effect runs every time the 'user' state changes

  // Function to update the user state upon successful login
  const login = (userData) => {
    setUser(userData);
  };

  // Function to log the user out, now calling our dedicated API endpoint
  const logout = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/logout', {
        method: 'POST', // Use POST for actions that change server state
        headers: {
          'Content-Type': 'application/json',
        },
      }); 

      if (!response.ok) {
        throw new Error('Server logout failed');
      }

      const data = await response.json();
      console.log('Server logout response:', data.message);

    } catch (error) {
      console.error("Error during server logout:", error);
    } finally {
      // Crucially, we always clear the user state in the frontend,
      // even if the server call fails.
      setUser(null);
    }
  };

  // useMemo ensures that the 'value' object is not recreated on every render,
  // preventing unnecessary re-renders of consuming components.
  // It will only be recreated if the 'user' state changes.
  const value = useMemo(
    () => ({
      user,
      login,
      logout,
    }),
    [user]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// 3. Create a custom hook for easy access to the context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}