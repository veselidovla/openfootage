# OpenFootage Backend Deployment Guide

## For ~10 Testers Demo

This guide helps you deploy the OpenFootage backend for a small demo with approximately 10 concurrent users.

## Server Requirements

**Recommended VPS Specs:**
- **CPU:** 2 vCPU
- **RAM:** 4GB
- **Storage:** 20GB SSD
- **OS:** Ubuntu 22.04 LTS

*Providers: DigitalOcean, Linode, Vultr, AWS Lightsail, Hetzner*

---

## Quick Setup Steps

### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3 python3-pip python3-venv -y

# Install Nginx (for frontend)
sudo apt install nginx -y

# Install Docker & Docker Compose (for Meilisearch)
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. Setup Meilisearch

```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  meilisearch:
    image: getmeili/meilisearch:v1.5
    ports:
      - "7700:7700"
    environment:
      - MEILI_MASTER_KEY=OPENFOOTAGE_PRODUCTION_KEY_CHANGE_ME
      - MEILI_ENV=production
    volumes:
      - ./meili_data:/meili_data
    restart: unless-stopped
EOF

# Start Meilisearch
sudo docker-compose up -d
```

### 3. Deploy Backend

```bash
# Clone repository
cd /opt
git clone <your-repo-url> openfootage-backend
cd openfootage-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn meilisearch-python openai requests python-dotenv

# Create .env file with your keys
cat > .env << 'EOF'
# Meilisearch
MEILI_HOST=http://127.0.0.1:7700
MEILI_API_KEY=OPENFOOTAGE_PRODUCTION_KEY_CHANGE_ME

# API Keys (replace with your actual keys)
PEXELS_API_KEY=your_pexels_key_here
PIXABAY_API_KEY=your_pixabay_key_here
COVERR_API_KEY=your_coverr_key_here
OPENAI_API_KEY=your_openai_key_here
EOF

# Test run
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Setup Systemd Service (Keep Backend Running)

```bash
# Create systemd service file
sudo cat > /etc/systemd/system/openfootage-backend.service << 'EOF'
[Unit]
Description=OpenFootage FastAPI Backend
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/openfootage-backend
Environment="PATH=/opt/openfootage-backend/venv/bin"
ExecStart=/opt/openfootage-backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable openfootage-backend
sudo systemctl start openfootage-backend

# Check status
sudo systemctl status openfootage-backend

# View logs
sudo journalctl -u openfootage-backend -f
```

---

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MEILI_HOST` | Meilisearch URL | `http://127.0.0.1:7700` |
| `MEILI_API_KEY` | Meilisearch master key | `OPENFOOTAGE_PRODUCTION_KEY_CHANGE_ME` |
| `PEXELS_API_KEY` | Pexels API key | Get from pexels.com/api |
| `PIXABAY_API_KEY` | Pixabay API key | Get from pixabay.com/api |
| `COVERR_API_KEY` | Coverr API key | Get from coverr.co/api |
| `OPENAI_API_KEY` | OpenAI API key (for health checks) | `sk-proj-...` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Backend server port |
| `WORKERS` | `2` | Uvicorn workers for multi-threading |

---

## Frontend Deployment (with Nginx)

```bash
# Build frontend (run on your local machine)
cd openfootage-frontend
npm run build

# Upload dist/ folder to server
scp -r dist/ user@your-server:/opt/openfootage-frontend

# Configure Nginx
sudo cat > /etc/nginx/sites-available/openfootage << 'EOF'
server {
    listen 80;
    server_name your-domain.com;  # or use IP address

    # Frontend
    location / {
        root /opt/openfootage-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/openfootage /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Monitoring & Debugging

### Check Backend Status
```bash
# View logs
sudo journalctl -u openfootage-backend -f

# Check if running
curl http://localhost:8000/health

# Check process
ps aux | grep uvicorn
```

### Check Meilisearch
```bash
# View logs
sudo docker logs -f meilisearch

# Check health
curl http://localhost:7700/health
```

### Performance Monitoring
```bash
# CPU and Memory usage
htop

# Network connections
netstat -tuln | grep 8000
```

---

## Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## Performance Optimizations (Already Applied)

✅ **Embeddings disabled** - No OpenAI calls during search  
✅ **Indexing disabled** - No Meilisearch writes on every search  
✅ **Provider limits reduced** - Fetch 20-30 results per provider max  
✅ **HTTP timeouts set** - 4-second timeout per provider request  
✅ **Logging enabled** - See search queries and result counts  

---

## Testing the Deployment

```bash
# Health check
curl http://your-server-ip:8000/health

# Simple search
curl "http://your-server-ip:8000/search/simple?query=ocean"

# With filters
curl "http://your-server-ip:8000/search/simple?query=sunset&provider=pexels&type=video"
```

---

## Troubleshooting

### Backend won't start
```bash
# Check logs
sudo journalctl -u openfootage-backend -n 50

# Check if port is in use
sudo lsof -i :8000

# Manually test
cd /opt/openfootage-backend
source venv/bin/activate
uvicorn main:app --reload
```

### Slow searches
- Check provider API keys are valid
- Verify network connectivity to external APIs
- Review logs for timeout errors
- Ensure Meilisearch is running

### Out of memory
```bash
# Check memory usage
free -h

# Restart backend
sudo systemctl restart openfootage-backend
```

---

## Scaling Beyond 10 Users

When ready to scale:

1. **Enable parallel provider fetching** (implement async/threading)
2. **Add caching layer** (Redis for frequent queries)
3. **Increase server resources** (4 vCPU, 8GB RAM)
4. **Add load balancer** (for multiple backend instances)
5. **Enable embeddings selectively** (for semantic search)

---

## Security Checklist

- [ ] Change default Meilisearch master key
- [ ] Use HTTPS (Let's Encrypt with Certbot)
- [ ] Keep API keys in `.env`, never commit to git
- [ ] Enable UFW firewall
- [ ] Regular system updates: `sudo apt update && sudo apt upgrade`
- [ ] Monitor logs for suspicious activity

---

## Support

For issues or questions:
- Check logs: `sudo journalctl -u openfootage-backend -f`
- Test endpoints: `curl http://localhost:8000/health`
- Review this guide's troubleshooting section

---

**Last Updated:** December 8, 2025
