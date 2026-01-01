# 🚀 Quick Start Deployment Guide

This is a condensed version of the full deployment guide. For detailed instructions, see `AWS_DEPLOYMENT_GUIDE.md`.

## Prerequisites Checklist

- [ ] AWS Account created
- [ ] EC2 instance launched (Ubuntu 22.04 LTS)
- [ ] Security group configured (ports 22, 80, 443)
- [ ] Key pair downloaded (.pem file)
- [ ] Project pushed to Git repository

## Step 1: Connect to EC2

```bash
# Windows (PuTTY): Convert .pem to .ppk and connect
# Mac/Linux:
chmod 400 hurricane-heroes-key.pem
ssh -i hurricane-heroes-key.pem ubuntu@<your-ec2-ip>
```

## Step 2: Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-dev python3-venv nginx git

# Create user
sudo adduser --disabled-password --gecos "" django
sudo usermod -aG sudo django
sudo su - django
```

## Step 3: Deploy Application

```bash
# Create project directory
mkdir -p ~/projects && cd ~/projects

# Clone repository (or upload files)
git clone https://github.com/yourusername/hurricane-heroes.git
cd hurricane-heroes

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
cp env.example .env
nano .env  # Edit with your values

# Generate secret key
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Copy output to .env file as SECRET_KEY

# Setup database
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## Step 4: Configure Gunicorn

```bash
# Create service file
sudo nano /etc/systemd/system/gunicorn.service
```

Paste this content (adjust paths if needed):

```ini
[Unit]
Description=gunicorn daemon for Hurricane Heroes
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/home/django/projects/hurricane-heroes
ExecStart=/home/django/projects/hurricane-heroes/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/home/django/projects/hurricane-heroes/gunicorn.sock \
    relief_system.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

## Step 5: Configure Nginx

```bash
# Create configuration
sudo nano /etc/nginx/sites-available/hurricane-heroes
```

Copy content from `nginx.conf.example` and update paths/domain.

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/hurricane-heroes /etc/nginx/sites-enabled/

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## Step 6: Setup Firewall

```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## Step 7: Test Application

Open browser: `http://your-ec2-ip`

## Step 8: Setup SSL (Optional)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Troubleshooting

```bash
# Check Gunicorn logs
sudo journalctl -u gunicorn -f

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Check permissions
sudo chown -R django:www-data /home/django/projects/hurricane-heroes
```

## Next Steps

1. Point your domain to EC2 IP (A record)
2. Update ALLOWED_HOSTS in .env
3. Setup automated backups
4. Configure monitoring
5. Review security settings

For detailed instructions, see `AWS_DEPLOYMENT_GUIDE.md`.

