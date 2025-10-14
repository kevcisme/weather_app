# Deployment Guide for Weather Station

Quick reference for deploying to your Raspberry Pi at **192.168.86.49**.

## 🚀 Quick Deploy

```bash
# Deploy everything and restart services
./scripts/deploy/rsync_deploy.sh
```

This will:
1. Sync backend code to Pi
2. Sync frontend code to Pi
3. Update dependencies
4. Rebuild frontend
5. Restart both services

## 🔧 Your Pi Configuration

- **IP Address**: `192.168.86.49`
- **Hostname**: Can also try `raspi.local` if mDNS is working
- **SSH**: `ssh pi@192.168.86.49`
- **Dashboard**: http://192.168.86.49:3000
- **API**: http://192.168.86.49:8000

## 📝 Configuration File

Your Pi's IP is saved in `.pi-config`:

```bash
PI_HOST=192.168.86.49
PI_USER=pi
```

You can edit this file if your Pi's IP changes.

## 🔑 SSH Access

### Quick SSH

```bash
# Use the helper script
./scripts/backend/quick-ssh.sh

# Or directly
ssh pi@192.168.86.49
```

### First Time SSH Setup (if needed)

If you haven't set up SSH keys:

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy to Pi
ssh-copy-id pi@192.168.86.49

# Test connection
ssh pi@192.168.86.49
```

## 📦 Deployment Commands

### Full Deployment

```bash
./scripts/deploy/rsync_deploy.sh
```

### Backend Only

```bash
rsync -az --delete backend/ pi@192.168.86.49:~/apps/weather_app/backend/
ssh pi@192.168.86.49 'cd ~/apps/weather_app/backend && uv sync && sudo systemctl restart weather.service'
```

### Frontend Only

```bash
rsync -az --delete --exclude 'node_modules' --exclude '.next' frontend/ pi@192.168.86.49:~/apps/weather_app/frontend/
ssh pi@192.168.86.49 'cd ~/apps/weather_app/frontend && npm install && npm run build && sudo systemctl restart weather-frontend.service'
```

### Config/Scripts Only

```bash
rsync -az deploy/ pi@192.168.86.49:~/apps/weather_app/deploy/
```

## 🔍 Monitoring

### Check Status

```bash
# From your Mac
ssh pi@192.168.86.49 'sudo systemctl status weather weather-frontend'

# View logs
ssh pi@192.168.86.49 'journalctl -u weather -u weather-frontend -f'
```

### Test Endpoints

```bash
# Test backend API
curl http://192.168.86.49:8000/latest

# Test frontend
curl http://192.168.86.49:3000

# Get current weather (formatted)
curl -s http://192.168.86.49:8000/latest | python3 -m json.tool
```

## 🔄 Common Tasks

### Restart Services

```bash
ssh pi@192.168.86.49 'sudo systemctl restart weather weather-frontend'
```

### View Logs

```bash
# Backend logs
ssh pi@192.168.86.49 'journalctl -u weather -f'

# Frontend logs
ssh pi@192.168.86.49 'journalctl -u weather-frontend -f'

# Both
ssh pi@192.168.86.49 'journalctl -u weather -u weather-frontend -f'
```

### Update Environment Variables

```bash
# SSH into Pi
ssh pi@192.168.86.49

# Edit backend .env
nano ~/apps/weather_app/backend/src/weather/.env

# Restart backend
sudo systemctl restart weather
```

### Check S3 Uploads

```bash
ssh pi@192.168.86.49 'cd ~/apps/weather_app/backend && uv run python list_s3_objects.py'
```

## 🌐 Access from Other Devices

Anyone on your network (192.168.86.x) can access:

### From Computer/Phone/Tablet

- **Dashboard**: http://192.168.86.49:3000
- **API**: http://192.168.86.49:8000/latest

### From Home Assistant

```yaml
sensor:
  - platform: rest
    name: "Weather Station Temperature"
    resource: "http://192.168.86.49:8000/latest"
    value_template: "{{ value_json.temp_f }}"
    unit_of_measurement: "°F"
    
  - platform: rest
    name: "Weather Station Humidity"
    resource: "http://192.168.86.49:8000/latest"
    value_template: "{{ value_json.humidity }}"
    unit_of_measurement: "%"
    
  - platform: rest
    name: "Weather Station Pressure"
    resource: "http://192.168.86.49:8000/latest"
    value_template: "{{ value_json.pressure }}"
    unit_of_measurement: "hPa"
