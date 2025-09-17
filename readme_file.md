# VAST Services MVP

A modern web interface for managing VAST Data Platform services, focusing on database schema management.

## Features

- **Authentication**: Secure login to VAST clusters
- **Database Management**: Create and manage database schemas
- **Modern UI**: React-based interface with Tailwind CSS
- **Real-time Integration**: Direct VAST API integration
- **Modular Architecture**: Easy to extend and modify

## Architecture

### Frontend (React)
- `src/pages/` - Main application pages
- `src/components/` - Reusable UI components  
- `src/services/` - API service layers
- `src/contexts/` - React context providers
- `src/hooks/` - Custom React hooks

### Backend (Node.js/Express)
- `src/controllers/` - Route handlers and business logic
- `src/services/` - External service integrations (VAST API)
- `src/middleware/` - Authentication, validation, error handling
- `src/routes/` - API route definitions

## Quick Start

1. **Setup the project:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure environment variables:**
   - Backend: Edit `backend/.env` with your settings
   - Frontend: Edit `frontend/.env` if needed

3. **Start the backend:**
   ```bash
   cd backend
   npm run dev
   ```

4. **Start the frontend (in another terminal):**
   ```bash
   cd frontend  
   npm start
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3001

## VAST API Integration

The application integrates with VAST Data Platform APIs:

- **Authentication**: `/api/token/` endpoint
- **Schema Management**: Uses VAST Views with DATABASE protocol
- **Tenant Support**: Multi-tenant database isolation

### Supported VAST API Endpoints

- `POST /token/` - Authentication
- `GET /views/` - List database schemas
- `POST /views/` - Create new schema
- `GET /tenants/` - List available tenants

## Usage

1. **Login**: Enter your VAST cluster details (IP, port, credentials)
2. **Dashboard**: View available services and system status
3. **Schema Management**: Create and manage database schemas
4. **Database Operations**: Create tables and manage data structures

## Development

### Adding New Services

1. Create service in `backend/src/services/`
2. Add controller in `backend/src/controllers/`
3. Define routes in `backend/src/routes/`
4. Create frontend components and pages
5. Add service to main navigation

### File Structure

```
vast-services-mvp/
├── frontend/
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/         # Application pages
│   │   ├── services/      # API clients
│   │   ├── contexts/      # React contexts
│   │   └── hooks/         # Custom hooks
│   └── public/
└── backend/
    └── src/
        ├── controllers/   # Request handlers
        ├── services/      # External integrations
        ├── middleware/    # Express middleware
        └── routes/        # API routes
```

## Security

- JWT-based authentication
- Request validation and sanitization
- CORS protection
- Rate limiting
- Secure VAST API token handling

## Environment Variables

### Backend (.env)
```
NODE_ENV=development
PORT=3001
JWT_SECRET=your-secret-key
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:3001/api
```

## Contributing

1. Keep components small and focused
2. Use TypeScript for new components (optional)
3. Follow existing code patterns
4. Add error handling for all API calls
5. Update this README for new features

## Troubleshooting

### Common Issues

- **CORS errors**: Check FRONTEND_URL in backend .env
- **Authentication failures**: Verify VAST cluster connectivity
- **Module not found**: Run `npm install` in both directories
- **Port conflicts**: Change ports in .env files

### API Testing

Use the VAST API documentation (Swagger UI) to test endpoints directly:
`https://your-vast-host/api/?format=openapi`

## Next Steps

- [ ] Add table management interface
- [ ] Implement vector database support  
- [ ] Add monitoring dashboards
- [ ] Support for other VAST services (Kafka, S3, etc.)
- [ ] Add user management features
- [ ] Implement comprehensive error logging