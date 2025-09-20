---
# PYTHON_BACKEND_README.md

# VAST Services MVP - Python Backend

A Python FastAPI backend conversion of the Node.js VAST Services MVP application. This backend provides REST API endpoints for VAST cluster authentication and database schema management.

## Features

- **JWT-based Authentication**: Secure authentication with VAST clusters
- **Database Schema Management**: Create, read, update, delete database schemas
- **Environment Variable Configuration**: Simplified VAST Database connection setup
- **Connection Status Monitoring**: Real-time VAST Database connection monitoring
- **Comprehensive Error Handling**: Robust validation and error management
- **Rate Limiting**: Built-in rate limiting middleware
- **Health Checks**: Application and service health monitoring

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type hints
- **PyJWT**: JSON Web Token implementation
- **HTTPX**: Async HTTP client for external API calls
- **Uvicorn**: ASGI server for running the application

## Project Structure

```
python-backend/
├── main.py                     # FastAPI application entry point
├── config.py                   # Configuration and settings
├── requirements.txt            # Python dependencies
├── models.py                   # Pydantic models for request/response
├── controllers/
│   ├── auth_controller.py      # Authentication endpoints
│   └── schema_controller.py    # Schema management endpoints
├── services/
│   ├── vast_service.py         # VAST API client service
│   └── vastdb_service.py       # VAST Database service
├── middleware/
│   ├── auth_middleware.py      # JWT authentication middleware
│   └── error_handler.py        # Error handling middleware
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Docker Compose setup
├── .env.example               # Environment variables template
└── start.sh                  # Development startup script
```

## Quick Start

### 1. Prerequisites

- Python 3.11 or higher
- VAST Data Cluster with Database service enabled
- VAST Database configuration (VIP pool, S3 credentials, bucket)

### 2. Installation

```bash
# Clone the repository and navigate to backend directory
cd python-backend

# Make startup script executable
chmod +x start.sh

# Run the startup script (creates venv, installs deps, starts server)
./start.sh
```

### 3. Manual Setup (Alternative)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start the application
uvicorn main:app --host 0.0.0.0 --port 3001 --reload
```

### 4. Environment Configuration

Create a `.env` file with your VAST configuration:

```bash
# Application Configuration
NODE_ENV=development
PORT=3001
JWT_SECRET=your-secure-secret-key-change-this
JWT_EXPIRES_IN=8h
FRONTEND_URL=http://localhost:3000

# VAST Database Configuration (Required)
VAST_ENDPOINT=http://vip-pool.v123-xy.VastENG.lab
VAST_ACCESS_KEY_ID=your-vast-access-key
VAST_SECRET_ACCESS_KEY=your-vast-secret-key
VAST_BUCKET_NAME=your-bucket-name

# Optional VAST Configuration
VAST_REGION=africa-east-1
VAST_VERIFY_SSL=false
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Authenticate with VAST cluster
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/verify` - Verify JWT token
- `GET /api/auth/me` - Get current user info

### Schema Management
- `GET /api/schemas/connection` - Get VAST Database connection status
- `GET /api/schemas` - List all database schemas
- `POST /api/schemas` - Create new schema
- `GET /api/schemas/{name}` - Get specific schema
- `DELETE /api/schemas/{name}` - Delete schema
- `POST /api/schemas/{name}/tables` - Create table in schema
- `GET /api/schemas/{name}/tables` - List tables in schema

### Health & Monitoring
- `GET /health` - Application health check
- `GET /api/schemas/health/schemas` - Database service health

## Usage Examples

### Create Schema
```bash
curl -X POST "http://localhost:3001/api/schemas" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "analytics_db",
       "description": "Analytics database schema"
     }'
```

### List Schemas
```bash
curl -X GET "http://localhost:3001/api/schemas" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Check Connection
```bash
curl -X GET "http://localhost:3001/api/schemas/connection" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Docker Deployment

### Using Docker Compose
```bash
# Create .env file with your configuration
cp .env.example .env

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Docker
```bash
# Build image
docker build -t vast-services-backend .

# Run container
docker run -d \
  --name vast-services \
  -p 3001:3001 \
  --env-file .env \
  vast-services-backend
```

## Development

### Adding New Features

1. **Models**: Add Pydantic models in `models.py`
2. **Controllers**: Create route handlers in `controllers/`
3. **Services**: Add business logic in `services/`
4. **Middleware**: Add middleware in `middleware/`

### Code Style
- Use Python type hints
- Follow PEP 8 style guide
- Add docstrings to functions and classes
- Use async/await for I/O operations

### Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when implemented)
pytest
```

## Production Deployment

### Environment Variables
```bash
NODE_ENV=production
JWT_SECRET=secure-random-secret-key
VAST_VERIFY_SSL=true
```

### Performance Tuning
```bash
# Run with multiple workers
uvicorn main:app --host 0.0.0.0 --port 3001 --workers 4

# Use Gunicorn with Uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Troubleshooting

### Common Issues

1. **VAST Database Connection Failed**
   - Check `VAST_ENDPOINT` accessibility
   - Verify `VAST_ACCESS_KEY_ID` and `VAST_SECRET_ACCESS_KEY`
   - Ensure `VAST_BUCKET_NAME` exists

2. **Authentication Issues**
   - Verify VAST cluster credentials
   - Check JWT_SECRET configuration
   - Ensure user has database permissions

3. **Port Already in Use**
   ```bash
   # Change port in .env or command line
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration from Node.js

The Python backend maintains the same API structure as the Node.js version:

- Same endpoint URLs and HTTP methods
- Same request/response formats
- Same authentication flow
- Same environment variable names

Simply replace the Node.js backend with this Python version and update the startup scripts.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow Python coding standards
4. Add tests for new features
5. Update documentation
6. Submit a pull request

## License

Apache-2.0 License - See LICENSE file for details