```

## 🔧 If Your Pi's IP Changes

Your router may assign a different IP to the Pi after a restart. To fix this:

### Option 1: Set Static IP (Recommended)

On your Pi:

```bash
sudo nano /etc/dhcpcd.conf
```

Add at the end:

```
interface eth0  # or wlan0 for WiFi
static ip_address=192.168.86.49/24
static routers=192.168.86.1
static domain_name_servers=192.168.86.1 8.8.8.8
```

Reboot:
```bash
sudo reboot
```

### Option 2: Reserve IP in Router

1. Log into your router (usually http://192.168.86.1)
2. Find DHCP settings
3. Reserve 192.168.86.49 for your Pi's MAC address

### Option 3: Update Scripts

If you need to change the IP in the scripts:

1. Edit `.pi-config`:
   ```bash
   nano .pi-config
   # Change PI_HOST=192.168.86.49 to new IP
   ```

2. Edit `deploy/rsync_deploy.sh`:
   ```bash
   nano scripts/deploy/rsync_deploy.sh
   # Change RSPI=pi@192.168.86.49
   ```

3. Edit `deploy/quick-ssh.sh`:
   ```bash
   nano scripts/backend/quick-ssh.sh
   # Change IP in ssh command
   ```

## 🐛 Troubleshooting

### Can't Connect to Pi

```bash
# Ping the Pi
ping 192.168.86.49

# Scan for Pi on network (if IP changed)
nmap -sn 192.168.86.0/24 | grep -B 2 "Raspberry Pi"

# Or use arp
arp -a | grep -i "b8:27:eb\|dc:a6:32\|e4:5f:01"  # Common Pi MAC prefixes
```

### SSH Connection Refused

```bash
# Check if SSH is enabled on Pi (requires physical access)
# On Pi: sudo raspi-config -> Interface Options -> SSH -> Enable
```

### Permission Denied

```bash
# Make sure you're using the right username (usually 'pi')
ssh pi@192.168.86.49

# If you changed the default password, use that
```

### Services Not Responding After Deploy

```bash
# Check service status
ssh pi@192.168.86.49 'sudo systemctl status weather weather-frontend'

# Restart manually
ssh pi@192.168.86.49 'sudo systemctl restart weather weather-frontend'

# Check logs for errors
ssh pi@192.168.86.49 'journalctl -u weather -n 50'
ssh pi@192.168.86.49 'journalctl -u weather-frontend -n 50'
```

## 📱 Bookmarks for Your Devices

Add these to your browser bookmarks:

- **Weather Dashboard**: http://192.168.86.49:3000
- **Current Conditions API**: http://192.168.86.49:8000/latest
- **24h History API**: http://192.168.86.49:8000/history?hours=24

## 🔗 Quick Links

| Purpose | Command/URL |
|---------|-------------|
| Deploy | `./scripts/deploy/rsync_deploy.sh` |
| SSH | `./scripts/backend/quick-ssh.sh` or `ssh pi@192.168.86.49` |
| Dashboard | http://192.168.86.49:3000 |
| API | http://192.168.86.49:8000 |
| Backend Logs | `ssh pi@192.168.86.49 'journalctl -u weather -f'` |
| Frontend Logs | `ssh pi@192.168.86.49 'journalctl -u weather-frontend -f'` |
| Restart All | `ssh pi@192.168.86.49 'sudo systemctl restart weather weather-frontend'` |

## 📚 More Documentation

- **[PI_FRONTEND_SETUP.md](PI_FRONTEND_SETUP.md)** - Complete Pi frontend guide
- **[RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md)** - Initial Pi setup
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Quick start guide
- **[README.md](README.md)** - Full project documentation

---

**Current Configuration**: Weather Station on Raspberry Pi at `192.168.86.49`
