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
echo "🔄 Step 1/4: Committing changes..."
echo "=> git add ."
git add .
echo "=> git commit -m '$COMMIT_MESSAGE'"
git commit -m "$COMMIT_MESSAGE"
echo "=> git push origin main"
if ! git push origin main; then
    echo "❌ Error: Failed to push to GitHub. This could be due to:"
    echo "   - Network connectivity issues"
    echo "   - DNS resolution problems"
    echo "   - GitHub authentication issues"
    echo "   - Repository access permissions"
    echo ""
    echo "Please check your network connection and try again."
    echo "You can also push manually with: git push origin main"
    exit 1
fi
echo "✅ Step 1 completed: Changes committed and pushed"

# SSH and deploy on production server
echo "🚀 Step 2/4: Connecting to production server..."
echo "=> ssh -i $SSH_KEY $SSH_USER@$SERVER_IP"

ssh -i $SSH_KEY $SSH_USER@$SERVER_IP << EOF
  set -e
  cd $DEPLOY_PATH
  
  echo "📥 Step 3/4: Pulling latest changes..."
  echo "=> git pull origin main"
  git pull origin main
  
  echo "🔄 Running restart script..."
  echo "=> ./restart.sh -y $FORCE_FLAG"
  echo ""
  echo "📋 Restart script output (this may take a few minutes):"
  echo "=================================================="
  ./restart.sh -y $FORCE_FLAG 2>&1
  echo "=================================================="
  echo "✅ Restart script completed"
  
  echo "⏳ Waiting for container to start..."
  echo "=> sleep 10"
  sleep 10
  
  echo "📋 Step 4/4: Verifying container started successfully..."
  echo "=> docker logs eko_backend_container --tail 20"
  docker logs eko_backend_container --tail 20
  
  echo "✅ Deployment completed successfully!"
EOF

# Check if SSH command succeeded
if [ $? -eq 0 ]; then
    echo "✅ Step 2 completed: Connected to production server"
else
    echo "❌ Error: Failed to connect to production server or deployment failed."
    echo "This could be due to:"
    echo "   - SSH connection issues"
    echo "   - Server is down or unreachable"
    echo "   - SSH key authentication failed"
    echo "   - Network connectivity problems"
    echo ""
    echo "Please check your server connection and SSH key configuration."
    exit 1
fi
echo "✅ Step 3 completed: Pulled latest changes and restarted container"
echo "✅ Step 4 completed: Verified container is running"
echo "🎉 All steps completed! Deployment to production server successful!"
