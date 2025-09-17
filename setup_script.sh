#!/bin/bash

echo "Setting up VAST Services MVP..."

# Install backend dependencies
echo "Installing backend dependencies..."
cd vast-services-mvp/backend
npm install

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd ../frontend
npm install

echo "Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend: cd backend && npm run dev"
echo "2. Frontend: cd frontend && npm start"
echo ""
echo "The application will be available at http://localhost:3000"
echo "Backend API will run on http://localhost:3001"