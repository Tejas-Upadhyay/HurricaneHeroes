#!/bin/bash

# Hurricane Heroes - Deployment Script for AWS EC2
# Run this script on your EC2 instance after initial setup

set -e  # Exit on error

echo "🚀 Starting Hurricane Heroes Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as correct user
if [ "$USER" != "django" ]; then
    echo -e "${YELLOW}Warning: Running as $USER. Should run as 'django' user.${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Navigate to project directory
PROJECT_DIR="$HOME/projects/hurricaneHeroes"
cd "$PROJECT_DIR" || exit 1

echo -e "${GREEN}✓ Project directory: $PROJECT_DIR${NC}"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Update pip
echo -e "${YELLOW}Updating pip...${NC}"
pip install --upgrade pip

# Install/update dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Install production dependencies
echo -e "${YELLOW}Installing production dependencies...${NC}"
pip install gunicorn

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${RED}⚠ .env file not found!${NC}"
    echo "Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env file with your production settings!${NC}"
        read -p "Press Enter after editing .env file..."
    else
        echo -e "${RED}Error: .env.example not found. Please create .env manually.${NC}"
        exit 1
    fi
fi

# Load environment variables
set -a
source .env
set +a

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py migrate --noinput

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Create logs directory
mkdir -p logs
echo -e "${GREEN}✓ Logs directory created${NC}"

# Check if superuser exists
echo -e "${YELLOW}Checking for superuser...${NC}"
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print("⚠ No superuser found. Create one with: python manage.py createsuperuser")
else:
    print("✓ Superuser exists")
EOF

# Restart Gunicorn
echo -e "${YELLOW}Restarting Gunicorn...${NC}"
sudo systemctl restart gunicorn
sudo systemctl status gunicorn --no-pager

# Reload Nginx
echo -e "${YELLOW}Reloading Nginx...${NC}"
sudo nginx -t && sudo systemctl reload nginx

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Check application: http://$(curl -s ifconfig.me)"
echo "2. View logs: sudo journalctl -u gunicorn -f"
echo "3. Check Nginx: sudo systemctl status nginx"

