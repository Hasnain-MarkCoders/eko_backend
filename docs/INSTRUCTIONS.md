# Eko Backend - Local Development Instructions

This document provides step-by-step instructions for running the Eko Backend API locally using Docker.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Docker** or **Podman** (container runtime)
- **Git** (for cloning the repository)
- **Text editor** (VS Code, Vim, etc.)

### Installing Docker/Podman

#### Docker
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
```

#### Podman
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install podman
```

## Quick Start

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd eko_backend
```

### 2. Environment Setup
Create a `.env` file in the project root with your Firebase credentials:

```bash
# Copy the example (if available)
cp .env.example .env

# Or create manually
touch .env
```

Add your Firebase configuration to `.env`:
```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour-Private-Key-Here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com
FIREBASE_UNIVERSE_DOMAIN=googleapis.com
```

### 3. Deploy the Application

#### Option A: Interactive Mode (Recommended for first-time setup)
```bash
./deploy.sh
```

The script will:
- Detect available container runtimes (Docker/Podman)
- Let you choose which one to use
- Build the Docker image
- Start the container
- Display connection information

#### Option B: Non-Interactive Mode (For automation/CI)
```bash
./deploy.sh --non-interactive
# or
./deploy.sh -y
```

### 4. Verify the Deployment

Once deployed, you should see:
```
✅ Container started successfully!
🌐 API is available at: http://localhost:9753
📋 Container logs: docker logs eko_backend_container
🛑 To stop container: docker stop eko_backend_container
```

Test the API:
```bash
# Health check
curl http://localhost:9753/health

# Root endpoint
curl http://localhost:9753/
```

## Development Workflow

### Making Changes

1. **Edit your code** in your preferred editor
2. **Restart the container** to apply changes:
   ```bash
   ./restart.sh
   ```

### Viewing Logs

```bash
# Using Docker
docker logs eko_backend_container

# Using Podman
podman logs eko_backend_container

# Follow logs in real-time
docker logs -f eko_backend_container
```

### Stopping the Application

```bash
# Stop the container
docker stop eko_backend_container

# Remove the container
docker rm eko_backend_container

# Or use the restart script (stops and restarts)
./restart.sh
```

## API Access

Once running, the API will be available at `http://localhost:9753`.

For detailed API endpoint documentation, see `docs/documentation.md`.

## Troubleshooting

### Common Issues

#### 1. Container Runtime Not Found
```
❌ No container runtime found!
```
**Solution:** Install Docker or Podman (see Prerequisites section)

#### 2. .env File Missing
```
❌ Error: .env file not found!
```
**Solution:** Create a `.env` file with your Firebase credentials

#### 3. Port Already in Use
```
❌ Container failed to start
```
**Solution:** 
- Check if port 9753 is already in use: `lsof -i :9753`
- Stop existing containers: `docker stop eko_backend_container`
- Or change the port in the deploy script

#### 4. Firebase Authentication Errors
```
❌ Firebase initialization failed
```
**Solution:** 
- Verify your Firebase credentials in `.env`
- Check that the service account has proper permissions
- Ensure the private key format is correct (with `\n` for newlines)

### Getting Help

1. **Check container logs:**
   ```bash
   docker logs eko_backend_container
   ```

2. **Verify container status:**
   ```bash
   docker ps
   ```

3. **Test individual components:**
   ```bash
   # Test health endpoint
   curl http://localhost:9753/health
   
   # Test root endpoint
   curl http://localhost:9753/
   ```

## Scripts Reference

### deploy.sh
- **Purpose:** Build and deploy the application
- **Usage:** `./deploy.sh [--non-interactive]`
- **Features:** 
  - Auto-detects Docker/Podman
  - Interactive runtime selection
  - Comprehensive error handling
  - Container status verification

### restart.sh
- **Purpose:** Stop and restart the application
- **Usage:** `./restart.sh`
- **Features:**
  - Graceful container shutdown
  - Quick restart for development

## Production Considerations

For production deployment:

1. **Environment Variables:** Use secure environment variable management
2. **Port Configuration:** Consider using standard ports (80/443)
3. **SSL/TLS:** Implement HTTPS with proper certificates
4. **Monitoring:** Add logging and monitoring solutions
5. **Scaling:** Consider container orchestration (Docker Compose, Kubernetes)

## Support

If you encounter issues not covered in this guide:

1. Check the container logs for detailed error messages
2. Verify your environment setup matches the prerequisites
3. Ensure all required environment variables are properly configured
4. Test with the health check endpoint to verify basic connectivity
