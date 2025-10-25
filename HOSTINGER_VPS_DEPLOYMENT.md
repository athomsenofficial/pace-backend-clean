# Deploying PACE FastAPI Backend to Hostinger VPS

## Project Overview

This is a comprehensive deployment guide for the PACE (Promotion Eligibility Processing) FastAPI backend application to a Hostinger VPS.

**Project Type:** FastAPI Backend for Military Promotion Eligibility Processing
**Technology Stack:** Python, FastAPI, Redis, Pandas, ReportLab (PDF generation)

---

## Table of Contents

1. [VPS Requirements](#1-vps-requirements)
2. [Pre-Deployment Setup](#2-pre-deployment-setup)
3. [Required Software Stack](#3-required-software-stack)
4. [Deployment Steps](#4-deployment-steps)
5. [Firewall Configuration](#5-firewall-configuration)
6. [Testing Deployment](#6-testing-deployment)
7. [Monitoring & Maintenance](#7-monitoring--maintenance)
8. [Optional Enhancements](#8-optional-enhancements)
9. [Frontend Deployment](#9-frontend-deployment)
10. [Summary](#10-summary)

---

## 1. VPS Requirements

### Minimum Specs

- **RAM:** 2GB minimum (4GB recommended for processing large rosters)
- **Storage:** 20GB+ (for logs, temporary files, PDFs)
- **OS:** Ubuntu 22.04 LTS (recommended)
- **Python:** 3.8 or higher

---

## 2. Pre-Deployment Setup

You'll need to:

1. Set up SSH access to your Hostinger VPS
2. Configure a domain name pointing to your VPS IP
3. Open ports 80 (HTTP) and 443 (HTTPS) in firewall

---

## 3. Required Software Stack

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Redis
sudo apt install redis-server -y

# Install Nginx (reverse proxy)
sudo apt install nginx -y

# Install Certbot (SSL certificates)
sudo apt install certbot python3-certbot-nginx -y

# Install Supervisor (process management)
sudo apt install supervisor -y
```

---

## 4. Deployment Steps

### Step 1: Transfer Your Code

```bash
# On your VPS, create application directory
sudo mkdir -p /var/www/pace-backend
sudo chown $USER:$USER /var/www/pace-backend

# From your local machine, upload code (choose one method):

# Option A: Git (recommended)
cd /var/www/pace-backend
git clone <your-repo-url> .

# Option B: SCP
scp -r /Users/drew/Coding/pace-backend-clean/* user@your-vps-ip:/var/www/pace-backend/
```

### Step 2: Set Up Python Environment

```bash
cd /var/www/pace-backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
# Create production .env file
nano .env
```

Add:

```env
REDIS_URL=redis://localhost:6379
```

### Step 4: Configure Redis

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf
```

Update these settings:

```conf
# Bind to localhost only (security)
bind 127.0.0.1

# Set maxmemory (e.g., 512MB)
maxmemory 512mb
maxmemory-policy allkeys-lru

# Enable persistence
save 900 1
save 300 10
save 60 10000
```

Restart Redis:

```bash
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### Step 5: Update CORS Origins

Edit `constants.py` and add your production domain:

```python
cors_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://your-domain.com",
    "https://www.your-domain.com",
    # Add your production frontend URL
]
```

### Step 6: Create Supervisor Configuration

```bash
sudo nano /etc/supervisor/conf.d/pace-backend.conf
```

Add:

```ini
[program:pace-backend]
directory=/var/www/pace-backend
command=/var/www/pace-backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 127.0.0.1:8000
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/pace-backend/err.log
stdout_logfile=/var/log/pace-backend/out.log
environment=PATH="/var/www/pace-backend/venv/bin"
```

Create log directory:

```bash
sudo mkdir -p /var/log/pace-backend
sudo chown www-data:www-data /var/log/pace-backend
```

Start the service:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start pace-backend
```

### Step 7: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/pace-backend
```

Add:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 50M;  # Match your MAX_FILE_SIZE_MB

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed in future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeout settings for large file uploads
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/pace-backend /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

### Step 8: Set Up SSL Certificate

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow the prompts. Certbot will automatically update your Nginx configuration.

### Step 9: Set Up Log Rotation

```bash
sudo nano /etc/logrotate.d/pace-backend
```

Add:

```
/var/www/pace-backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 0644 www-data www-data
}
```

### Step 10: Create Required Directories

```bash
cd /var/www/pace-backend
mkdir -p logs tmp backups
sudo chown -R www-data:www-data logs tmp backups
```

---

## 5. Firewall Configuration

```bash
# Enable UFW firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

---

## 6. Testing Deployment

```bash
# Check if Redis is running
redis-cli ping  # Should return "PONG"

# Check if Gunicorn is running
sudo supervisorctl status pace-backend  # Should show "RUNNING"

# Check Nginx
sudo systemctl status nginx

# Test API endpoint
curl https://your-domain.com/docs  # Should show FastAPI docs
```

---

## 7. Monitoring & Maintenance

### Check Logs

```bash
# Application logs
tail -f /var/www/pace-backend/logs/*.log

# Supervisor logs
tail -f /var/log/pace-backend/out.log
tail -f /var/log/pace-backend/err.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Restart Services

```bash
# Restart application
sudo supervisorctl restart pace-backend

# Restart Nginx
sudo systemctl restart nginx

# Restart Redis
sudo systemctl restart redis-server
```

### Update Application

```bash
cd /var/www/pace-backend
git pull  # If using git
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart pace-backend
```

---

## 8. Optional Enhancements

### Set Up Automatic Backups

Create backup script:

```bash
sudo nano /usr/local/bin/backup-pace.sh
```

Add:

```bash
#!/bin/bash
BACKUP_DIR="/var/www/pace-backend/backups"
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf $BACKUP_DIR/pace-backup-$DATE.tar.gz /var/www/pace-backend --exclude=venv --exclude=backups
find $BACKUP_DIR -name "pace-backup-*.tar.gz" -mtime +7 -delete
```

Make executable and add to cron:

```bash
sudo chmod +x /usr/local/bin/backup-pace.sh
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-pace.sh
```

---

## 9. Frontend Deployment

Your frontend needs to be updated to point to your new backend URL. Update the API base URL in your frontend configuration to:

```
https://your-domain.com
```

---

## 10. Summary

### Key Files Needed on VPS

1. All Python files from your project
2. `requirements.txt`
3. `.env` file (with production Redis URL)
4. `fonts/` directory with TTF files
5. `images/` directory with logos
6. Empty `logs/`, `tmp/`, and `backups/` directories

### Main Changes from Local to VPS

- **Redis:** From localhost to managed Redis service or local Redis server
- **CORS:** Add production domain to `constants.py`
- **Process Manager:** Use Gunicorn + Supervisor instead of `uvicorn main:app`
- **Reverse Proxy:** Nginx in front of Gunicorn
- **SSL:** HTTPS via Certbot/Let's Encrypt

### Architecture Overview

```
Internet
   ↓
HTTPS (Port 443)
   ↓
Nginx (Reverse Proxy)
   ↓
Gunicorn (WSGI Server) - Port 8000
   ↓
FastAPI Application (main.py)
   ↓
Redis (Session Storage) - Port 6379
```

### Service Dependencies

| Service | Purpose | Port |
|---------|---------|------|
| Nginx | Reverse proxy, SSL termination | 80, 443 |
| Gunicorn | Python WSGI HTTP server | 8000 (internal) |
| Redis | Session storage and caching | 6379 (internal) |
| Supervisor | Process management | N/A |

### Quick Reference Commands

```bash
# Check all services
sudo systemctl status nginx
sudo systemctl status redis-server
sudo supervisorctl status pace-backend

# Restart everything
sudo supervisorctl restart pace-backend
sudo systemctl restart nginx
sudo systemctl restart redis-server

# View logs
tail -f /var/log/pace-backend/out.log
tail -f /var/log/nginx/error.log

# Test Redis connection
redis-cli ping

# Test application
curl https://your-domain.com/docs
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check supervisor logs
tail -f /var/log/pace-backend/err.log

# Check if port 8000 is in use
sudo lsof -i :8000

# Manually test Gunicorn
cd /var/www/pace-backend
source venv/bin/activate
gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app --bind 127.0.0.1:8000
```

### Redis Connection Issues

```bash
# Check Redis status
sudo systemctl status redis-server

# Test connection
redis-cli ping

# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

### Nginx Issues

```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Verify site is enabled
ls -la /etc/nginx/sites-enabled/
```

### SSL Certificate Issues

```bash
# Renew certificates manually
sudo certbot renew

# Check certificate expiry
sudo certbot certificates
```

### File Upload Issues

```bash
# Check permissions
ls -la /var/www/pace-backend/tmp

# Fix permissions
sudo chown -R www-data:www-data /var/www/pace-backend/tmp
sudo chmod 755 /var/www/pace-backend/tmp
```

---

## Security Checklist

- [ ] SSH key-based authentication enabled (disable password auth)
- [ ] UFW firewall enabled with only necessary ports open
- [ ] Redis bound to localhost only
- [ ] SSL certificate installed and auto-renewal configured
- [ ] Application running as www-data user (not root)
- [ ] .env file has restricted permissions (600)
- [ ] Regular backups scheduled
- [ ] Log rotation configured
- [ ] Keep system and dependencies updated

---

## Performance Optimization

### Gunicorn Workers

Adjust worker count based on CPU cores:

```bash
# Formula: (2 × CPU cores) + 1
# For 2 cores: 5 workers
# For 4 cores: 9 workers
```

Update `/etc/supervisor/conf.d/pace-backend.conf`:

```ini
command=/var/www/pace-backend/venv/bin/gunicorn -w 9 -k uvicorn.workers.UvicornWorker main:app --bind 127.0.0.1:8000
```

### Redis Optimization

Adjust Redis memory based on session size:

```conf
# /etc/redis/redis.conf
maxmemory 1gb
maxmemory-policy allkeys-lru
```

### Nginx Caching (Optional)

Add to Nginx config for static file caching:

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js|ttf)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## Support & Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Gunicorn Documentation:** https://docs.gunicorn.org/
- **Nginx Documentation:** https://nginx.org/en/docs/
- **Supervisor Documentation:** http://supervisord.org/
- **Redis Documentation:** https://redis.io/documentation
- **Certbot Documentation:** https://certbot.eff.org/

---

## License

This deployment guide is part of the PACE backend project.
