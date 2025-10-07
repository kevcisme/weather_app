# Running Frontend on Raspberry Pi

Complete guide for running both the backend API and frontend dashboard on your Raspberry Pi.

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────┐
│         Raspberry Pi                    │
│                                         │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │   Backend    │  │   Frontend      │ │
│  │   FastAPI    │  │   Next.js       │ │
│  │   Port 8000  │  │   Port 3000     │ │
│  └──────┬───────┘  └────────┬────────┘ │
│         │                   │          │
│         │                   │          │
│         └───────────────────┘          │
│                  │                     │
└──────────────────┼─────────────────────┘
                   │
                   ▼
              ┌─────────┐
              │   S3    │
              └─────────┘
```

**Benefits:**
- ✅ Self-contained system (no external hosting needed)
- ✅ Access dashboard from any device on your network
- ✅ No internet dependency for viewing data
- ✅ Lower latency (everything local)
- ✅ Privacy (data never leaves your network except S3 uploads)

## 🚀 Quick Setup

### Automated Setup (Recommended)

From your Mac:

```bash
# Deploy everything to the Pi
./deploy/rsync_deploy.sh
```

Then SSH into your Pi:

```bash
ssh pi@raspi.local

cd ~/apps/weather_app

# Run automated setup
./deploy/setup-pi.sh
```

That's it! Both services will be running.

## 📊 Accessing Your Dashboard

After setup, access from any device on your network:

### Direct Access (Two Ports)

- **Dashboard**: `http://raspi.local:3000` or `http://192.168.x.x:3000`
- **API**: `http://raspi.local:8000` or `http://192.168.x.x:8000`

### Using Nginx (Single Port - Optional)

For cleaner URLs on port 80:

```bash
# On your Pi
cd ~/apps/weather_app
./deploy/setup-nginx.sh
```

Then access:
- **Dashboard**: `http://raspi.local` or `http://192.168.x.x`
- **API**: `http://raspi.local/api/latest` or `http://192.168.x.x/api/latest`

## ⚙️ Services

Two systemd services are created:

### 1. Backend Service (`weather.service`)
- Collects sensor data from Sense HAT
- Uploads to S3 every 15 minutes (configurable)
- Serves API on port 8000

### 2. Frontend Service (`weather-frontend.service`)
- Serves Next.js dashboard on port 3000
- Auto-starts on boot
- Restarts automatically if crashes

## 🔧 Management Commands

### Check Status

```bash
# Both services
sudo systemctl status weather weather-frontend

# Just backend
sudo systemctl status weather

# Just frontend
sudo systemctl status weather-frontend
```

### View Logs

```bash
# Backend logs
journalctl -u weather -f

# Frontend logs
journalctl -u weather-frontend -f

# Both together
journalctl -u weather -u weather-frontend -f
```

### Restart Services

```bash
# Restart both
sudo systemctl restart weather weather-frontend

# Restart just one
sudo systemctl restart weather
sudo systemctl restart weather-frontend
```

### Stop/Start Services

```bash
# Stop all
sudo systemctl stop weather weather-frontend

# Start all
sudo systemctl start weather weather-frontend
```

## 📁 File Locations on Pi

```
/home/pi/apps/weather_app/
├── backend/
│   ├── src/weather/
│   │   ├── .env              # AWS credentials & config
│   │   ├── api.py
│   │   ├── s3.py
│   │   └── ...
│   └── pyproject.toml
├── frontend/
│   ├── .env.local            # Points to http://localhost:8000
│   ├── .next/                # Built production files
│   ├── src/
│   └── package.json
└── deploy/
    ├── weather.service           # Backend systemd service
    ├── weather-frontend.service  # Frontend systemd service
    ├── nginx-weather.conf        # Optional Nginx config
    └── ...
```

### Service Files

```
/etc/systemd/system/
├── weather.service
└── weather-frontend.service
```

## 🔄 Updating Code

### From Your Mac

