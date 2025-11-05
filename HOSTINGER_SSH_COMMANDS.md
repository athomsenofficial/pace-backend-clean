# Hostinger VPS Restart Commands

## SSH Credentials
- **Host:** srv1045045.hstgr.cloud
- **Username:** andrew.t247@gmail.com
- **Password:** gmm

---

## Quick Restart Steps

### Step 1: Connect via SSH

Open your terminal and run:

```bash
ssh andrew.t247@gmail.com@srv1045045.hstgr.cloud
```

**Note:** If the email format doesn't work, try:
```bash
ssh root@srv1045045.hstgr.cloud
# OR
ssh andrew.t247@srv1045045.hstgr.cloud
# OR
ssh andrew@srv1045045.hstgr.cloud
```

When prompted for password, enter: `gmm`

### Step 2: Find Your Project

Once connected, run:

```bash
# Check current directory
pwd

# List files
ls -la

# Try to find the project
find ~ -name "pace-backend-clean" -type d 2>/dev/null
```

### Step 3: Navigate to Project Directory

Based on what you find, navigate to the project:

```bash
# Most likely one of these:
cd pace-backend-clean
# OR
cd ~/pace-backend-clean
# OR
cd /root/pace-backend-clean
# OR
cd /home/andrew.t247@gmail.com/pace-backend-clean
```

### Step 4: Pull Latest Code and Restart Docker

Once you're in the project directory, run:

```bash
# Pull latest changes (includes CORS fix)
git pull origin main

# Stop Docker containers
docker-compose down

# Rebuild and start
docker-compose up -d --build

# Wait for startup
sleep 5

# Check status
docker-compose ps

# Test health endpoint
curl http://localhost:8000/api/health
```

### Step 5: Exit SSH

```bash
exit
```

---

## One-Line Command (After Connecting)

After you SSH in and find the project directory, you can paste this:

```bash
git pull origin main && docker-compose down && docker-compose up -d --build && sleep 5 && docker-compose ps && curl http://localhost:8000/api/health
```

---

## If Docker Commands Don't Work

You might need sudo or full path:

```bash
# Try with sudo
sudo docker-compose down
sudo docker-compose up -d --build

# Or try full path
/usr/local/bin/docker-compose down
/usr/local/bin/docker-compose up -d --build

# Check if docker is installed
which docker
which docker-compose
docker --version
```

---

## Alternative: Use Hostinger Panel

If SSH is complicated, you can also:

1. Go to https://hpanel.hostinger.com
2. Login with: andrew.t247@gmail.com / gmm
3. Navigate to VPS → Docker Manager
4. Find your `pace-backend-clean` project
5. Click "Redeploy" or "Rebuild"

---

## After Restart: Test Locally

From your Mac terminal (NEW window):

```bash
# Test backend health
curl http://89.116.187.76:8000/api/health

# Should return:
# {"status":"healthy","service":"pace-backend"}
```

Then start frontend:

```bash
cd /Users/drew/Coding/pace-front-end-react
npm run dev
```

Open: http://localhost:5173

Try uploading a roster - it should connect to the backend!

---

## Troubleshooting SSH Login

If the email format doesn't work as username, check:

1. **Try different username formats:**
   - `andrew.t247@gmail.com`
   - `andrew.t247`
   - `andrew`
   - `root`

2. **Check Hostinger documentation:**
   - Log into hpanel.hostinger.com
   - Go to VPS settings
   - Look for "SSH Access" section
   - It will show the exact username to use

3. **Use the Hostinger web terminal:**
   - In hpanel.hostinger.com
   - VPS → Overview
   - Look for "Web Terminal" or "Browser SSH"
   - Click to open terminal in browser
   - No username needed!

---

## Expected Success Output

```
Cloning into 'pace-backend-clean'...
Already up to date.
[+] Running 2/2
 ✔ Container pace-redis    Started
 ✔ Container pace-backend  Started
NAME            IMAGE                          STATUS
pace-backend    pace-backend-clean-backend     Up 3 seconds
pace-redis      redis:7.4-alpine               Up 3 seconds
{"status":"healthy","service":"pace-backend"}
```

---

## Quick Summary

1. SSH in: `ssh andrew.t247@gmail.com@srv1045045.hstgr.cloud` (password: `gmm`)
2. Find project: `cd pace-backend-clean`
3. Restart: `git pull && docker-compose down && docker-compose up -d --build`
4. Test: `curl http://localhost:8000/api/health`
5. Exit: `exit`
6. Local test: `curl http://89.116.187.76:8000/api/health`
7. Start frontend: `cd /Users/drew/Coding/pace-front-end-react && npm run dev`
