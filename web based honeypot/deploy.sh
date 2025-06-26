#!/bin/bash

# Honeypot Deployment and Management Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}==== $1 ====${NC}"
}

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Function to create necessary directories
setup_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs data
    chmod 755 logs data
}

# Function to build and deploy honeypot
deploy() {
    print_header "Deploying Web Honeypot"
    
    check_docker
    setup_directories
    
    print_status "Building Docker image..."
    docker-compose build
    
    print_status "Starting honeypot container..."
    docker-compose up -d
    
    print_status "Waiting for honeypot to start..."
    sleep 5
    
    if docker-compose ps | grep -q "Up"; then
        print_status "Honeypot deployed successfully!"
        print_status "Access points:"
        echo "  - Main interface: http://localhost:8080"
        echo "  - Admin panel: http://localhost:8080/admin"
        echo "  - Logs viewer: http://localhost:8080/honeypot/admin/logs"
        echo ""
        print_status "Monitoring:"
        echo "  - View logs: ./deploy.sh logs"
        echo "  - View stats: ./deploy.sh stats"
        echo "  - Stop honeypot: ./deploy.sh stop"
    else
        print_error "Failed to deploy honeypot"
        exit 1
    fi
}

# Function to stop honeypot
stop() {
    print_header "Stopping Web Honeypot"
    docker-compose down
    print_status "Honeypot stopped"
}

# Function to restart honeypot
restart() {
    print_header "Restarting Web Honeypot"
    docker-compose restart
    print_status "Honeypot restarted"
}

# Function to view logs
view_logs() {
    print_header "Honeypot Logs"
    if [ -f logs/honeypot.log ]; then
        tail -n 50 logs/honeypot.log
    else
        print_warning "No log file found yet"
    fi
}

# Function to view live logs
live_logs() {
    print_header "Live Honeypot Logs"
    docker-compose logs -f honeypot
}

# Function to show statistics
show_stats() {
    print_header "Honeypot Statistics"
    
    if [ -f data/honeypot.db ]; then
        # Use sqlite3 to query the database
        echo "Total interactions:"
        sqlite3 data/honeypot.db "SELECT COUNT(*) FROM interactions;"
        
        echo -e "\nTop IP addresses:"
        sqlite3 data/honeypot.db "SELECT ip_address, COUNT(*) as count FROM interactions GROUP BY ip_address ORDER BY count DESC LIMIT 10;" | column -t -s '|'
        
        echo -e "\nMost targeted paths:"
        sqlite3 data/honeypot.db "SELECT path, COUNT(*) as count FROM interactions GROUP BY path ORDER BY count DESC LIMIT 10;" | column -t -s '|'
        
        echo -e "\nLogin attempts:"
        sqlite3 data/honeypot.db "SELECT COUNT(*) FROM interactions WHERE interaction_type LIKE '%login%';"
        
        echo -e "\nRecent activity (last 10):"
        sqlite3 data/honeypot.db "SELECT timestamp, ip_address, method, path FROM interactions ORDER BY timestamp DESC LIMIT 10;" | column -t -s '|'
    else
        print_warning "No database file found yet"
    fi
}

# Function to show honeypot status
status() {
    print_header "Honeypot Status"
    docker-compose ps
    
    if docker-compose ps | grep -q "Up"; then
        print_status "Honeypot is running"
        
        # Check if port is accessible
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 > /dev/null; then
            print_status "Web interface is accessible"
        else
            print_warning "Web interface may not be accessible"
        fi
    else
        print_warning "Honeypot is not running"
    fi
}

# Function to monitor attacks in real-time
monitor() {
    print_header "Real-time Attack Monitor"
    print_status "Monitoring for attacks..."
    
    # Monitor log file for new entries
    tail -f logs/honeypot.log 2>/dev/null | while read line; do
        if echo "$line" | grep -q "login_attempt\|sensitive_file_access"; then
            echo -e "${RED}[ATTACK]${NC} $line"
        elif echo "$line" | grep -q "WARNING"; then
            echo -e "${YELLOW}[SUSPICIOUS]${NC} $line"
        else
            echo "$line"
        fi
    done
}

# Function to show help
show_help() {
    echo "Web Honeypot Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy    - Build and deploy the honeypot"
    echo "  stop      - Stop the honeypot"
    echo "  restart   - Restart the honeypot"
    echo "  status    - Show honeypot status"
    echo "  logs      - View recent logs"
    echo "  live-logs - View live logs"
    echo "  monitor   - Monitor attacks in real-time"
    echo "  stats     - Show interaction statistics"
    echo "  help      - Show this help message"
}

# Main script logic
case "${1:-}" in
    deploy)
        deploy
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        view_logs
        ;;
    live-logs)
        live_logs
        ;;
    monitor)
        monitor
        ;;
    stats)
        show_stats
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac