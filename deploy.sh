#!/bin/bash

# Eko Backend Deployment Script - Intelligent Container Runtime Detection

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

echo "🚀 Starting Eko Backend deployment..."

# Check for non-interactive mode
NON_INTERACTIVE=false
if [[ "$1" == "--non-interactive" ]] || [[ "$1" == "-y" ]]; then
    NON_INTERACTIVE=true
    print_info "Non-interactive mode enabled"
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
    # Return only the runtime name
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

# Function to stop and remove existing container
stop_existing_container() {
    local runtime="$1"
    print_info "Stopping existing container..."
    $runtime stop eko_backend_container 2>/dev/null || true
    $runtime rm eko_backend_container 2>/dev/null || true
}

# Function to build container image
build_image() {
    local runtime="$1"
    print_info "Building container image with $runtime..."
    $runtime build -t eko_backend .
}

# Function to run container
run_container() {
    local runtime="$1"
    print_info "Starting container with $runtime..."
    $runtime run -d \
        --name eko_backend_container \
        --env-file .env \
        -p 9753:8000 \
        eko_backend
}

# Function to check container status
check_container_status() {
    local runtime="$1"
    sleep 5
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
}

# Function to show help
show_help() {
    echo "Eko Backend Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -y, --non-interactive    Run in non-interactive mode (auto-select runtime)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "This script will:"
    echo "  1. Detect available container runtimes (Docker, Podman)"
    echo "  2. Allow you to select a runtime (or auto-select in non-interactive mode)"
    echo "  3. Build and deploy the Eko Backend application"
    echo ""
    echo "Examples:"
    echo "  $0                      # Interactive mode"
    echo "  $0 -y                   # Non-interactive mode"
    echo "  $0 --non-interactive    # Non-interactive mode"
}

# Main deployment logic
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
    
    # Deploy the application
    stop_existing_container "$selected_runtime"
    build_image "$selected_runtime"
    run_container "$selected_runtime"
    check_container_status "$selected_runtime"
}

# Run main function
main "$@"
