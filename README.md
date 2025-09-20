# VAST Services MVP

A modern web application for managing VAST Data Platform services with a focus on database schema management and cloud service orchestration. Now featuring simplified database schema creation using environment variables for seamless VAST Database integration.

## Overview

VAST Services MVP provides an intuitive interface for managing VAST Data Platform resources through a React frontend and Node.js backend. The application now uses environment variables for VAST Database connection parameters, making schema creation as simple as providing just a schema name.

## Features

### Current Features
- **Simplified VAST Database Integration** - Configure connection once via environment variables
- **One-Click Schema Creation** - Users only need to provide schema name
- **Database Schema Management** - Create and manage database schemas via VAST Database
- **Connection Status Monitoring** - Real-time VAST Database connection monitoring
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
│   │   ├── services/        # VAST Database and API integrations
│   │   │   ├── vastDbService.js    # VAST Database SDK-like service
│   │   │   └── vastService.js      # VAST API authentication
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
- **VAST Data Cluster** with Database service enabled
- **VAST Database Configuration**:
  - Virtual IP pool configured with DNS service
  - S3 access & secret keys on the VAST cluster
  - Tabular identity policy with proper permissions
  - VAST Cluster release `5.0.0-sp10` or later

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
# Application Configuration
NODE_ENV=development
PORT=3001
JWT_SECRET=your-secure-secret-key-change-this
JWT_EXPIRES_IN=8h
FRONTEND_URL=http://localhost:3000

# VAST Database Configuration
VAST_ENDPOINT=http://vip-pool.v123-xy.VastENG.lab
VAST_ACCESS_KEY_ID=your-vast-access-key
VAST_SECRET_ACCESS_KEY=your-vast-secret-key
VAST_BUCKET_NAME=your-bucket-name

# Optional VAST Configuration
VAST_REGION=africa-east-1
VAST_VERIFY_SSL=false
```

**Frontend Configuration** (`frontend/.env`):
```bash
REACT_APP_API_URL=http://localhost:3001/api
```

### 3. Set Up VAST Database Connection

Before running the application, ensure your VAST cluster has:

1. **Virtual IP Pool**: Configured with DNS service for database access
2. **S3 Credentials**: Access key and secret key for authentication
3. **Bucket**: Pre-created bucket specified in `VAST_BUCKET_NAME`
4. **Permissions**: Tabular identity policy allowing schema/table operations

### 4. Start the Application

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

### 5. Access the Application
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

#### Creating Schemas (Simplified!)
1. From the dashboard, click "Database Schemas" or navigate to `/schemas`
2. Verify VAST Database connection status (should show "Connected")
3. Click "Create Schema"
4. Enter only:
   - **Schema Name**: Unique identifier (e.g., `analytics_db`)
   - **Description**: Optional description
5. Click "Create Schema"

The application automatically:
- Uses the configured VAST endpoint and credentials
- Creates the schema in the specified bucket
- Sets up DATABASE and S3 protocols
- Configures the proper path: `/{bucket-name}/{schema-name}`

#### Schema Management
- **View Schemas**: All schemas are listed with connection status
- **Schema Details**: Click the eye icon to view full schema information
- **Delete Schemas**: Click the trash icon (with confirmation)
- **Connection Monitoring**: Real-time status of VAST Database connection

## API Reference

### Connection Endpoints
- `GET /api/schemas/connection` - Get VAST Database connection status

### Schema Management Endpoints
- `GET /api/schemas` - List all database schemas
- `POST /api/schemas` - Create new schema (requires only `name` and optional `description`)
- `GET /api/schemas/:name` - Get specific schema details
- `DELETE /api/schemas/:name` - Delete schema

### Table Management Endpoints
- `GET /api/schemas/:name/tables` - List tables in schema
- `POST /api/schemas/:name/tables` - Create table in schema

### Request/Response Examples

**Create Schema Request (Simplified):**
```json
POST /api/schemas
{
  "name": "analytics_db",
  "description": "Analytics database schema"
}
```

**Response:**
```json
{
  "success": true,
  "schema": {
    "name": "analytics_db",
    "bucket": "your-bucket-name",
    "path": "/your-bucket-name/analytics_db",
    "protocols": ["DATABASE", "S3"],
    "created": "2025-01-01T12:00:00Z",
    "id": "abc123"
  },
  "message": "Schema 'analytics_db' created successfully"
}
```

## Development

### Technology Stack
- **Frontend**: React 18, React Router, React Query, Tailwind CSS
- **Backend**: Node.js, Express, JWT, Axios
- **VAST Integration**: Environment-based configuration, SDK-like service pattern
- **State Management**: React Query for server state, React Context for auth

### VAST Database Service Pattern

The application uses a `vastDbService` that mimics the vastdb Python SDK pattern:

```javascript
// Automatic connection using environment variables
const result = await vastDbService.createSchema('my_schema');

