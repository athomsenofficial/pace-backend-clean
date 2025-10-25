# SSH Commands to Restart Backend Server

## Quick Restart Instructions

### Option 1: Using the Restart Script (Recommended)

1. **SSH into your server:**
   ```bash
   ssh root@89.116.187.76
   # OR
   ssh your-username@89.116.187.76
   ```

2. **Navigate to project directory:**
   ```bash
   cd pace-backend-clean
   # OR try these if above doesn't work:
   # cd /var/www/pace-backend-clean
   # cd /root/pace-backend-clean
   # cd ~/pace-backend-clean
   ```

3. **Run the restart script:**
   ```bash
   bash RESTART_SERVER.sh
   ```

### Option 2: Manual Commands

If you prefer to run commands manually:

```bash
# 1. SSH into server
ssh root@89.116.187.76

# 2. Navigate to project
cd pace-backend-clean  # or wherever you deployed it

# 3. Pull latest changes
git pull origin main

# 4. Stop containers
docker-compose down

# 5. Rebuild and start
docker-compose up -d --build

# 6. Check status
docker-compose ps

# 7. View logs
docker-compose logs -f backend

# 8. Test health endpoint
curl http://localhost:8000/api/health
```

## Troubleshooting

### If Git Pull Fails

```bash
# Check current changes
git status

# Stash local changes if any
git stash

# Pull again
git pull origin main

# Apply stashed changes (if needed)
git stash pop
```

### If Docker Commands Fail

```bash
# Check if Docker is running
docker --version
docker-compose --version

# Check running containers
docker ps -a

# Force remove containers
docker-compose down -v
docker-compose up -d --build
```

### View Detailed Logs

```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Redis only
docker-compose logs -f redis

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Check Container Health

```bash
# Check if containers are running
docker-compose ps

# Inspect backend container
docker inspect pace-backend

# Check health status
docker inspect pace-backend | grep -A 10 Health
```

### Restart Specific Service

```bash
# Restart backend only
docker-compose restart backend

# Restart Redis only
docker-compose restart redis
```

## Verify Everything is Working

After restart, run these checks:

```bash
# 1. Check containers are running
docker-compose ps

# 2. Test health endpoint
curl http://localhost:8000/api/health

# 3. Test from outside (from your local machine)
curl http://89.116.187.76:8000/api/health

# 4. Check API docs are accessible
curl http://89.116.187.76:8000/docs
```

## Expected Output

### Successful Health Check:
```json
{"status":"healthy","service":"pace-backend"}
```

### Successful Container Status:
```
NAME            IMAGE                          STATUS          PORTS
pace-backend    pace-backend-clean_backend     Up 2 minutes    0.0.0.0:8000->8000/tcp
pace-redis      redis:7.4-alpine               Up 2 minutes    0.0.0.0:6379->6379/tcp
```

## Common Issues

### Issue: Port 8000 already in use
```bash
# Find what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or stop all Docker containers
docker stop $(docker ps -aq)
docker-compose up -d
```

### Issue: Permission denied
```bash
# Run with sudo
sudo docker-compose down
sudo docker-compose up -d --build
```

### Issue: Out of disk space
```bash
# Clean up Docker
docker system prune -a

# Check disk usage
df -h
```

## After Successful Restart

1. ✅ Backend should be accessible at: `http://89.116.187.76:8000`
2. ✅ Health endpoint: `http://89.116.187.76:8000/api/health`
3. ✅ API docs: `http://89.116.187.76:8000/docs`
4. ✅ CORS should now allow all origins (for development)

## Next Steps

Once the server is restarted:

1. Test the health endpoint from your browser
2. Try the frontend locally (it should now connect to the backend)
3. Upload a test roster file to verify full functionality

## Quick Test Command (Run from Local Machine)

```bash
# Test health endpoint
curl http://89.116.187.76:8000/api/health

# Test CORS headers
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     http://89.116.187.76:8000/api/upload/initial-mel -v
```

If you see CORS headers in the response, the server is properly configured!
