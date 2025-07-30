import Cookies from 'js-cookie';
import { authAPI } from './api';

// Auth context and utilities
export const AUTH_COOKIE_OPTIONS = {
  expires: 7, // 7 days
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'strict',
};

export const setAuthTokens = (accessToken, refreshToken) => {
  Cookies.set('access_token', accessToken, { ...AUTH_COOKIE_OPTIONS, expires: 1 }); // 1 day
  Cookies.set('refresh_token', refreshToken, AUTH_COOKIE_OPTIONS);
};

export const clearAuthTokens = () => {
  Cookies.remove('access_token');
  Cookies.remove('refresh_token');
};

export const getAccessToken = () => {
  return Cookies.get('access_token');
};

export const getRefreshToken = () => {
  return Cookies.get('refresh_token');
};

export const isAuthenticated = () => {
  return !!getAccessToken();
};

export const login = async (email, password) => {
  try {
    const response = await authAPI.login({ email, password });
    const { access_token, refresh_token, user } = response.data;
    
    setAuthTokens(access_token, refresh_token);
    
    return { success: true, user };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.error || 'Login failed' 
    };
  }
};

export const register = async (email, password) => {
  try {
    const response = await authAPI.register({ email, password });
    const { access_token, refresh_token, user } = response.data;
    
    setAuthTokens(access_token, refresh_token);
    
    return { success: true, user };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.error || 'Registration failed' 
    };
  }
};

export const logout = async () => {
  try {
    await authAPI.logout();
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    clearAuthTokens();
    window.location.href = '/login';
  }
};

export const getCurrentUser = async () => {
  try {
    if (!isAuthenticated()) {
      return null;
    }
    
    const response = await authAPI.getProfile();
    return response.data.user;
  } catch (error) {
    console.error('Get current user error:', error);
    if (error.response?.status === 401) {
      clearAuthTokens();
    }
    return null;
  }
};

export const updateProfile = async (data) => {
  try {
    const response = await authAPI.updateProfile(data);
    return { success: true, user: response.data.user };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.error || 'Profile update failed' 
    };
  }
};

export const forgotPassword = async (email) => {
  try {
    await authAPI.forgotPassword({ email });
    return { success: true };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.error || 'Password reset request failed' 
    };
  }
};

export const googleAuth = async (token) => {
  try {
    const response = await authAPI.googleAuth({ token });
    const { access_token, refresh_token, user } = response.data;
    
    setAuthTokens(access_token, refresh_token);
    
    return { success: true, user };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.error || 'Google authentication failed' 
    };
  }
};

