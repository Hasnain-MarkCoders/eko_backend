#!/bin/bash

# Eko Backend Redeploy Script - Complete Clean Rebuild
# This script performs a complete redeploy by stopping containers, removing them,
# removing images, and rebuilding everything from scratch

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_step() { echo -e "${PURPLE}🔄 $1${NC}"; }

echo "🚀 Starting Eko Backend complete redeploy..."

# Check for non-interactive mode
NON_INTERACTIVE=false
FORCE_CLEANUP=false
if [[ "$1" == "--non-interactive" ]] || [[ "$1" == "-y" ]]; then
    NON_INTERACTIVE=true
    print_info "Non-interactive mode enabled"
fi

if [[ "$1" == "--force" ]] || [[ "$2" == "--force" ]]; then
    FORCE_CLEANUP=true
    print_warning "Force cleanup mode enabled - will remove all related containers and images"
fi

# Function to detect available container runtimes
detect_container_runtimes() {
    local runtimes=()
    
    if command -v docker &> /dev/null && docker --version &> /dev/null; then
        runtimes+=("docker")
    fi
    
    if command -v podman &> /dev/null && podman --version &> /dev/null; then
        runtimes+=("podman")
    fi
    
    printf '%s\n' "${runtimes[@]}"
}

# Function to select container runtime
select_container_runtime() {
    local available_runtimes=("$@")
    local runtime=""
    
    if [ ${#available_runtimes[@]} -eq 0 ]; then
        print_error "No container runtime found!" >&2
        echo "Please install either Docker or Podman to continue." >&2
        echo "  - Docker: https://docs.docker.com/get-docker/" >&2
        echo "  - Podman: https://podman.io/getting-started/installation" >&2
        exit 1
    elif [ ${#available_runtimes[@]} -eq 1 ]; then
        runtime="${available_runtimes[0]}"
        print_info "Detected container runtime: $runtime" >&2
    else
        print_info "Multiple container runtimes detected:" >&2
        for i in "${!available_runtimes[@]}"; do
            echo "  $((i+1)). ${available_runtimes[i]}" >&2
        done
        
        if [ "$NON_INTERACTIVE" = true ]; then
            # In non-interactive mode, prefer docker over podman
            if [[ " ${available_runtimes[*]} " =~ " docker " ]]; then
                runtime="docker"
                print_info "Non-interactive mode: Auto-selected docker" >&2
            else
                runtime="${available_runtimes[0]}"
                print_info "Non-interactive mode: Auto-selected ${available_runtimes[0]}" >&2
            fi
        else
            while true; do
                read -p "Please select a container runtime (1-${#available_runtimes[@]}): " choice
                if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#available_runtimes[@]} ]; then
                    runtime="${available_runtimes[$((choice-1))]}"
                    break
                else
                    print_error "Invalid choice. Please enter a number between 1 and ${#available_runtimes[@]}." >&2
                fi
            done
        fi
    fi
    
    print_success "Selected container runtime: $runtime" >&2
    printf '%s' "$runtime"
}

# Function to check if container runtime is available
check_runtime_available() {
    local runtime="$1"
    if ! command -v "$runtime" &> /dev/null; then
        print_error "$runtime is not available!"
        exit 1
    fi
}

# Function to check if container runtime daemon is running
check_runtime_daemon() {
    local runtime="$1"
    
    if [ "$runtime" = "docker" ]; then
        if ! docker info &> /dev/null; then
            print_warning "Docker daemon is not running. Attempting to start..."
            if command -v systemctl &> /dev/null; then
                sudo systemctl start docker 2>/dev/null || true
                sleep 2
                if ! docker info &> /dev/null; then
                    print_error "Docker daemon failed to start. Please start Docker manually."
                    exit 1
                fi
            else
                print_error "Docker daemon is not running. Please start Docker manually."
                exit 1
            fi
        fi
    elif [ "$runtime" = "podman" ]; then
        if ! podman info &> /dev/null; then
            print_warning "Podman daemon is not running. Attempting to start..."
            if command -v systemctl &> /dev/null; then
                sudo systemctl start podman 2>/dev/null || true
                sleep 2
                if ! podman info &> /dev/null; then
                    print_warning "Podman daemon failed to start, but continuing (rootless mode might work)..."
                fi
            fi
        fi
    fi
}

# Function to stop and remove all Eko Backend containers
stop_and_remove_containers() {
    local runtime="$1"
    print_step "Stopping and removing all Eko Backend containers..."
    
    # Stop all containers with eko_backend in the name
    local containers=$($runtime ps -a --filter "name=eko_backend" --format "{{.Names}}" 2>/dev/null || true)
    if [ -n "$containers" ]; then
        echo "$containers" | while read -r container; do
            if [ -n "$container" ]; then
                print_info "Stopping container: $container"
                $runtime stop "$container" 2>/dev/null || true
                print_info "Removing container: $container"
                $runtime rm "$container" 2>/dev/null || true
            fi
        done
        print_success "All Eko Backend containers stopped and removed"
    else
        print_info "No Eko Backend containers found to remove"
    fi
}

# Function to remove Eko Backend images (only with --force flag)
remove_images() {
    local runtime="$1"
    
    if [ "$FORCE_CLEANUP" = true ]; then
        print_step "Removing Eko Backend images (force cleanup enabled)..."
        
        # Remove images with eko_backend in the name
        local images=$($runtime images --filter "reference=eko_backend*" --format "{{.Repository}}:{{.Tag}}" 2>/dev/null || true)
        if [ -n "$images" ]; then
            echo "$images" | while read -r image; do
                if [ -n "$image" ]; then
                    print_info "Removing image: $image"
                    $runtime rmi "$image" 2>/dev/null || true
                fi
            done
            print_success "All Eko Backend images removed"
        else
            print_info "No Eko Backend images found to remove"
        fi
        
        # Also remove any dangling images
        print_info "Removing dangling images..."
        $runtime image prune -f 2>/dev/null || true
    else
        print_info "Skipping image removal (use --force to remove images for complete cleanup)"
    fi
}

# Function to remove unused volumes (optional, with confirmation)
remove_volumes() {
    local runtime="$1"
    
    if [ "$FORCE_CLEANUP" = true ]; then
        print_step "Removing unused volumes..."
        $runtime volume prune -f 2>/dev/null || true
        print_success "Unused volumes removed"
    else
        print_info "Skipping volume cleanup (use --force to remove unused volumes)"
    fi
}

# Function to remove unused networks (optional, with confirmation)
remove_networks() {
    local runtime="$1"
    
    if [ "$FORCE_CLEANUP" = true ]; then
        print_step "Removing unused networks..."
        $runtime network prune -f 2>/dev/null || true
        print_success "Unused networks removed"
    else
        print_info "Skipping network cleanup (use --force to remove unused networks)"
    fi
}

# Function to check if docker-compose is available and preferred
check_docker_compose() {
    local runtime="$1"
    
    if [ "$runtime" = "docker" ] && command -v docker-compose &> /dev/null; then
        if [ -f "docker-compose.yml" ]; then
            if [ "$NON_INTERACTIVE" = true ]; then
                echo "docker-compose"
            else
                read -p "Docker Compose detected. Use docker-compose for deployment? (y/n): " use_compose
                if [[ "$use_compose" =~ ^[Yy]$ ]]; then
                    echo "docker-compose"
                else
                    echo "docker"
                fi
            fi
        else
            echo "docker"
        fi
    else
        echo "$runtime"
    fi
}

# Function to build and deploy with docker-compose
deploy_with_compose() {
    print_step "Building and deploying with docker-compose..."
    
    # Build and start services
    docker-compose down --remove-orphans 2>/dev/null || true
    docker-compose build --no-cache
    docker-compose up -d
    
    print_success "Deployment completed with docker-compose"
}

# Function to build and deploy with standalone docker
deploy_with_docker() {
    local runtime="$1"
    print_step "Building and deploying with $runtime..."
    
    # Build the image (with cache for faster builds)
    print_info "Building container image with $runtime..."
    if [ "$FORCE_CLEANUP" = true ]; then
        print_info "Force cleanup enabled - building without cache..."
        $runtime build --no-cache -t eko_backend .
    else
        print_info "Building with cache for faster deployment..."
        $runtime build -t eko_backend .
    fi
    
    # Run the container
    print_info "Starting container with $runtime..."
    $runtime run -d \
        --name eko_backend_container \
        --env-file .env \
        -p 9753:8000 \
        --restart unless-stopped \
        eko_backend
}

# Function to check deployment status
check_deployment_status() {
    local runtime="$1"
    local deployment_method="$2"
    
    print_step "Checking deployment status..."
    sleep 5
    
    if [ "$deployment_method" = "docker-compose" ]; then
        if docker-compose ps | grep -q "Up"; then
            print_success "Docker Compose services started successfully!"
            echo "🌐 API is available at: http://localhost:9753"
            echo "📋 Service logs: docker-compose logs -f"
            echo "🛑 To stop services: docker-compose down"
        else
            print_error "Docker Compose services failed to start. Check logs:"
            docker-compose logs
            exit 1
        fi
    else
        if $runtime ps | grep -q eko_backend_container; then
            print_success "Container started successfully!"
            echo "🌐 API is available at: http://localhost:9753"
            echo "📋 Container logs: $runtime logs eko_backend_container"
            echo "🛑 To stop container: $runtime stop eko_backend_container"
            echo "🗑️  To remove container: $runtime rm eko_backend_container"
        else
            print_error "Container failed to start. Check logs:"
            $runtime logs eko_backend_container
            exit 1
        fi
    fi
}

# Function to show help
show_help() {
    echo "Eko Backend Redeploy Script - Complete Clean Rebuild"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -y, --non-interactive    Run in non-interactive mode (auto-select runtime)"
    echo "  --force                  Force cleanup of all unused resources (volumes, networks)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "This script will:"
    echo "  1. Stop and remove all Eko Backend containers"
    echo "  2. Optionally remove images (only with --force flag)"
    echo "  3. Optionally clean up unused volumes and networks (with --force)"
    echo "  4. Rebuild the application (with cache for speed)"
    echo "  5. Deploy the new version"
    echo ""
    echo "Examples:"
    echo "  $0                      # Interactive mode with basic cleanup"
    echo "  $0 -y                   # Non-interactive mode"
    echo "  $0 --force              # Force cleanup of all unused resources"
    echo "  $0 -y --force           # Non-interactive with force cleanup"
}

# Main redeploy logic
main() {
    # Check for help flag
    if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        show_help
        exit 0
    fi
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        echo "Please create a .env file based on .env.example with your Firebase credentials."
        echo "You can copy the example: cp .env.example .env"
        exit 1
    fi
    
    # Detect and select container runtime
    local available_runtimes=($(detect_container_runtimes))
    local selected_runtime=$(select_container_runtime "${available_runtimes[@]}")
    
    # Verify the selected runtime is available
    check_runtime_available "$selected_runtime"
    
    # Check if daemon is running
    check_runtime_daemon "$selected_runtime"
    
    # Perform cleanup and rebuild
    if [ "$FORCE_CLEANUP" = true ]; then
        print_warning "This will perform a complete cleanup and rebuild. This may take several minutes."
    else
        print_info "This will perform a fast rebuild using Docker cache. This should be much faster."
    fi
    
    # Cleanup phase
    stop_and_remove_containers "$selected_runtime"
    remove_images "$selected_runtime"
    remove_volumes "$selected_runtime"
    remove_networks "$selected_runtime"
    
    # Determine deployment method
    local deployment_method=$(check_docker_compose "$selected_runtime")
    
    # Deploy phase
    if [ "$deployment_method" = "docker-compose" ]; then
        deploy_with_compose
    else
        deploy_with_docker "$selected_runtime"
    fi
    
    # Check deployment status
    check_deployment_status "$selected_runtime" "$deployment_method"
    
    print_success "🎉 Redeploy completed successfully!"
}

# Run main function
main "$@"
