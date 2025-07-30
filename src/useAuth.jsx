import { useState, useEffect, createContext, useContext } from 'react';
import { getCurrentUser, isAuthenticated } from '../lib/auth';

// Create Auth Context
const AuthContext = createContext();

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      try {
        if (isAuthenticated()) {
          const currentUser = await getCurrentUser();
          if (currentUser) {
            setUser(currentUser);
            setIsLoggedIn(true);
          } else {
            setIsLoggedIn(false);
          }
        } else {
          setIsLoggedIn(false);
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        setIsLoggedIn(false);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const updateUser = (userData) => {
    setUser(userData);
    setIsLoggedIn(!!userData);
  };

  const clearUser = () => {
    setUser(null);
    setIsLoggedIn(false);
  };

  const value = {
    user,
    loading,
    isLoggedIn,
    updateUser,
    clearUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Hook for protected routes
export const useRequireAuth = () => {
  const { isLoggedIn, loading } = useAuth();
  
  useEffect(() => {
    if (!loading && !isLoggedIn) {
      window.location.href = '/login';
    }
  }, [isLoggedIn, loading]);

  return { isLoggedIn, loading };
};

