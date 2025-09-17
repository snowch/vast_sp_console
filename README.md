# VAST Services MVP

A modern web application for managing VAST Data Platform services with a focus on database schema management and cloud service orchestration.

## Overview

VAST Services MVP provides an intuitive interface for managing VAST Data Platform resources through a React frontend and Node.js backend. The application enables direct authentication with VAST clusters and offers streamlined management of database schemas, with plans to expand to additional cloud services.

## Features

### Current Features
- **Secure VAST Authentication** - Direct JWT-based authentication with VAST clusters
- **Database Schema Management** - Create and manage database schemas via VAST Views
- **Multi-Protocol Support** - Configure views with DATABASE, S3, NFS, and SMB protocols  
- **Real-time Integration** - Live communication with VAST APIs
- **Modern UI** - Responsive React interface built with Tailwind CSS
- **Comprehensive Error Handling** - Robust validation and error management

### Planned Services
- Vector Database management
- Serverless Functions platform
- Virtual Server deployment
- Kafka messaging services
- Document RAG processing
- Container Services
- S3-compatible storage management

## Architecture

```
vast-services-mvp/
├── backend/                 # Node.js/Express API server
│   ├── src/
│   │   ├── controllers/     # Request handlers and business logic
│   │   ├── services/        # External API integrations (VAST, Database)
│   │   ├── middleware/      # Authentication, validation, error handling
│   │   ├── routes/          # API endpoint definitions
│   │   └── server.js        # Application entry point
│   └── package.json
└── frontend/                # React application
    ├── src/
    │   ├── components/      # Reusable UI components
    │   ├── pages/           # Application pages and views
    │   ├── services/        # API client and service layers
    │   ├── contexts/        # React context providers
    │   ├── hooks/           # Custom React hooks
    │   └── styles/          # Global styles and CSS
    └── package.json
```

## Prerequisites

- **Node.js** 16.x or higher
- **npm** 7.x or higher
- **VAST Data Cluster** with API access
- Valid VAST cluster credentials (host, port, username, password)

## Quick Start

### 1. Clone and Install
```bash
git clone <repository-url>
cd vast-services-mvp

# Install backend dependencies
cd backend
npm install

# Install frontend dependencies
cd ../frontend
npm install
```

### 2. Configure Environment Variables

**Backend Configuration** (`backend/.env`):
```bash
NODE_ENV=development
PORT=3001
JWT_SECRET=your-secure-secret-key-change-this
JWT_EXPIRES_IN=8h
FRONTEND_URL=http://localhost:3000
```

**Frontend Configuration** (`frontend/.env`):
```bash
REACT_APP_API_URL=http://localhost:3001/api
```

### 3. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
npm run dev
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:3001/api

## Usage Guide

### Initial Login
1. Navigate to the login page
2. Enter your VAST cluster information:
   - **Host**: Your VAST cluster IP address
   - **Port**: API port (typically 443)
   - **Username/Password**: Your VAST credentials
   - **Tenant**: Tenant name (default: "default")
3. Click "Connect to VAST"

### Managing Database Schemas
1. From the dashboard, click "Database Schemas" or navigate to `/schemas`
2. Click "Create Schema" to add a new database schema
3. Configure the schema:
   - **Name**: Unique schema identifier
   - **Path**: Filesystem path (auto-generated if empty)
   - **Protocols**: Select protocols (DATABASE required for database functionality)
4. Click "Create Schema"

The application creates VAST Views with DATABASE protocol enabled to implement database schemas.

## API Reference

### Authentication Endpoints
- `POST /api/auth/login` - Authenticate with VAST cluster
- `GET /api/auth/verify` - Verify current JWT token
- `POST /api/auth/logout` - End user session

### Schema Management Endpoints
- `GET /api/schemas` - List all database schemas
- `POST /api/schemas` - Create new schema
- `GET /api/schemas/:name` - Get specific schema details
- `DELETE /api/schemas/:name` - Delete schema
- `GET /api/schemas/:name/tables` - List tables in schema

### Request/Response Examples

