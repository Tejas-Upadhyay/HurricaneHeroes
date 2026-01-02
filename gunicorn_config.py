# Gunicorn configuration file for Hurricane Heroes
# Reference: https://docs.gunicorn.org/en/stable/settings.html

import multiprocessing
import os

# Server socket
bind = "unix:/home/django/projects/hurricaneHeroes/gunicorn.sock"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "hurricaneHeroes"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = "django"
group = "www-data"
tmp_upload_dir = None

# SSL (if using HTTPS directly with Gunicorn)
# keyfile = None
# certfile = None

