const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

const authenticateToken = (req, res, next) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ 
      error: 'Unauthorized', 
      message: 'No valid token provided' 
    });
  }

  const token = authHeader.substring(7);

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    
    // Add user info to request object
    req.user = {
      username: decoded.username,
      vastHost: decoded.vastHost,
      vastPort: decoded.vastPort,
      tenant: decoded.tenant,
      accessToken: decoded.accessToken,
      refreshToken: decoded.refreshToken
    };

    next();
  } catch (error) {
    console.error('Token verification error:', error.message);
    
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ 
        error: 'Token expired', 
        message: 'Please log in again' 
      });
    } else if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ 
        error: 'Invalid token', 
        message: 'Please log in again' 
      });
    }
    
    return res.status(500).json({ 
      error: 'Token verification failed' 
    });
  }
};

module.exports = authenticateToken;