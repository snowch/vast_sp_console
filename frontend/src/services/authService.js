import { apiClient } from './apiClient';

class AuthService {
  async login(credentials) {
    try {
      const response = await apiClient.post('/auth/login', credentials);
      return {
        success: true,
        token: response.data.token,
        user: response.data.user
      };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || 'Login failed'
      };
    }
  }

  async logout() {
    try {
      await apiClient.post('/auth/logout');
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      return { success: false };
    }
  }

  async verifyToken() {
    try {
      const response = await apiClient.get('/auth/verify');
      return {
        success: true,
        user: response.data.user
      };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || 'Token verification failed'
      };
    }
  }

  getToken() {
    return localStorage.getItem('vast_token');
  }

  isAuthenticated() {
    const token = this.getToken();
    return !!token;
  }
}

export const authService = new AuthService();