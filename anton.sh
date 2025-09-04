#!/bin/bash
# anton.sh - EKO Backend Deployment Script

set -e

# Configuration
SERVER_IP="194.35.120.165"  # Update with your server IP
DEPLOY_PATH="/var/www/html/eko_backend"
SSH_USER="markcoders"  # Update with your username
SSH_KEY="~/.ssh/markcoders_deploy_key"  # Update with your key path

# Parse command line arguments
FORCE_FLAG=""
if [[ "$1" == "--force" ]]; then
    FORCE_FLAG="--force"
    echo "🔧 Force mode enabled - restart script will run with --force"
fi

# Get commit message input
read -p "Enter commit message: " COMMIT_MESSAGE

if [ -z "$COMMIT_MESSAGE" ]; then
  echo "❌ Commit message cannot be empty!"
  exit 1
fi

# Commit and push changes
echo "🔄 Committing changes..."
git add .
git commit -m "$COMMIT_MESSAGE"
git push origin main

# SSH and deploy on production server
echo "🚀 Deploying to production server at $SERVER_IP ($DEPLOY_PATH) as $SSH_USER"

ssh -i $SSH_KEY $SSH_USER@$SERVER_IP << EOF
  set -e
  cd $DEPLOY_PATH
  
  echo "📥 Pulling latest changes..."
  git pull origin main
  
  echo "🔄 Running restart script..."
  ./restart.sh -y $FORCE_FLAG
  
  echo "⏳ Waiting for container to start..."
  sleep 10
  
  echo "📋 Verifying container started successfully..."
  docker logs eko_backend_container --tail 20
  
  echo "✅ Deployment completed successfully!"
EOF

echo "🎉 Deployment to production server completed!"
