#!/bin/bash
# Restart script for PACE Backend on Hostinger VPS
# This script pulls the latest changes and restarts the Docker containers

echo "=========================================="
echo "PACE Backend Server Restart Script"
echo "=========================================="
echo ""

# Navigate to project directory
echo "Step 1: Navigating to project directory..."
cd /root/pace-backend-clean || cd /var/www/pace-backend-clean || cd ~/pace-backend-clean || {
    echo "Error: Could not find project directory"
    echo "Please run this script from the correct location or update the path"
    exit 1
}

echo "Current directory: $(pwd)"
echo ""

# Pull latest changes from GitHub
echo "Step 2: Pulling latest changes from GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "Error: Failed to pull from GitHub"
    echo "You may need to stash or commit local changes first"
    exit 1
fi
echo ""

# Stop running containers
echo "Step 3: Stopping current containers..."
docker-compose down

if [ $? -ne 0 ]; then
    echo "Warning: docker-compose down failed, continuing anyway..."
fi
echo ""

# Rebuild and restart containers
echo "Step 4: Rebuilding and starting containers..."
docker-compose up -d --build

if [ $? -ne 0 ]; then
    echo "Error: Failed to start containers"
    exit 1
fi
echo ""

# Wait for services to start
echo "Step 5: Waiting for services to start..."
sleep 5
echo ""

# Check container status
echo "Step 6: Checking container status..."
docker-compose ps
echo ""

# Test health endpoint
echo "Step 7: Testing health endpoint..."
sleep 3
curl -s http://localhost:8000/api/health || curl -s http://127.0.0.1:8000/api/health

if [ $? -eq 0 ]; then
    echo ""
    echo ""
    echo "=========================================="
    echo "✓ Server restarted successfully!"
    echo "=========================================="
    echo "Backend is running at: http://89.116.187.76:8000"
    echo "Health check: http://89.116.187.76:8000/api/health"
    echo "API docs: http://89.116.187.76:8000/docs"
else
    echo ""
    echo "Warning: Health check failed. Check logs with:"
    echo "  docker-compose logs -f backend"
fi

echo ""
echo "Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart: docker-compose restart"
echo "=========================================="
