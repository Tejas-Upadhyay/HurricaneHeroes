# Hurricane Heroes - Deployment Steps

## Server Info

- **Host:** Azure Virtual Machine "Hosting"
- **IP:** 23.101.174.87
- **User:** azureuser
- **OS:** Ubuntu 24.04
- **Project Path:** /home/azureuser/HurricaneHeroes
- **Domain:** https://southwestfloridahurricaneheroes.com
- **PEM Key:** ~/.ssh/Azur-hurricane-heroes-key.pem

---

## How to Connect

### From Git Bash (local laptop):
```bash
ssh -i ~/.ssh/Azur-hurricane-heroes-key.pem azureuser@23.101.174.87
```

### From VS Code:
1. Open VS Code
2. Ctrl+Shift+P → "Remote-SSH: Connect to Host" → select "hurricane-heroes"
3. Select "Linux" when asked

### SSH Config (~/.ssh/config):
```
Host hurricane-heroes
    HostName 23.101.174.87
    User azureuser
    IdentityFile ~/.ssh/Azur-hurricane-heroes-key.pem
```

### VS Code Settings Required:
In VS Code User Settings JSON, this line is needed:
```json
"remote.SSH.path": "C:\\Program Files\\Git\\usr\\bin\\ssh.exe"
```

---

## Deploy New Code (Routine Update)

### Step 1: Push code from local
```bash
git add .
git commit -m "your message"
git push
```

### Step 2: Connect to Azure and pull
```bash
ssh -i ~/.ssh/Azur-hurricane-heroes-key.pem azureuser@23.101.174.87
cd /home/azureuser/HurricaneHeroes
git pull
```

### Step 3: Run migrations (only if models changed)
```bash
source .venv/bin/activate
python manage.py migrate
```

### Step 4: Restart gunicorn
```bash
pkill -f gunicorn
.venv/bin/gunicorn relief_system.wsgi:application --bind 127.0.0.1:8001 --workers 3 --timeout 60 --daemon
```

### Step 5: Verify
```bash
curl -I http://127.0.0.1:8001
```
Should return `HTTP/1.1 200 OK`

---

## Deploy Database (When local data needs to go to server)

### From local Git Bash:
```bash
scp -i ~/.ssh/Azur-hurricane-heroes-key.pem "<local-path-to-project>/db.sqlite3" azureuser@23.101.174.87:/home/azureuser/HurricaneHeroes/db.sqlite3
```

Then restart gunicorn on the server:
```bash
pkill -f gunicorn
.venv/bin/gunicorn relief_system.wsgi:application --bind 127.0.0.1:8001 --workers 3 --timeout 60 --daemon
```

### Alternative: Use the web UI
1. Local site → Super Admin → Database Management → Export Backup
2. Live site → Super Admin → Database Management → Import Database

---

## Install New Python Packages

If you add a new package to requirements.txt:
```bash
cd /home/azureuser/HurricaneHeroes
source .venv/bin/activate
pip install -r requirements.txt
pkill -f gunicorn
.venv/bin/gunicorn relief_system.wsgi:application --bind 127.0.0.1:8001 --workers 3 --timeout 60 --daemon
```

---

## Troubleshooting

### Site shows "DisallowedHost" error
The domain is not in ALLOWED_HOSTS. Fix:
```bash
sed -i "s/ALLOWED_HOSTS = .*/ALLOWED_HOSTS = ['*']/" relief_system/settings.py
pkill -f gunicorn
.venv/bin/gunicorn relief_system.wsgi:application --bind 127.0.0.1:8001 --workers 3 --timeout 60 --daemon
```

### Gunicorn not running
```bash
cd /home/azureuser/HurricaneHeroes
source .venv/bin/activate
.venv/bin/gunicorn relief_system.wsgi:application --bind 127.0.0.1:8001 --workers 3 --timeout 60 --daemon
```

### Check if gunicorn is running
```bash
ps aux | grep gunicorn
```

### Check error logs
```bash
cd /home/azureuser/HurricaneHeroes
.venv/bin/gunicorn relief_system.wsgi:application --bind 127.0.0.1:8001 --workers 1
```
(Run without --daemon to see errors in terminal)

### PEM key permission issues on Windows
```cmd
icacls "%USERPROFILE%\.ssh\Azur-hurricane-heroes-key.pem" /inheritance:r
icacls "%USERPROFILE%\.ssh\Azur-hurricane-heroes-key.pem" /remove "Authenticated Users"
icacls "%USERPROFILE%\.ssh\Azur-hurricane-heroes-key.pem" /remove "Users"
icacls "%USERPROFILE%\.ssh\Azur-hurricane-heroes-key.pem" /grant:r "%USERNAME%:(R)"
```
Note: Use Git Bash for SSH (Windows CMD has permission issues with PEM files on corporate machines).

### Virtual environment missing
```bash
cd /home/azureuser/HurricaneHeroes
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Quick Deploy Cheat Sheet (copy-paste)

```bash
# Connect
ssh -i ~/.ssh/Azur-hurricane-heroes-key.pem azureuser@23.101.174.87

# Deploy
cd /home/azureuser/HurricaneHeroes
git pull
source .venv/bin/activate
python manage.py migrate
pkill -f gunicorn
.venv/bin/gunicorn relief_system.wsgi:application --bind 127.0.0.1:8001 --workers 3 --timeout 60 --daemon

# Verify
curl -I http://127.0.0.1:8001
```