**Login Request:**
```json
POST /api/auth/login
{
  "vastHost": "10.143.11.204",
  "vastPort": 443,
  "username": "admin",
  "password": "password",
  "tenant": "default"
}
```

**Create Schema Request:**
```json
POST /api/schemas
{
  "name": "analytics_db",
  "path": "/analytics_db",
  "protocols": ["DATABASE", "S3"],
  "description": "Analytics database schema"
}
```

## Development

### Technology Stack
- **Frontend**: React 18, React Router, React Query, Tailwind CSS
- **Backend**: Node.js, Express, JWT, Axios
- **Authentication**: JWT with VAST API integration
- **State Management**: React Query for server state, React Context for auth

### Development Scripts
```bash
# Backend
npm run dev          # Start development server with nodemon
npm start           # Start production server

# Frontend  
npm start           # Start development server
npm run build       # Build for production
npm test            # Run tests
```

### Adding New Features
1. **Backend Services**: Add to `backend/src/services/`
2. **API Controllers**: Create in `backend/src/controllers/`
3. **Routes**: Define in `backend/src/routes/`
4. **Frontend Components**: Add to `frontend/src/components/`
5. **Pages**: Create in `frontend/src/pages/`

### Code Style Guidelines
- Use functional components with hooks in React
- Implement proper error boundaries and loading states
- Follow REST API conventions for backend endpoints
- Use TypeScript-style JSDoc comments for better documentation
- Maintain consistent error handling patterns

## Deployment

### Production Environment Variables
```bash
# Backend
NODE_ENV=production
JWT_SECRET=secure-production-secret
FRONTEND_URL=https://your-domain.com

# Frontend
REACT_APP_API_URL=https://api.your-domain.com
```

### Build Commands
```bash
# Frontend production build
cd frontend
npm run build

# Backend runs with same commands
cd backend
npm start
```

## Security Considerations

- **JWT Security**: Tokens expire after 8 hours by default
- **HTTPS Enforcement**: All VAST API communication uses HTTPS
- **Input Validation**: Comprehensive validation on all endpoints
- **Rate Limiting**: 100 requests per 15 minutes per IP
- **CORS Configuration**: Restricted to configured frontend URL
- **SSL Verification**: Disabled for development (configure for production)

## Troubleshooting

### Common Issues

**Connection Failed:**
- Verify VAST cluster IP and port accessibility
- Check firewall settings and network connectivity
- Ensure VAST API service is running

**Authentication Errors:**
- Confirm username and password are correct
- Verify tenant exists on the VAST cluster
- Check if user has necessary permissions

**CORS Errors:**
- Ensure `FRONTEND_URL` is correctly set in backend `.env`
- Verify both servers are running on expected ports

**Development Issues:**
- Run `npm install` in both backend and frontend directories
- Check Node.js version compatibility
- Ensure environment variables are properly configured

### Debug Mode
Enable debug logging by setting:
```bash
NODE_ENV=development
```

### Health Checks
- **Backend Health**: http://localhost:3001/health
- **Frontend**: Check browser console for errors

## Roadmap

### Phase 1 (Current)
- ✅ VAST authentication and connection
- ✅ Database schema management
- ✅ Basic dashboard and navigation

### Phase 2 (Planned)
- [ ] Vector Database integration and management
- [ ] Table management interface with CRUD operations
- [ ] Advanced query interface for database operations
- [ ] S3 bucket management

### Phase 3 (Future)
- [ ] Serverless Functions platform
- [ ] Virtual Server deployment and management
- [ ] Kafka topic and stream management
- [ ] Container Services orchestration
- [ ] Monitoring and analytics dashboards
- [ ] Role-based access control and user management

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow existing code patterns and conventions
4. Add comprehensive error handling for new features
5. Update documentation for any API changes
6. Test with real VAST clusters when possible
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## License

Apache-2.0

## Support

- **VAST Data Platform Documentation**: https://vastdata.com/documentation/
- **Issues**: [Add issue tracker URL]
- **Contact**: [Add contact information]

---

*Built with ❤️ for the VAST Data Platform ecosystem*
