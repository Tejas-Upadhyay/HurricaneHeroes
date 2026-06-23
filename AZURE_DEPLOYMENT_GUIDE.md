# Azure Deployment Guide - Hurricane Heroes Relief System

This guide outlines the step-by-step process for deploying the Django-based Hurricane Heroes Relief System on **Microsoft Azure**. 

We recommend **Option A: Azure App Service (Linux Web App)** as it is a fully managed Platform-as-a-Service (PaaS) that handles operating system updates, auto-scaling, and SSL certificates automatically. However, we also provide **Option B: Azure Virtual Machines** if you prefer a traditional virtual machine setup similar to your previous AWS EC2 instance.

---

## 📋 Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Option A: Deploying on Azure App Service (Recommended)](#2-option-a-deploying-on-azure-app-service-recommended)
   - [Step 1: Create the Web App](#step-1-create-the-web-app)
   - [Step 2: Configure Environment Variables (Application Settings)](#step-2-configure-environment-variables-application-settings)
   - [Step 3: Configure Startup Command](#step-3-configure-startup-command)
   - [Step 4: Database Setup (SQLite vs. PostgreSQL)](#step-4-database-setup-sqlite-vs-postgresql)
3. [Option B: Deploying on Azure Virtual Machine (Ubuntu 22.04)](#3-option-b-deploying-on-azure-virtual-machine-ubuntu-22-04)
   - [Step 1: Create Azure VM](#step-1-create-azure-vm)
   - [Step 2: Server Setup & Configuration](#step-2-server-setup--configuration)
   - [Step 3: Gunicorn & Nginx Configuration](#step-3-gunicorn--nginx-configuration)
4. [Continuous Deployment (CI/CD) via GitHub Actions](#4-continuous-deployment-cicd-via-github-actions)
5. [Monitoring and Maintenance](#5-monitoring-and-maintenance)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Prerequisites

Before starting, ensure you have:
*   An active **Azure Account** ([Create free Azure account](https://azure.microsoft.com/free/)).
*   A **GitHub Repository** containing the codebase.
*   Your project configured with a `requirements.txt` file (already included).
*   The `startup.sh` script present in the project root directory (already included).

---

## 2. Option A: Deploying on Azure App Service (Recommended)

Azure App Service allows you to run Django on a pre-configured Python container without managing Gunicorn, Nginx, or SSH keypairs.

### Step 1: Create the Web App

1.  Log in to the [Azure Portal](https://portal.azure.com/).
2.  Click **"Create a resource"** and search for **"Web App"**.
3.  Configure the **Basics** tab:
    *   **Subscription**: Select your active Azure subscription.
    *   **Resource Group**: Create new (e.g., `hurricane-heroes-rg`).
    *   **Name**: Enter a unique name (e.g., `hurricane-heroes-app`). This determines your default URL: `https://<app-name>.azurewebsites.net`.
    *   **Publish**: Select `Code`.
    *   **Runtime stack**: Select `Python 3.11` (or `Python 3.12`).
    *   **Operating System**: Select `Linux`.
    *   **Region**: Select the region closest to your users (e.g., `East US` or `South Central US`).
    *   **Pricing Plan**: Choose `Basic B1` or `Premium V3` (free tier `F1` is also available for testing, though it has resources limits).
4.  Click **Review + Create**, then click **Create**. Wait for deployment to finish.

### Step 2: Configure Environment Variables (Application Settings)

Instead of saving secret variables in `.env` files which shouldn't be committed to Git, Azure App Service loads environmental variables from Application Settings.

1.  Go to your Web App resource in the Azure Portal.
2.  In the left menu under **Settings**, click **Environment variables**.
3.  Add the following variables:

| Name | Value | Description |
| :--- | :--- | :--- |
| `DJANGO_ENV` | `production` | Enables production settings configurations. |
| `SECRET_KEY` | *Your Random Secret Key* | Secret key for cryptographic signing. |
| `DEBUG` | `False` | Disables debug mode in production. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,<your-app-name>.azurewebsites.net,yourdomain.com` | List of host/domain names this site can serve. |
| `DB_ENGINE` | `django.db.backends.sqlite3` | Database engine (Use `django.db.backends.postgresql` if using Azure PostgreSQL). |

4.  Click **Apply** at the bottom of the page to save the settings.

### Step 3: Configure Startup Command

Since Django requires migrations and static file compilation on startup, we must configure App Service to use our custom `startup.sh` script.

1.  In your Web App, go to **Settings** -> **Configuration** -> **General settings**.
2.  In the **Startup Command** box, enter:
    ```bash
    /home/site/wwwroot/startup.sh
    ```
3.  Click **Save**.

### Step 4: Database Setup (SQLite vs. PostgreSQL)

*   **SQLite (Default)**:
    Azure App Service has a persistent storage directory mounted at `/home`. By default, files stored inside `/home` are preserved across app restarts.
    To use SQLite:
    *   Ensure your SQLite path points to the persistent directory. In `settings.py`, the default setting is:
        `'NAME': BASE_DIR / 'db.sqlite3'`
        This is typically located under `/home/site/wwwroot/db.sqlite3` in App Service, which is persistent.
*   **Azure Database for PostgreSQL (Recommended for Scale)**:
    1.  Create an **Azure Database for PostgreSQL flexible server** in the Azure Portal.
    2.  Configure database credentials in your Web App environment variables:
        *   `DB_NAME` = `hurricane_heroes`
        *   `DB_USER` = `db_admin`
        *   `DB_PASSWORD` = *your_password*
        *   `DB_HOST` = `<your-postgresql-server>.postgres.database.azure.com`
        *   `DB_PORT` = `5432`
    3.  In `settings_production.py`, uncomment the PostgreSQL configuration block to parse these environment variables.

---

## 3. Option B: Deploying on Azure Virtual Machine (Ubuntu 22.04)

If you prefer an exact replication of the AWS EC2 VM setup:

### Step 1: Create Azure VM

1.  In Azure Portal, click **"Create a resource"** -> **"Virtual Machine"**.
2.  Configure VM:
    *   **Resource Group**: Select your resource group.
    *   **Virtual machine name**: `hurricane-heroes-vm`
    *   **Region**: Select your region.
    *   **Image**: `Ubuntu Server 22.04 LTS - x64 Gen2`
    *   **Size**: `Standard_B1s` (1 vCPU, 1 GiB memory - eligible for free trial) or `Standard_B2s` for production.
    *   **Authentication type**: `SSH public key`
    *   **Username**: `azureuser`
    *   **SSH public key source**: `Generate new key pair` (Name it `hurricane-heroes-key`)
3.  Under **Inbound port rules**:
    *   Allow **SSH (22)**, **HTTP (80)**, and **HTTPS (443)**.
4.  Click **Review + Create** -> **Create**.
5.  Download the private key (`.pem` file) and keep it secure.

### Step 2: Server Setup & Configuration

Connect to your Azure VM using Terminal (Mac) or PuTTY (Windows):

```bash
# Secure the downloaded key
chmod 400 hurricane-heroes-key.pem

# SSH into the VM (Get public IP from Azure Portal VM Dashboard)
ssh -i hurricane-heroes-key.pem azureuser@<azure-vm-public-ip>
```

Once connected, run the installation script:

```bash
# Update and upgrade system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3-pip python3-dev python3-venv nginx git curl

# Create application user
sudo adduser --disabled-password --gecos "" django
sudo usermod -aG sudo django
sudo su - django

# Create project directory
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/Tejas-Upadhyay/HurricaneHeroes.git
cd HurricaneHeroes

# Configure Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### Step 3: Gunicorn & Nginx Configuration

This configuration mirrors the AWS deployment structure.

1.  **Gunicorn Systemd Service**:
    Create the service file:
    ```bash
    sudo nano /etc/systemd/system/gunicorn.service
    ```
    Add the configuration:
    ```ini
    [Unit]
    Description=gunicorn daemon for Hurricane Heroes
    After=network.target

    [Service]
    User=django
    Group=www-data
    WorkingDirectory=/home/django/projects/HurricaneHeroes
    ExecStart=/home/django/projects/HurricaneHeroes/venv/bin/gunicorn \
        --access-logfile - \
        --workers 3 \
        --bind unix:/home/django/projects/HurricaneHeroes/gunicorn.sock \
        relief_system.wsgi:application

    [Install]
    WantedBy=multi-user.target
    ```
    Enable and start the service:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start gunicorn
    sudo systemctl enable gunicorn
    ```

2.  **Nginx Server Block**:
    Create Nginx config file:
    ```bash
    sudo nano /etc/nginx/sites-available/hurricane-heroes
    ```
    Add configuration:
    ```nginx
    server {
        listen 80;
        server_name your-domain.com <azure-vm-public-ip>;

        client_max_body_size 20M;

        location /static/ {
            alias /home/django/projects/HurricaneHeroes/staticfiles/;
        }

        location / {
            include proxy_params;
            proxy_pass http://unix:/home/django/projects/HurricaneHeroes/gunicorn.sock;
        }
    }
    ```
    Activate configuration and reload Nginx:
    ```bash
    sudo ln -s /etc/nginx/sites-available/hurricane-heroes /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx
    ```

---

## 4. Continuous Deployment (CI/CD) via GitHub Actions

We have preconfigured a Continuous Deployment workflow in `.github/workflows/azure-deploy.yml` which deploys the app dynamically every time you push to the `main` branch.

To activate the workflow:
1.  Open your **Web App** in the Azure Portal.
2.  Click **"Get publish profile"** from the top dashboard menu. This downloads a `.PublishSettings` XML file.
3.  Go to your **GitHub Repository** -> **Settings** -> **Secrets and variables** -> **Actions**.
4.  Click **"New repository secret"**.
5.  Name the secret: `AZURE_WEBAPP_PUBLISH_PROFILE`.
6.  Open the downloaded `.PublishSettings` file in a text editor, copy its entire contents, and paste it into the GitHub secret text box.
7.  Click **Add secret**.
8.  Now, pushing commits to the `main` branch will trigger an automated build and deploy script.

---

## 5. Monitoring and Maintenance

### For App Service (Linux Web App):
*   **Application Logs**: Go to **Monitoring** -> **Log stream** to view console logs (STDOUT/STDERR) in real-time.
*   **App Service Logs**: Enable filesystem storage logging via **Monitoring** -> **App Service logs** to record error files.
*   **Diagnostic Logs**: Access using the Azure CLI:
    ```bash
    az webapp log tail --name <app-name> --resource-group <resource-group-name>
    ```

### For Azure Virtual Machine:
*   Check Gunicorn status: `sudo systemctl status gunicorn`
*   View Gunicorn live logs: `sudo journalctl -u gunicorn -f`
*   View Nginx error logs: `sudo tail -f /var/log/nginx/error.log`

---

## 6. Troubleshooting

*   **Error: `Application Error` page on Azure Web App**:
    *   Verify the **Startup Command** is exactly set to `/home/site/wwwroot/startup.sh`.
    *   Verify that your environment variables (`SECRET_KEY`, `DJANGO_ENV=production`) are correctly applied.
    *   Verify `DJANGO_ENV` is set to `production` (case sensitive).
*   **Error: Static CSS files are not loading (404 errors)**:
    *   Ensure Django's `collectstatic` was executed successfully. Check the startup logs to see if it ran.
    *   Check that `STATIC_ROOT` and `STATIC_URL` configurations are correct in `settings_production.py`.
*   **Error: Database is locked or migrations failed**:
    *   SQLite locks database files if multiple write processes occur simultaneously. Consider migrating database variables to PostgreSQL for high availability.
