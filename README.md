# VAST Services MVP

A modern web interface for managing VAST Data Platform services, with initial focus on database schema management.

## Overview

This MVP provides a React-based frontend and Node.js backend for managing VAST Data Platform resources. It authenticates directly with VAST clusters and provides a user-friendly interface for database operations.

## Features

- **VAST Authentication**: Secure login to VAST clusters with JWT token management
- **Database Schema Management**: Create and manage database schemas via VAST Views
- **Protocol Support**: Configure views with DATABASE, S3, NFS, and SMB protocols
- **Real-time Integration**: Direct VAST API communication
- **Responsive UI**: Modern React interface with Tailwind CSS
- **Error Handling**: Comprehensive validation and error management

## Architecture

```
vast-services-mvp/
├── frontend/          # React application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Application pages
│   │   ├── services/      # API service layer
│   │   ├── contexts/      # React context providers
│   │   └── hooks/         # Custom React hooks
│   └── public/
└── backend/           # Node.js/Express API
    └── src/
        ├── controllers/   # Route handlers
        ├── services/      # External integrations
        ├── middleware/    # Express middleware
        └── routes/        # API route definitions
```

## Prerequisites

- Node.js 16+ and npm
- Access to a VAST Data cluster
- VAST cluster credentials (IP, port, username, password)

## Installation

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd vast-services-mvp
   ```

2. **Install dependencies:**
   ```bash
   # Backend
   cd backend
   npm install
   
   # Frontend  
   cd ../frontend
   npm install
   ```

3. **Configure environment:**
   ```bash
   # Backend - create backend/.env
   NODE_ENV=development
   PORT=3001
   JWT_SECRET=your-secure-secret-key
   JWT_EXPIRES_IN=8h
   FRONTEND_URL=http://localhost:3000
   
   # Frontend - create frontend/.env
   REACT_APP_API_URL=http://localhost:3001/api
   ```

## Running the Application

Start both servers in separate terminals:

**Backend:**
```bash
cd backend
npm run dev
```

**Frontend:**
```bash
cd frontend
npm start
```

Access the application at `http://localhost:3000`

## Usage

### Login
1. Enter your VAST cluster details:
   - **Host**: VAST cluster IP address
   - **Port**: API port (typically 443)
   - **Username/Password**: VAST credentials
   - **Tenant**: Tenant name (default: "default")

### Managing Database Schemas
1. Navigate to "Database Schemas"
2. Click "Create Schema" to add a new schema
3. Configure:
   - **Name**: Schema identifier
   - **Path**: Filesystem path (auto-generated if empty)
   - **Protocols**: Select DATABASE for database functionality
   - **Description**: Optional description

Schemas are implemented as VAST Views with DATABASE protocol enabled.

## API Endpoints

### Authentication
- `POST /api/auth/login` - Authenticate with VAST cluster
- `GET /api/auth/verify` - Verify JWT token
- `POST /api/auth/logout` - Logout

### Schema Management
- `GET /api/schemas` - List all database schemas
- `POST /api/schemas` - Create new schema
- `GET /api/schemas/:name` - Get schema details
- `DELETE /api/schemas/:name` - Delete schema
- `GET /api/schemas/:name/tables` - List tables in schema

## VAST API Integration

The application integrates with these VAST endpoints:
- `POST /token/` - Authentication
- `GET /views/` - List views (schemas)
- `POST /views/` - Create views
- `GET /tenants/` - List tenants

## Development

### Adding New Services

1. **Backend**: Create service in `backend/src/services/`
2. **Controller**: Add controller in `backend/src/controllers/`
3. **Routes**: Define routes in `backend/src/routes/`
4. **Frontend**: Create components and pages
5. **Navigation**: Add to main menu

### Code Organization

- Keep components small and focused
- Use React hooks for state management
- Implement proper error boundaries
- Follow existing patterns for API integration
- Add comprehensive error handling

### Environment Variables

**Backend:**
- `NODE_ENV` - Environment (development/production)
- `PORT` - Server port
- `JWT_SECRET` - JWT signing secret
- `FRONTEND_URL` - Frontend URL for CORS

**Frontend:**
- `REACT_APP_API_URL` - Backend API base URL

## Troubleshooting

### Common Issues

**Authentication Failures:**
- Verify VAST cluster connectivity
- Check IP address and port
- Confirm credentials are correct
- Ensure tenant exists

**CORS Errors:**
- Check `FRONTEND_URL` in backend `.env`
- Verify both servers are running

**Module Not Found:**
- Run `npm install` in both directories
- Check file paths and imports

**Port Conflicts:**
- Change `PORT` in backend `.env`
- Update `REACT_APP_API_URL` accordingly

### API Testing

Test VAST connectivity directly:
```bash
curl -k https://your-vast-host:443/api/
```

## Security Considerations

- JWT tokens expire after 8 hours
- HTTPS enforced for VAST communication
- SSL certificate validation disabled for development
- Input validation on all endpoints
- Rate limiting implemented

## Future Enhancements

- [ ] Table management interface
- [ ] Vector database integration
- [ ] S3 bucket management
- [ ] Kafka topic management
- [ ] User management
- [ ] Monitoring dashboards
- [ ] Advanced query interface
- [ ] Role-based access control

## Contributing

1. Follow existing code patterns
2. Add error handling for new features
3. Update documentation for changes
4. Test with real VAST clusters
5. Keep components modular and reusable

## License

[Add your license information]

## Support

For VAST Data Platform documentation: https://vastdata.com/documentation/

For issues with this MVP: [Add contact information or issue tracker]
