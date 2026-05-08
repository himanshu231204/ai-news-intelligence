#!/bin/bash
# Production deployment helper script

set -e

echo "🚀 AI News Research Agent - Deployment Script"
echo "=============================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Install from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Install from: https://docs.docker.com/compose/install/"
    exit 1
fi

# Function to check if .env exists
check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  .env file not found${NC}"
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please edit .env with your API keys:${NC}"
        echo "   - OPENAI_API_KEY"
        echo "   - GROQ_API_KEY"
        echo "   - TELEGRAM_BOT_TOKEN"
        echo "   - TELEGRAM_CHAT_ID"
        echo ""
        echo "Then run: $0"
        exit 1
    fi
}

# Function to validate required env vars
validate_env() {
    local required_vars=("OPENAI_API_KEY" "GROQ_API_KEY" "TELEGRAM_BOT_TOKEN" "TELEGRAM_CHAT_ID")
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" .env || grep "^$var=$" .env > /dev/null; then
            echo -e "${RED}❌ Required variable not set: $var${NC}"
            exit 1
        fi
    done
}

# Parse command line arguments
COMMAND=${1:-help}

case $COMMAND in
    "up")
        echo -e "${GREEN}🔧 Starting services...${NC}"
        check_env
        validate_env
        docker-compose -f docker/docker-compose.yml up -d
        echo -e "${GREEN}✅ Services started!${NC}"
        echo ""
        echo "Status:"
        docker-compose -f docker/docker-compose.yml ps
        echo ""
        echo "View logs:"
        echo "  docker-compose -f docker/docker-compose.yml logs -f news_agent"
        ;;

    "down")
        echo -e "${GREEN}🛑 Stopping services...${NC}"
        docker-compose -f docker/docker-compose.yml down
        echo -e "${GREEN}✅ Services stopped!${NC}"
        ;;

    "logs")
        echo -e "${GREEN}📋 Showing logs...${NC}"
        docker-compose -f docker/docker-compose.yml logs -f news_agent
        ;;

    "shell")
        echo -e "${GREEN}🐚 Opening container shell...${NC}"
        docker-compose -f docker/docker-compose.yml exec news_agent bash
        ;;

    "test")
        echo -e "${GREEN}🧪 Running single workflow...${NC}"
        check_env
        validate_env
        docker-compose -f docker/docker-compose.yml exec news_agent python main.py --mode workflow
        ;;

    "bot")
        echo -e "${GREEN}🤖 Starting Telegram bot...${NC}"
        check_env
        validate_env
        docker-compose -f docker/docker-compose.yml --profile bot up -d telegram_bot
        docker-compose -f docker/docker-compose.yml logs -f telegram_bot
        ;;

    "status")
        echo -e "${GREEN}📊 Service status...${NC}"
        docker-compose -f docker/docker-compose.yml ps
        ;;

    "clean")
        echo -e "${YELLOW}⚠️  Cleaning up containers and volumes...${NC}"
        read -p "Continue? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose -f docker/docker-compose.yml down -v
            echo -e "${GREEN}✅ Cleanup complete!${NC}"
        fi
        ;;

    "help"|*)
        echo "Usage: ./deploy.sh [command]"
        echo ""
        echo "Commands:"
        echo "  up        - Start all services"
        echo "  down      - Stop all services"
        echo "  logs      - Show scheduler logs"
        echo "  shell     - Open container shell"
        echo "  test      - Run single workflow test"
        echo "  bot       - Start Telegram bot"
        echo "  status    - Show service status"
        echo "  clean     - Remove containers and volumes"
        echo "  help      - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./deploy.sh up          # Start services"
        echo "  ./deploy.sh logs        # View logs"
        echo "  ./deploy.sh test        # Run single test"
        ;;
esac
