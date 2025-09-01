# Eko Backend Deployment Guide

## Firebase Configuration Issue Fix

The Docker container was failing because Firebase credentials were not properly configured. Here's how to fix it:

## Quick Fix Steps

### 1. Create Environment File
```bash
cp .env.example .env
```

### 2. Configure Firebase Credentials
Edit the `.env` file with your actual Firebase service account credentials:

```bash
nano .env
```

Replace the placeholder values with your actual Firebase service account details:
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `FIREBASE_PRIVATE_KEY`: Your service account private key (keep the quotes and \n characters)
- `FIREBASE_CLIENT_EMAIL`: Your service account email
- `FIREBASE_CLIENT_ID`: Your service account client ID
- `FIREBASE_CLIENT_X509_CERT_URL`: Your service account cert URL

### 3. Deploy with Script
```bash
./deploy.sh
```

## Alternative Deployment Methods

### Method 1: Using Docker Compose
```bash
docker-compose up -d
```

### Method 2: Manual Docker Commands
```bash
# Build image
docker build -t eko_backend .

# Run with environment file
docker run -d \
    --name eko_backend_container \
    --env-file .env \
    -p 9753:8000 \
    eko_backend
```

### Method 3: Run with Environment Variables
```bash
docker run -d \
    --name eko_backend_container \
    -e FIREBASE_PROJECT_ID="your-project-id" \
    -e FIREBASE_PRIVATE_KEY="your-private-key" \
    -e FIREBASE_CLIENT_EMAIL="your-service-account@project.iam.gserviceaccount.com" \
    -p 9753:8000 \
    eko_backend
```

## Getting Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Project Settings > Service Accounts
4. Click "Generate new private key"
5. Download the JSON file
6. Extract the values and put them in your `.env` file

## Troubleshooting

### Check Container Logs
```bash
docker logs eko_backend_container
```

### Check Container Status
```bash
docker ps -a
```

### Restart Container
```bash
docker restart eko_backend_container
```

## Security Notes

- Never commit your `.env` file to version control
- The `.env` file is already in `.gitignore`
- Use environment variables in production
- Consider using Docker secrets for sensitive data in production
