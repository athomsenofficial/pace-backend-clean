# Docker Deployment Guide

This guide covers deploying the PACE backend using Docker and Docker Compose.

## Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

### Local Development with Docker

1. **Clone the repository:**
   ```bash
   git clone https://github.com/athomsenofficial/pace-backend-clean.git
   cd pace-backend-clean
   ```

2. **Create environment file:**
   ```bash
   cp .env.production.example .env
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Check the application:**
   ```bash
   # View logs
   docker-compose logs -f backend

   # Check health
   curl http://localhost:8000/api/health

   # Access API docs
   open http://localhost:8000/docs
   ```

5. **Stop the application:**
   ```bash
   docker-compose down
   ```

## Docker Compose Services

The `docker-compose.yml` defines two services:

### 1. Redis Service
- **Image:** redis:7.4-alpine
- **Port:** 6379
- **Purpose:** Session storage and caching
- **Configuration:**
  - Persistence enabled (saves every 60 seconds if 1+ keys changed)
  - Max memory: 512MB with LRU eviction policy
  - Health checks enabled

### 2. Backend Service
- **Build:** Local Dockerfile
- **Port:** 8000
- **Purpose:** FastAPI application
- **Features:**
  - 4 Gunicorn workers with Uvicorn
  - Auto-restart on failure
  - Health checks
  - Volume mounts for logs, temp files, and backups

## Dockerfile Overview

The Dockerfile uses a multi-stage approach optimized for production:

- **Base Image:** python:3.11-slim
- **Dependencies:** Installed via requirements.txt
- **Optimizations:**
  - Layer caching for dependencies
  - Minimal system packages
  - Non-root user execution
- **Server:** Gunicorn with Uvicorn workers

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| REDIS_URL | redis://redis:6379 | Redis connection URL |
| SESSION_TTL | 1800 | Session timeout in seconds |
| MAX_FILE_SIZE_MB | 50 | Maximum upload file size |

## Production Deployment

### Hostinger VPS with Docker

1. **SSH into your VPS:**
   ```bash
   ssh user@your-vps-ip
   ```

2. **Install Docker and Docker Compose:**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose

   # Add your user to docker group
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Clone and deploy:**
   ```bash
   git clone https://github.com/athomsenofficial/pace-backend-clean.git
   cd pace-backend-clean
   cp .env.production.example .env
   docker-compose up -d
   ```

4. **Set up Nginx reverse proxy:**
   ```bash
   sudo nano /etc/nginx/sites-available/pace-backend
   ```

   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;

       client_max_body_size 50M;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;

           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";

           proxy_connect_timeout 600;
           proxy_send_timeout 600;
           proxy_read_timeout 600;
       }
   }
   ```

   Enable and restart:
   ```bash
   sudo ln -s /etc/nginx/sites-available/pace-backend /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. **Set up SSL:**
   ```bash
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

### Using Docker Hub (Alternative)

1. **Build and push to Docker Hub:**
   ```bash
   docker build -t athomsenofficial/pace-backend:latest .
   docker push athomsenofficial/pace-backend:latest
   ```

2. **Update docker-compose.yml on server:**
   ```yaml
   backend:
     image: athomsenofficial/pace-backend:latest
     # Remove the build section
   ```

## Monitoring and Maintenance

### View Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Redis only
docker-compose logs -f redis

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Check Service Status
```bash
# Service status
docker-compose ps

# Health checks
docker inspect pace-backend | grep -A 10 Health
docker inspect pace-redis | grep -A 10 Health
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart backend only
docker-compose restart backend

# Full rebuild
docker-compose down
docker-compose up -d --build
```

### Update Application
```bash
cd pace-backend-clean
git pull
docker-compose down
docker-compose up -d --build
```

### Backup Data
```bash
# Backup Redis data
docker exec pace-redis redis-cli SAVE
docker cp pace-redis:/data/dump.rdb ./backups/redis-$(date +%Y%m%d).rdb

# Backup application data
tar -czf backup-$(date +%Y%m%d).tar.gz logs/ tmp/ backups/
```

### Clean Up
```bash
# Remove stopped containers
docker-compose down

# Remove all (including volumes)
docker-compose down -v

# Clean up Docker system
docker system prune -a
```

## Scaling

To increase the number of Gunicorn workers:

1. **Edit docker-compose.yml:**
   ```yaml
   backend:
     command: gunicorn -w 8 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
   ```

2. **Recommended workers:** `(2 × CPU cores) + 1`

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs backend

# Check if ports are available
sudo lsof -i :8000
sudo lsof -i :6379
```

### Redis connection issues
```bash
# Test Redis connection
docker exec pace-redis redis-cli ping

# Check network
docker network inspect pace-backend-clean_pace-network
```

### Permission issues
```bash
# Fix volume permissions
sudo chown -R 1000:1000 logs/ tmp/ backups/
```

### Out of memory
```bash
# Check Docker memory
docker stats

# Increase Redis maxmemory in docker-compose.yml
command: redis-server --maxmemory 1gb
```

## Security Best Practices

1. **Use secrets for sensitive data:**
   ```bash
   docker secret create redis_password /path/to/password
   ```

2. **Limit container resources:**
   ```yaml
   backend:
     deploy:
       resources:
         limits:
           cpus: '2'
           memory: 2G
   ```

3. **Use specific image versions:**
   ```yaml
   redis:
     image: redis:7.4.1-alpine
   ```

4. **Regular updates:**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

## Health Checks

The application includes health check endpoints:

- **Application Health:** `GET /api/health`
- **Redis Health:** Automatic via Docker Compose
- **Docker Health:** Built into containers

Monitor health:
```bash
# Check health status
docker inspect pace-backend --format='{{.State.Health.Status}}'

# View health logs
docker inspect pace-backend --format='{{json .State.Health}}' | jq
```

## Performance Tuning

### Gunicorn Workers
```bash
# Formula: (2 × CPU cores) + 1
# Adjust in docker-compose.yml or Dockerfile
```

### Redis Memory
```bash
# Adjust maxmemory based on available RAM
# Recommended: 25-50% of total RAM for Redis
```

### Nginx Caching
Add to Nginx config for static files:
```nginx
location /static {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Support

- **GitHub Issues:** https://github.com/athomsenofficial/pace-backend-clean/issues
- **Documentation:** See HOSTINGER_VPS_DEPLOYMENT.md for non-Docker deployment

## License

This project is part of the PACE backend system.
