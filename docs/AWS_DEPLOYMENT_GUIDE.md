# AWS EC2 Deployment Guide - Hurricane Heroes Relief System

Complete step-by-step guide to deploy Django application on AWS EC2 instance.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS EC2 Instance Setup](#aws-ec2-instance-setup)
3. [Server Configuration](#server-configuration)
4. [Application Deployment](#application-deployment)
5. [Web Server Setup (Nginx + Gunicorn)](#web-server-setup-nginx--gunicorn)
6. [SSL Certificate Setup (Optional)](#ssl-certificate-setup-optional)
7. [Domain Configuration](#domain-configuration)
8. [Security Hardening](#security-hardening)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

### Required Accounts & Tools:
- ✅ AWS Account
- ✅ Domain name (optional, can use EC2 public IP)
- ✅ Git installed on local machine
- ✅ SSH client (PuTTY for Windows, Terminal for Mac/Linux)

### Local Project Preparation:
- ✅ Project should be in Git repository (GitHub/GitLab/Bitbucket)
- ✅ All code committed and pushed
- ✅ `requirements.txt` file exists
- ✅ Database backup ready (if migrating existing data)

---

## 2. AWS EC2 Instance Setup

### Step 1: Launch EC2 Instance

1. **Login to AWS Console**
   - Go to https://aws.amazon.com/console/
   - Navigate to **EC2 Dashboard**

2. **Launch Instance**
   - Click **"Launch Instance"**
   - Configure as follows:

#### Instance Configuration:
- **Name**: `hurricane-heroes-production` (or your preferred name)
- **AMI (Amazon Machine Image)**: 
  - Select **Ubuntu Server 22.04 LTS** (Free tier eligible)
  - Architecture: `64-bit (x86)`
- **Instance Type**: 
  - For testing: `t2.micro` (Free tier)
  - For production: `t3.small` or `t3.medium` (recommended)
- **Key Pair**: 
  - Create new key pair or use existing
  - Name: `hurricane-heroes-key`
  - Key pair type: `RSA`
  - Private key file format: `.pem`
  - **⚠️ IMPORTANT**: Download and save the `.pem` file securely
- **Network Settings**: 
  - Create security group: `hurricane-heroes-sg`
  - Allow SSH (port 22) from your IP
  - Allow HTTP (port 80) from anywhere (0.0.0.0/0)
  - Allow HTTPS (port 443) from anywhere (0.0.0.0/0)
- **Storage**: 
  - 20 GB gp3 (minimum recommended)
  - Can increase if needed
- **Advanced Details** (Optional):
  - Add user data script (see below)

3. **Launch Instance**
   - Review settings
   - Click **"Launch Instance"**
   - Wait for instance to be in "Running" state

### Step 2: Configure Security Group

1. Go to **Security Groups** in EC2 Dashboard
2. Select your security group
3. **Inbound Rules** should have:
   ```
   Type        Protocol    Port Range    Source
   SSH         TCP         22            Your IP (or 0.0.0.0/0 for testing)
   HTTP        TCP         80            0.0.0.0/0
   HTTPS       TCP         443           0.0.0.0/0
   ```
4. **Outbound Rules**: Allow all (default)

### Step 3: Get Instance Details

1. Note down:
   - **Public IPv4 address**: `xx.xx.xx.xx`
   - **Instance ID**: `i-xxxxxxxxxxxxx`
   - **Key pair file location**: `hurricane-heroes-key.pem`

---

## 3. Server Configuration

### Step 1: Connect to EC2 Instance

#### For Windows (Using PuTTY):

1. **Convert .pem to .ppk**:
   - Open PuTTYgen
   - Load `hurricane-heroes-key.pem`
   - Click "Save private key" → Save as `hurricane-heroes-key.ppk`

2. **Connect via PuTTY**:
   - Host: `ubuntu@<your-ec2-public-ip>`
   - Port: `22`
   - Connection → SSH → Auth → Browse → Select `.ppk` file
   - Click "Open"

#### For Mac/Linux (Using Terminal):

```bash
# Set correct permissions
chmod 400 hurricane-heroes-key.pem

# Connect to instance
ssh -i hurricane-heroes-key.pem ubuntu@<your-ec2-public-ip>
```

### Step 2: Update System

```bash
# Update package list
sudo apt update

# Upgrade system packages
sudo apt upgrade -y

# Install essential packages
sudo apt install -y python3-pip python3-dev python3-venv nginx git curl
```

### Step 3: Create Application User

```bash
# Create dedicated user for Django app
sudo adduser --disabled-password --gecos "" django

# Add user to sudo group (optional, for admin tasks)
sudo usermod -aG sudo django

# Switch to django user
sudo su - django
```

### Step 4: Setup Python Environment

```bash
# Create project directory
mkdir -p ~/projects
cd ~/projects

# Clone your repository (replace with your repo URL)
git clone https://github.com/yourusername/hurricane-heroes.git
# OR upload files using SCP (see below)

# Navigate to project
cd hurricane-heroes

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 5: Upload Project Files (If not using Git)

#### For Windows (Using WinSCP or FileZilla):
- Use SFTP protocol
- Host: `your-ec2-public-ip`
- Username: `ubuntu`
- Port: `22`
- Private key: Your `.ppk` file

#### For Mac/Linux (Using SCP):

```bash
# From your local machine
scp -i hurricane-heroes-key.pem -r /path/to/your/project/* ubuntu@<ec2-ip>:~/projects/hurricane-heroes/
```

---

## 4. Application Deployment

### Step 1: Install Dependencies

```bash
# Make sure you're in project directory with venv activated
cd ~/projects/hurricane-heroes
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn psycopg2-binary  # PostgreSQL (if using)
# OR keep SQLite (default)
```

### Step 2: Configure Production Settings

```bash
# Create production settings file
nano relief_system/settings_production.py
```

Copy content from `settings_production.py` file (will be created in project).

### Step 3: Environment Variables

```bash
# Create .env file
nano .env
```

Add the following (use strong values):
```env
SECRET_KEY=your-super-secret-key-here-generate-using-django-secret-key-generator
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ec2-ip,localhost
DATABASE_URL=sqlite:///db.sqlite3
```

**Generate Secret Key:**
```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 4: Database Setup

```bash
# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser (optional)
python manage.py createsuperuser
```

### Step 5: Test Application Locally

```bash
# Test with Django development server (temporary)
python manage.py runserver 0.0.0.0:8000

# In another terminal, test from browser
# http://your-ec2-ip:8000
# Press Ctrl+C to stop
```

---

## 5. Web Server Setup (Nginx + Gunicorn)

### Step 1: Configure Gunicorn

```bash
# Create Gunicorn service file
sudo nano /etc/systemd/system/gunicorn.service
```

Add the following content:

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

**Save and exit** (Ctrl+X, then Y, then Enter)

### Step 2: Start Gunicorn Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start Gunicorn
sudo systemctl start gunicorn

# Enable Gunicorn to start on boot
sudo systemctl enable gunicorn

# Check status
sudo systemctl status gunicorn
```

### Step 3: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/hurricane-heroes
```

Add the following:

```nginx
server {
    listen 80;
    server_name your-domain.com your-ec2-ip;

    # Maximum upload size
    client_max_body_size 20M;

    # Static files
    location /static/ {
        alias /home/django/projects/hurricane-heroes/staticfiles/;
    }

    # Media files (if you have media)
    location /media/ {
        alias /home/django/projects/hurricane-heroes/media/;
    }

    # Django application
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/django/projects/hurricane-heroes/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Save and exit**

### Step 4: Enable Nginx Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/hurricane-heroes /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# If test passes, restart Nginx
sudo systemctl restart nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

### Step 5: Configure Firewall

```bash
# Allow Nginx through firewall
sudo ufw allow 'Nginx Full'

# Check firewall status
sudo ufw status
```

---

## 6. SSL Certificate Setup (Optional but Recommended)

### Using Let's Encrypt (Free SSL):

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

Certbot will automatically:
- Configure SSL certificate
- Update Nginx configuration
- Set up auto-renewal

---

## 7. Domain Configuration

### Step 1: Point Domain to EC2

1. **Get EC2 Public IP** (or Elastic IP - recommended)

2. **Create A Record in DNS**:
   - Go to your domain registrar (GoDaddy, Namecheap, etc.)
   - Add DNS record:
     ```
     Type: A
     Name: @ (or leave blank)
     Value: your-ec2-public-ip
     TTL: 3600
     ```

3. **For www subdomain**:
   ```
   Type: A
   Name: www
   Value: your-ec2-public-ip
   TTL: 3600
   ```

### Step 2: Update ALLOWED_HOSTS

```bash
# Edit .env file
nano .env
```

Update:
```env
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-ec2-ip
```

### Step 3: Restart Services

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## 8. Security Hardening

### Step 1: Update ALLOWED_HOSTS in Settings

Make sure production settings have:
```python
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
```

### Step 2: Disable DEBUG Mode

```python
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

### Step 3: Secure Secret Key

Never commit secret key to Git. Always use environment variables.

### Step 4: Configure Firewall Rules

```bash
# Only allow necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Step 5: Regular Updates

```bash
# Set up automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Step 6: Database Backup

Set up automated database backups:

```bash
# Create backup script
nano ~/backup_db.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/django/backups"
mkdir -p $BACKUP_DIR
cd /home/django/projects/hurricane-heroes
source venv/bin/activate
python manage.py dumpdata > $BACKUP_DIR/backup_$DATE.json
# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.json" -mtime +7 -delete
```

```bash
# Make executable
chmod +x ~/backup_db.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/django/backup_db.sh
```

---

## 9. Monitoring & Maintenance

### Useful Commands:

```bash
# Check Gunicorn status
sudo systemctl status gunicorn

# Check Nginx status
sudo systemctl status nginx

# View Gunicorn logs
sudo journalctl -u gunicorn -f

# View Nginx error logs
sudo tail -f /var/log/nginx/error.log

# View Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Check disk space
df -h

# Check memory usage
free -h
```

### Application Logs:

```bash
# Django application logs (if configured)
tail -f /home/django/projects/hurricane-heroes/logs/django.log
```

---

## 10. Troubleshooting

### Issue: 502 Bad Gateway

**Solution:**
```bash
# Check if Gunicorn is running
sudo systemctl status gunicorn

# Check socket file permissions
ls -la /home/django/projects/hurricane-heroes/gunicorn.sock

# Fix permissions if needed
sudo chown django:www-data /home/django/projects/hurricane-heroes/gunicorn.sock
```

### Issue: Static files not loading

**Solution:**
```bash
# Recollect static files
cd /home/django/projects/hurricane-heroes
source venv/bin/activate
python manage.py collectstatic --noinput

# Check Nginx static file path
sudo nginx -t
```

### Issue: Permission denied errors

**Solution:**
```bash
# Fix ownership
sudo chown -R django:www-data /home/django/projects/hurricane-heroes
sudo chmod -R 755 /home/django/projects/hurricane-heroes
```

### Issue: Database connection errors

**Solution:**
```bash
# Check database file permissions
ls -la db.sqlite3
sudo chown django:django db.sqlite3
```

### Issue: Can't connect via SSH

**Solution:**
- Check Security Group rules (port 22)
- Verify key pair file permissions
- Check instance status in AWS Console

---

## 📝 Quick Deployment Checklist

- [ ] EC2 instance launched and running
- [ ] Security group configured (ports 22, 80, 443)
- [ ] Connected to instance via SSH
- [ ] System packages updated
- [ ] Python and dependencies installed
- [ ] Project files uploaded/cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Production settings configured
- [ ] Environment variables set (.env file)
- [ ] Database migrations run
- [ ] Static files collected
- [ ] Superuser created (if needed)
- [ ] Gunicorn service configured and running
- [ ] Nginx configured and running
- [ ] Firewall rules configured
- [ ] Domain DNS configured (if using domain)
- [ ] SSL certificate installed (if using HTTPS)
- [ ] Application accessible via browser
- [ ] Database backups configured
- [ ] Monitoring set up

---

## 🔗 Useful Resources

- **AWS EC2 Documentation**: https://docs.aws.amazon.com/ec2/
- **Django Deployment**: https://docs.djangoproject.com/en/stable/howto/deployment/
- **Gunicorn Documentation**: https://docs.gunicorn.org/
- **Nginx Documentation**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/

---

## 💰 Cost Estimation

### Free Tier (First 12 months):
- **EC2 t2.micro**: Free (750 hours/month)
- **Storage (20GB)**: Free
- **Data Transfer**: 15GB free/month

### Paid Tier:
- **EC2 t3.small**: ~$15/month
- **Storage (20GB)**: ~$2/month
- **Data Transfer**: ~$0.09/GB after free tier

**Total Estimated Cost**: $0-20/month (depending on usage)

---

## 📞 Support

If you encounter any issues:
1. Check logs: `sudo journalctl -u gunicorn -f`
2. Verify configuration: `sudo nginx -t`
3. Check service status: `sudo systemctl status gunicorn nginx`
4. Review this guide's troubleshooting section

---

**Last Updated**: December 2024
**Version**: 1.0

