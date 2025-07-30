import axios from 'axios';
import Cookies from 'js-cookie';

// Base URL for API calls
const BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://zeropapel.com.br/api' 
  : 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = Cookies.get('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${BASE_URL}/auth/refresh`, {}, {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
            },
          });

          const { access_token } = response.data;
          Cookies.set('access_token', access_token, { expires: 1 }); // 1 day

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data) => api.put('/auth/profile', data),
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  googleAuth: (data) => api.post('/auth/google-auth', data),
};

// Documents API
export const documentsAPI = {
  getDocuments: (params) => api.get('/documents', { params }),
  getDocument: (id) => api.get(`/documents/${id}`),
  uploadDocument: (formData) => api.post('/documents', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  deleteDocument: (id) => api.delete(`/documents/${id}`),
  downloadDocument: (id) => api.get(`/documents/${id}/download`, {
    responseType: 'blob',
  }),
  previewDocument: (id) => api.get(`/documents/${id}/preview`, {
    responseType: 'blob',
  }),
  addDocumentFields: (id, data) => api.post(`/documents/${id}/fields`, data),
};

// Signatures API
export const signaturesAPI = {
  createSignatureRequest: (documentId, data) => 
    api.post(`/documents/${documentId}/signature-requests`, data),
  getSignatureRequest: (id) => api.get(`/signature-requests/${id}`),
  signDocument: (requestId, data) => api.post(`/signature-requests/${requestId}/sign`, data),
  getDocumentSignatureRequests: (documentId) => 
    api.get(`/documents/${documentId}/signature-requests`),
  resendSignatureRequest: (requestId) => 
    api.post(`/signature-requests/${requestId}/resend`),
  cancelSignatureRequest: (requestId) => 
    api.post(`/signature-requests/${requestId}/cancel`),
  verifyDocument: (documentId) => api.get(`/documents/${documentId}/verify`),
};

// Audit API
export const auditAPI = {
  getAuditLogs: (params) => api.get('/audit/logs', { params }),
  getAuditLog: (id) => api.get(`/audit/logs/${id}`),
  getAuditStats: (params) => api.get('/audit/stats', { params }),
  exportAuditLogs: (params) => api.get('/audit/export', { 
    params,
    responseType: 'blob',
  }),
  getDocumentTimeline: (documentId) => 
    api.get(`/audit/document/${documentId}/timeline`),
  performIntegrityCheck: (data) => api.post('/audit/integrity-check', data),
};

// Users API (for admin)
export const usersAPI = {
  getUsers: (params) => api.get('/users', { params }),
  getUser: (id) => api.get(`/users/${id}`),
  createUser: (data) => api.post('/users', data),
  updateUser: (id, data) => api.put(`/users/${id}`, data),
  deleteUser: (id) => api.delete(`/users/${id}`),
};

export default api;

