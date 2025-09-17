import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('vast_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const { response } = error;

    if (response) {
      const { status, data } = response;
      
      // Handle authentication errors
      if (status === 401) {
        localStorage.removeItem('vast_token');
        if (!window.location.pathname.includes('/login')) {
          toast.error('Session expired. Please log in again.');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }

      // Handle other HTTP errors
      const message = data?.message || data?.error || `HTTP ${status} Error`;
      
      if (status >= 500) {
        toast.error(`Server error: ${message}`);
      } else if (status >= 400) {
        // Don't show toast for validation errors, let components handle them
        console.warn(`Client error: ${message}`);
      }
    } else if (error.code === 'NETWORK_ERROR' || error.code === 'ECONNABORTED') {
      toast.error('Network error. Please check your connection.');
    } else {
      toast.error('An unexpected error occurred.');
    }

    return Promise.reject(error);
  }
);

export default apiClient;