```bash
# Deploy updated code and restart services
./deploy/rsync_deploy.sh
```

This will:
1. Sync backend code
2. Sync frontend code
3. Update dependencies
4. Rebuild frontend
5. Restart both services

### Manually on Pi

```bash
cd ~/apps/weather_app

# Update backend
cd backend
git pull  # if using git
uv sync
sudo systemctl restart weather

# Update frontend
cd ../frontend
git pull  # if using git
npm install
npm run build
sudo systemctl restart weather-frontend
```

## 🐛 Troubleshooting

### Frontend Won't Start

**Check logs:**
```bash
journalctl -u weather-frontend -n 50
```

**Common issues:**

1. **Port 3000 already in use**
   ```bash
   # Find what's using port 3000
   sudo lsof -i :3000
   
   # Kill it if needed
   sudo kill <PID>
   ```

2. **npm not installed**
   ```bash
   sudo apt install nodejs npm
   ```

3. **Build failed**
   ```bash
   cd ~/apps/weather_app/frontend
   rm -rf .next node_modules
   npm install
   npm run build
   sudo systemctl restart weather-frontend
   ```

4. **Out of memory during build**
   ```bash
   # Increase swap space temporarily
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   # Set CONF_SWAPSIZE=2048
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   
   # Try build again
   cd ~/apps/weather_app/frontend
   npm run build
   ```

### Frontend Shows "Failed to load current conditions"

**Check if backend is running:**
```bash
curl http://localhost:8000/latest
```

**If not:**
```bash
sudo systemctl status weather
journalctl -u weather -n 50
```

**Check frontend .env.local:**
```bash
cat ~/apps/weather_app/frontend/.env.local
# Should contain: NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Can't Access from Other Devices

**Check firewall:**
```bash
# Allow ports (if ufw is enabled)
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp

# Or allow from local network only
sudo ufw allow from 192.168.1.0/24 to any port 3000
sudo ufw allow from 192.168.1.0/24 to any port 8000
```

**Check services are listening on 0.0.0.0:**
```bash
# Should show 0.0.0.0:8000 and 0.0.0.0:3000
sudo netstat -tlnp | grep -E ':(3000|8000)'
```

**Find Pi's IP address:**
```bash
hostname -I
```

### High Memory Usage

**Check memory:**
```bash
free -h
htop
```

**Frontend uses more memory than backend. If running low:**

1. **Use Nginx reverse proxy** and stop frontend development mode
2. **Build static export** (optional advanced setup)
3. **Add swap space** (see above)

### Slow Performance

**The Pi should handle this fine, but if slow:**

1. **Check CPU usage:**
   ```bash
   htop
   ```

2. **Ensure frontend is built for production:**
   ```bash
   cd ~/apps/weather_app/frontend
   npm run build
   sudo systemctl restart weather-frontend
   ```

3. **Check for other processes:**
   ```bash
   top
   ```

## 🔐 Security Considerations

### Local Network Only (Recommended)

By default, services bind to `0.0.0.0` which allows access from your local network. This is fine for home use.

### Expose to Internet (Advanced)

If you want to access from outside your network:

**Option 1: Cloudflare Tunnel (Recommended)**
- Free
- No port forwarding
- HTTPS included
- See: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/

**Option 2: Tailscale**
- Creates VPN to your Pi
- Easy setup
- See: https://tailscale.com/

**Option 3: Port Forwarding (Not Recommended)**
- Security risk without proper HTTPS/auth
- Requires router configuration
- Needs dynamic DNS

### Add Basic Authentication (Optional)

Using Nginx:

```nginx
# In /etc/nginx/sites-available/weather
location / {
    auth_basic "Weather Station";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://127.0.0.1:3000;
    # ...
}
```

Create password:
```bash
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd pi
sudo systemctl restart nginx
```

## 🎨 Customization

### Change Ports

**Frontend Port:**

Edit `/etc/systemd/system/weather-frontend.service`:
```ini
[Service]
Environment="PORT=8080"  # Add this line
ExecStart=/usr/bin/npm start
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart weather-frontend
```

**Backend Port:**

Edit `/etc/systemd/system/weather.service`:
```ini
ExecStart=/home/pi/.local/bin/uv run uvicorn weather.api:app --host 0.0.0.0 --port 9000
```

Update frontend `.env.local`:
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:9000" > ~/apps/weather_app/frontend/.env.local
```

