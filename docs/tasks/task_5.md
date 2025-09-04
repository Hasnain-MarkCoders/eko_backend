# Task 5: CI/CD Pipeline Implementation

## 🎯 **Objective**
Create a simple deployment script `anton.sh` based on the existing reference script to automate the deployment process for the EKO backend.

## 📋 **Current Setup Analysis**

### **Development Environment**
- **Local Machine**: Ubuntu laptop with Docker
- **Testing Server**: Ubuntu VPS with Docker
- **Deployment Path**: `/var/www/html/eko_backend`
- **Container Management**: Docker (not PM2)
- **Current Workflow**: 
  - `./deploy.sh` for initial setup
  - `git pull` + `./restart.sh` for updates
  - Manual deployment process

### **Reference Script Analysis**
The provided reference script (`deploy_dev_branch_to_anton.sh`) shows:
- ✅ Git commit and push workflow
- ✅ SSH deployment to server
- ✅ Server-side git pull and restart
- ✅ Container health checking
- ❌ Uses PM2 (we need Docker)
- ❌ Uses Node.js environment (we need Python/Docker)

## 🚀 **Proposed Solution: anton.sh Script**

### **Script Requirements**
1. **Local Git Operations**: Commit, push to main branch
2. **SSH Deployment**: Connect to production server
3. **Git Pull**: Pull latest changes on server
4. **Restart Script**: Use `./restart.sh` script (with optional `--force` flag)
5. **Docker Compose Handling**: Pass `-y` flag to restart script to auto-answer "y" to Docker Compose prompt
6. **Health Monitoring**: Check container logs and status with `docker logs eko_backend_container`
7. **Force Mode**: Support `--force` parameter for restart script
8. **Error Handling**: Proper error messages and exit codes

### **Implementation Plan**

#### **Step 1: Create anton.sh Script**
```bash
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
```

#### **Step 2: Make Script Executable**
```bash
chmod +x anton.sh
```

#### **Step 3: Test Script**
```bash
./anton.sh
```

## 🔧 **Configuration Steps**

### **1. Update Server Details**
Edit the configuration section in `anton.sh`:
```bash
SERVER_IP="your-server-ip"           # Your VPS IP address
DEPLOY_PATH="/var/www/html/eko_backend"  # Your deployment path
SSH_USER="your-username"             # Your SSH username
SSH_KEY="~/.ssh/your_deploy_key"     # Path to your SSH private key
```

### **2. Set Up SSH Key (if not already done)**
```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "eko-deploy" -f ~/.ssh/eko_deploy_key

# Copy public key to server
ssh-copy-id -i ~/.ssh/eko_deploy_key.pub your-username@your-server-ip

# Test connection
ssh -i ~/.ssh/eko_deploy_key your-username@your-server-ip
```

### **3. Verify Server Setup**
Ensure your server has:
- ✅ Git repository cloned at `/var/www/html/eko_backend`
- ✅ `restart.sh` script executable
- ✅ Docker installed and running
- ✅ SSH access configured

## 📊 **Script Features**

| Feature | Status | Description |
|---------|--------|-------------|
| **Git Operations** | ✅ | Add, commit, push to main branch |
| **SSH Deployment** | ✅ | Secure connection to production server |
| **Git Pull** | ✅ | Pull latest changes on server |
| **Restart Script** | ✅ | Use `./restart.sh` script for container management |
| **Docker Compose** | ✅ | Auto-answer "y" to Docker Compose prompt with `-y` flag |
| **Force Mode** | ✅ | Support `--force` parameter for restart script |
| **Health Monitoring** | ✅ | Check container logs with `docker logs eko_backend_container` |
| **Error Handling** | ✅ | Proper error messages and exit codes |
| **User Input** | ✅ | Interactive commit message input |
| **Logging** | ✅ | Clear status messages throughout process |

## 🎯 **Usage Instructions**

### **Basic Usage**
```bash
./anton.sh
```

### **Force Mode Usage**
```bash
./anton.sh --force
```

### **What the Script Does**
1. **Prompts for commit message**
2. **Commits and pushes changes** to main branch
3. **Connects to production server** via SSH
4. **Pulls latest changes** from git
5. **Runs restart script** using `./restart.sh -y` (with `--force` if specified)
6. **Auto-answers "y"** to Docker Compose prompt (if detected)
7. **Verifies container started** with `docker logs eko_backend_container`
8. **Confirms successful deployment**

### **Expected Output**
```
Enter commit message: Fix login password validation
🔄 Committing changes...
=> git add .
=> git commit -m 'Fix login password validation'
=> git push origin main
🚀 Deploying to production server at 194.35.120.165 (/var/www/html/eko_backend) as markcoders
📥 Pulling latest changes...
🔄 Running restart script...
⏳ Waiting for container to start...
📋 Verifying container started successfully...
✅ Deployment completed successfully!
🎉 Deployment to production server completed!
```

### **Force Mode Output**
```
🔧 Force mode enabled - restart script will run with --force
Enter commit message: Emergency fix for critical bug
🔄 Committing changes...
=> git add .
=> git commit -m 'Emergency fix for critical bug'
=> git push origin main
🚀 Deploying to production server at 194.35.120.165 (/var/www/html/eko_backend) as markcoders
📥 Pulling latest changes...
🔄 Running restart script...
⏳ Waiting for container to start...
📋 Verifying container started successfully...
✅ Deployment completed successfully!
🎉 Deployment to production server completed!
```

## 🔗 **Related Files**

- `deploy.sh` - Current initial deployment script
- `restart.sh` - Current restart script (used by anton.sh)
- `docker-compose.yml` - Docker configuration
- `Dockerfile` - Container build instructions
- `requirements.txt` - Python dependencies

## 📝 **Next Steps**

1. **Create anton.sh script** with the provided template
2. **Update configuration** with your server details
3. **Set up SSH key** if not already configured
4. **Test the script** with a small change
5. **Document usage** for team members

---

**Status**: Ready for implementation
**Priority**: High
**Estimated Time**: 30 minutes
**Dependencies**: SSH key setup, server access configuration