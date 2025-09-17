const axios = require('axios');

class VastService {
  constructor() {
    this.clients = new Map(); // Cache authenticated clients
  }

  createClient(host, port, skipSSLVerify = true) {
    const baseURL = `https://${host}:${port}/api`;
    
    return axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      httpsAgent: skipSSLVerify ? new (require('https').Agent)({
        rejectUnauthorized: false
      }) : undefined
    });
  }

  async authenticate({ host, port, username, password, tenant = 'default' }) {
    try {
      const client = this.createClient(host, port);
      
      // Use the token endpoint from the swagger spec
      const tokenEndpoint = tenant === 'default' ? '/token/' : `/token/${tenant}`;
      
      const response = await client.post(tokenEndpoint, {
        username,
        password
      });

      if (response.data.access) {
        const clientKey = `${host}:${port}:${tenant}`;
        
        // Store authenticated client
        const authClient = this.createClient(host, port);
        authClient.defaults.headers['Authorization'] = `Bearer ${response.data.access}`;
        
        this.clients.set(clientKey, {
          client: authClient,
          accessToken: response.data.access,
          refreshToken: response.data.refresh,
          username,
          tenant,
          createdAt: Date.now()
        });

        return {
          success: true,
          accessToken: response.data.access,
          refreshToken: response.data.refresh
        };
      }

      return {
        success: false,
        message: 'Invalid response format'
      };

    } catch (error) {
      console.error('VAST authentication error:', error.message);
      
      if (error.response) {
        const status = error.response.status;
        const message = error.response.data?.message || error.response.statusText;
        
        if (status === 401) {
          return { success: false, message: 'Invalid credentials' };
        } else if (status === 404) {
          return { success: false, message: 'VAST API endpoint not found' };
        } else {
          return { success: false, message: `Authentication failed: ${message}` };
        }
      } else if (error.code === 'ECONNREFUSED') {
        return { success: false, message: 'Cannot connect to VAST server' };
      } else if (error.code === 'ENOTFOUND') {
        return { success: false, message: 'VAST server not found' };
      }

      return {
        success: false,
        message: error.message || 'Authentication failed'
      };
    }
  }

  async verifyToken(accessToken, { host, port }) {
    try {
      const client = this.createClient(host, port);
      client.defaults.headers['Authorization'] = `Bearer ${accessToken}`;
      
      // Try to make a simple API call to verify token
      await client.get('/tenants/configured_idp/');
      return true;
    } catch (error) {
      console.error('Token verification failed:', error.message);
      return false;
    }
  }

  getAuthenticatedClient(host, port, tenant = 'default') {
    const clientKey = `${host}:${port}:${tenant}`;
    const cached = this.clients.get(clientKey);
    
    if (!cached) {
      throw new Error('No authenticated session found');
    }

    // Check if token is too old (8 hours)
    const ageHours = (Date.now() - cached.createdAt) / (1000 * 60 * 60);
    if (ageHours > 8) {
      this.clients.delete(clientKey);
      throw new Error('Session expired');
    }

    return cached.client;
  }

  async getTenants(host, port, tenant = 'default') {
    try {
      const client = this.getAuthenticatedClient(host, port, tenant);
      const response = await client.get('/tenants/');
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Get tenants error:', error.message);
      return { success: false, message: error.message };
    }
  }

  async getVipPools(host, port, tenant = 'default') {
    try {
      const client = this.getAuthenticatedClient(host, port, tenant);
      const response = await client.get('/vippools/');
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Get VIP pools error:', error.message);
      return { success: false, message: error.message };
    }
  }

  async createView(host, port, tenant, viewData) {
    try {
      const client = this.getAuthenticatedClient(host, port, tenant);
      const response = await client.post('/views/', viewData);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Create view error:', error.message);
      return { 
        success: false, 
        message: error.response?.data?.message || error.message 
      };
    }
  }

  async getViews(host, port, tenant = 'default') {
    try {
      const client = this.getAuthenticatedClient(host, port, tenant);
      const response = await client.get('/views/');
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Get views error:', error.message);
      return { success: false, message: error.message };
    }
  }

  // Clean up expired sessions
  cleanupSessions() {
    const now = Date.now();
    for (const [key, session] of this.clients.entries()) {
      const ageHours = (now - session.createdAt) / (1000 * 60 * 60);
      if (ageHours > 8) {
        this.clients.delete(key);
      }
    }
  }
}

// Cleanup expired sessions every hour
setInterval(() => {
  vastService.cleanupSessions();
}, 60 * 60 * 1000);

const vastService = new VastService();
module.exports = vastService;