// Equivalent to Python vastdb:
// session = vastdb.connect(endpoint, access, secret)
// with session.transaction() as tx:
//     bucket = tx.bucket(bucket_name)
//     schema = bucket.create_schema('my_schema')
```

### Development Scripts
```bash
# Backend
docker compose up   # Start development server with nodemon

# Frontend  
npm start           # Start development server
```

### Environment Variable Requirements

**Required Variables:**
- `VAST_ENDPOINT`: VAST cluster endpoint URL
- `VAST_ACCESS_KEY_ID`: S3 access key for authentication
- `VAST_SECRET_ACCESS_KEY`: S3 secret key for authentication  
- `VAST_BUCKET_NAME`: Target bucket for schema creation

**Optional Variables:**
- `VAST_REGION`: AWS region identifier (default: "africa-east-1")
- `VAST_VERIFY_SSL`: SSL verification (default: false for development)

## Deployment

### Production Environment Variables
```bash
# Application
NODE_ENV=production
JWT_SECRET=secure-production-secret
FRONTEND_URL=https://your-domain.com

# VAST Database
VAST_ENDPOINT=https://production-vip-pool.vastcluster.com
VAST_ACCESS_KEY_ID=production-access-key
VAST_SECRET_ACCESS_KEY=production-secret-key
VAST_BUCKET_NAME=production-bucket
VAST_VERIFY_SSL=true
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

- **Environment Variables**: All VAST credentials stored in environment variables
- **JWT Security**: Tokens expire after 8 hours by default
- **HTTPS Enforcement**: All VAST Database communication uses HTTPS
- **Input Validation**: Comprehensive validation on all endpoints
- **Rate Limiting**: 100 requests per 15 minutes per IP
- **CORS Configuration**: Restricted to configured frontend URL

## Troubleshooting

### Common Issues

**VAST Database Connection Failed:**
- Verify `VAST_ENDPOINT` is accessible from your network
- Check `VAST_ACCESS_KEY_ID` and `VAST_SECRET_ACCESS_KEY` are correct
- Ensure `VAST_BUCKET_NAME` exists on the cluster
- Verify tabular identity policy permissions

**Schema Creation Failed:**
- Check VAST Database connection status in the UI
- Verify bucket exists and is accessible
- Ensure schema name follows naming conventions (letters, numbers, underscore)
- Check cluster has sufficient permissions for schema creation

**Authentication Issues:**
- Verify VAST cluster user credentials are correct
- Check if user has necessary tabular database permissions
- Ensure tenant exists on the VAST cluster

### Connection Status Monitoring

The application provides real-time connection monitoring:
- **Green Status**: VAST Database is connected and ready
- **Red Status**: Connection issues detected
- **Connection Info**: Shows endpoint, bucket, and status details

### Debug Mode
Enable debug logging by setting:
```bash
NODE_ENV=development
```

### Health Checks
- **Backend Health**: http://localhost:3001/health
- **VAST Database Connection**: http://localhost:3001/api/schemas/connection
- **Frontend**: Check browser console for errors

## Migration from Manual Configuration

If migrating from manual VAST connection configuration:

1. **Set Environment Variables**: Add VAST connection details to `.env`
2. **Remove Frontend Fields**: Path and protocols no longer required in UI
3. **Update API Calls**: Schema creation now only requires name and description
4. **Test Connection**: Use connection status endpoint to verify setup

## Roadmap

### Phase 1 (Current)
- ✅ Environment-based VAST Database configuration
- ✅ Simplified schema creation (name only)
- ✅ Real-time connection monitoring
- ✅ Basic dashboard and navigation

### Phase 2 (Planned)
- [ ] Advanced table management with column definitions
- [ ] Query interface for database operations
- [ ] Schema import/export functionality
- [ ] Vector Database integration

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
4. Test with real VAST clusters when possible
5. Update documentation for any environment variable changes
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

Apache-2.0

## Support

- **VAST Data Platform Documentation**: https://vastdata.com/documentation/
- **VAST Database SDK**: https://vastdb-sdk.readthedocs.io/
- **Issues**: [Add issue tracker URL]
- **Contact**: [Add contact information]

---

*Built with ❤️ for the VAST Data Platform ecosystem*