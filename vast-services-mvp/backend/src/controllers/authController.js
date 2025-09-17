const jwt = require('jsonwebtoken');
const vastService = require('../services/vastService');

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '8h';

class AuthController {
  async login(req, res, next) {
    try {
      const { vastHost, vastPort, username, password, tenant = 'default' } = req.body;

      // Authenticate with VAST API
      const authResult = await vastService.authenticate({
        host: vastHost,
        port: vastPort,
        username,
        password,
        tenant
      });

      if (!authResult.success) {
        return res.status(401).json({ 
          error: 'Authentication failed', 
          message: authResult.message 
        });
      }

      // Create JWT token with VAST credentials
      const tokenPayload = {
        username,
        vastHost,
        vastPort,
        tenant,
        accessToken: authResult.accessToken,
        refreshToken: authResult.refreshToken
      };

      const token = jwt.sign(tokenPayload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });

      res.json({
        success: true,
        token,
        user: {
          username,
          vastHost,
          vastPort,
          tenant
        }
      });

    } catch (error) {
      console.error('Login error:', error);
      next(error);
    }
  }

  async logout(req, res) {
    // In a real implementation, you might invalidate the token
    res.json({ success: true, message: 'Logged out successfully' });
  }

  async verifyToken(req, res, next) {
    try {
      const authHeader = req.headers.authorization;
      
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'No token provided' });
      }

      const token = authHeader.substring(7);
      const decoded = jwt.verify(token, JWT_SECRET);

      // Optionally verify token is still valid with VAST
      const isValid = await vastService.verifyToken(decoded.accessToken, {
        host: decoded.vastHost,
        port: decoded.vastPort
      });

      if (!isValid) {
        return res.status(401).json({ error: 'Token expired or invalid' });
      }

      res.json({
        valid: true,
        user: {
          username: decoded.username,
          vastHost: decoded.vastHost,
          vastPort: decoded.vastPort,
          tenant: decoded.tenant
        }
      });

    } catch (error) {
      console.error('Token verification error:', error);
      if (error.name === 'JsonWebTokenError' || error.name === 'TokenExpiredError') {
        return res.status(401).json({ error: 'Invalid or expired token' });
      }
      next(error);
    }
  }
}

module.exports = new AuthController();