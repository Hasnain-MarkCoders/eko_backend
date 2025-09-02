#!/bin/bash

# Eko Backend Deployment Script

echo "🚀 Starting Eko Backend deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file based on .env.example with your Firebase credentials."
    echo "You can copy the example: cp .env.example .env"
    exit 1
fi

# Stop and remove existing container if it exists
echo "🛑 Stopping existing container..."
podman stop eko_backend_container 2>/dev/null || true
podman rm eko_backend_container 2>/dev/null || true

# Build the Docker image
echo "🔨 Building Docker image..."
podman build -t eko_backend .

# Run the container with environment variables
echo "🏃 Starting container..."
podman run -d \
    --name eko_backend_container \
    --env-file .env \
    -p 9753:8000 \
    eko_backend

# Check if container is running
sleep 5
if podman ps | grep -q eko_backend_container; then
    echo "✅ Container started successfully!"
    echo "🌐 API is available at: http://localhost:9753"
    echo "📋 Container logs: podman logs eko_backend_container"
else
    echo "❌ Container failed to start. Check logs:"
    podman logs eko_backend_container
    exit 1
fi