Rebuild and restart:
```bash
cd ~/apps/weather_app/frontend
npm run build
sudo systemctl daemon-reload
sudo systemctl restart weather weather-frontend
```

## 📊 Monitoring

### Create Simple Status Check Script

```bash
cat > ~/check-weather.sh << 'EOF'
#!/bin/bash
echo "Weather Station Status"
echo "====================="
echo ""
echo "Backend:"
sudo systemctl is-active --quiet weather && echo "✅ Running" || echo "❌ Stopped"
echo ""
echo "Frontend:"
sudo systemctl is-active --quiet weather-frontend && echo "✅ Running" || echo "❌ Stopped"
echo ""
echo "API Test:"
curl -s http://localhost:8000/latest > /dev/null && echo "✅ Responding" || echo "❌ Not responding"
echo ""
echo "Dashboard Test:"
curl -s http://localhost:3000 > /dev/null && echo "✅ Responding" || echo "❌ Not responding"
EOF

chmod +x ~/check-weather.sh
```

Run with:
```bash
~/check-weather.sh
```

### Add to cron for email alerts (optional)

```bash
crontab -e
```

Add:
```cron
*/30 * * * * ~/check-weather.sh || echo "Weather station down!" | mail -s "Alert" your@email.com
```

## 🎯 Performance Tips

1. **Use production build** (already done by setup script)
2. **Increase swap if needed** (for builds)
3. **Use Nginx** for better performance and single port access
4. **Monitor with htop** to catch issues early
5. **Keep system updated**: `sudo apt update && sudo apt upgrade`

## 📱 Mobile-Friendly

The dashboard is fully responsive and works great on:
- Phones
- Tablets
- Desktop computers

Just visit `http://raspi.local:3000` from any device on your network.

## 🔗 Integration with Other Services

### Home Assistant

Add to your `configuration.yaml`:

```yaml
sensor:
  - platform: rest
    name: "Weather Station Temperature"
    resource: "http://raspi.local:8000/latest"
    value_template: "{{ value_json.temp_f }}"
    unit_of_measurement: "°F"
    
  - platform: rest
    name: "Weather Station Humidity"
    resource: "http://raspi.local:8000/latest"
    value_template: "{{ value_json.humidity }}"
    unit_of_measurement: "%"
```

### Prometheus Monitoring

Expose metrics endpoint (requires code changes) or scrape logs.

### Grafana

Point Grafana at your S3 bucket or add a metrics endpoint to the backend.

## 🚀 Quick Reference

| Task | Command |
|------|---------|
| Check all services | `sudo systemctl status weather weather-frontend` |
| View all logs | `journalctl -u weather -u weather-frontend -f` |
| Restart everything | `sudo systemctl restart weather weather-frontend` |
| Update from Mac | `./deploy/rsync_deploy.sh` |
| Test backend | `curl http://localhost:8000/latest` |
| Test frontend | `curl http://localhost:3000` |
| Find Pi IP | `hostname -I` |
| Check memory | `free -h` |
| Check CPU | `htop` |

## 🌐 Access URLs

| Service | URL (hostname) | URL (IP) |
|---------|---------------|----------|
| Dashboard | http://raspi.local:3000 | http://192.168.x.x:3000 |
| API | http://raspi.local:8000 | http://192.168.x.x:8000 |
| With Nginx | http://raspi.local | http://192.168.x.x |

---

**For more help:**
- Main docs: [README.md](README.md)
- Pi setup: [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md)
- Getting started: [GETTING_STARTED.md](GETTING_STARTED.md)
