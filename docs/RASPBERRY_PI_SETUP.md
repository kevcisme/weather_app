# Raspberry Pi Setup Guide

Complete guide for setting up the weather station backend on your Raspberry Pi with Sense HAT.

## 📋 Prerequisites

- Raspberry Pi (any model with 40-pin GPIO header)
- Sense HAT installed on GPIO pins
- Raspberry Pi OS (Bullseye or newer)
- Internet connection
- SSH access enabled

## 🚀 Quick Setup (Automated)

### From Your Development Machine

```bash
# 1. Copy files to Raspberry Pi
./scripts/deploy/rsync_deploy.sh

# 2. SSH into your Pi
ssh pi@raspi.local  # or use IP address: ssh pi@192.168.x.x
```

### On the Raspberry Pi

```bash
cd ~/apps/weather_app

# Run the automated setup
./scripts/setup/setup-pi.sh
```

That's it! The service will start automatically and begin collecting data.

## 📝 Manual Setup (Step-by-Step)

If you prefer to set things up manually or need to troubleshoot:

### 1. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv sense-hat

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for current session
source $HOME/.cargo/env
```

### 2. Create Project Directory

```bash
# Create directory structure
mkdir -p ~/apps/weather_app
cd ~/apps/weather_app
```

### 3. Copy Project Files

**Option A: From your development machine**
```bash
# On your dev machine, run:
cd /Users/kevincoyle/side-projects/weather_app
./scripts/deploy/rsync_deploy.sh
```

**Option B: Manual copy via SCP**
```bash
# On your dev machine:
scp -r backend/ pi@raspi.local:~/apps/weather_app/
scp -r scripts/ pi@raspi.local:~/apps/weather_app/
```

**Option C: Git clone**
```bash
# If your project is in git:
cd ~/apps/weather_app
git clone <your-repo-url> .
```

### 4. Configure Environment Variables

```bash
cd ~/apps/weather_app/backend

# Create .env file with your AWS credentials
cat > src/weather/.env << EOF
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-west-2
S3_BUCKET=manoa-raspi-weather
S3_PREFIX=samples
SAMPLE_INTERVAL_SEC=900
EOF

# Secure the .env file
chmod 600 src/weather/.env
```

### 5. Install Python Dependencies

```bash
cd ~/apps/weather_app/backend

# Install dependencies with uv
uv sync
```

### 6. Test the Application

```bash
# Test that Sense HAT is working
python3 -c "from sense_hat import SenseHat; s = SenseHat(); print(f'Temp: {s.get_temperature():.1f}°C')"

# Test the API manually
uv run uvicorn weather.api:app --host 0.0.0.0 --port 8000
```

In another terminal or browser, test the endpoints:
```bash
# From another machine on the same network:
curl http://raspi.local:8000/latest
curl http://raspi.local:8000/history?hours=1
```

Press `Ctrl+C` to stop the test server.

### 7. Set Up Systemd Service

```bash
cd ~/apps/weather_app

# Copy service file to systemd
sudo cp scripts/deploy/config/weather.service /etc/systemd/system/weather.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable weather.service
sudo systemctl start weather.service

# Check status
sudo systemctl status weather.service
```

## 🔍 Verification

### Check Service Status

```bash
# View service status
sudo systemctl status weather.service

# View logs
journalctl -u weather -f

# View last 100 lines
journalctl -u weather -n 100
```

### Test API Endpoints

```bash
# Get current reading
curl http://localhost:8000/latest

# Get 1 hour history
curl http://localhost:8000/history?hours=1
```

### Check S3 Uploads

```bash
cd ~/apps/weather_app/backend

# List uploaded objects
uv run python list_s3_objects.py
```

You should see new files appearing every 15 minutes (or your configured interval).

## 🔧 Configuration

### Change Sampling Interval

Edit `~/apps/weather_app/backend/src/weather/.env`:
```bash
# Sample every 5 minutes instead of 15
SAMPLE_INTERVAL_SEC=300
```

Then restart the service:
```bash
sudo systemctl restart weather.service
```

### Change S3 Bucket or Prefix

Edit the same `.env` file:
```bash
S3_BUCKET=my-new-bucket
S3_PREFIX=weather-data
```

Restart the service after changes.

## 🔄 Updating the Application

### Automated Update (from dev machine)

```bash
# On your development machine:
cd /Users/kevincoyle/side-projects/weather_app
./scripts/deploy/rsync_deploy.sh
```

This script will:
1. Sync code changes
2. Update dependencies
3. Restart the service

### Manual Update (on Pi)

```bash
cd ~/apps/weather_app

# Pull latest changes (if using git)
git pull

# Update dependencies
cd backend
uv sync

# Restart service
sudo systemctl restart weather.service
```

## 🐛 Troubleshooting

### Service Won't Start

**Check logs:**
```bash
journalctl -u weather -n 50 --no-pager
```

**Common issues:**

1. **Sense HAT not detected**
   ```bash
   # Test hardware
   i2cdetect -y 1
   # Should show devices at addresses like 0x5c, 0x5f, 0x6a
   
   # Try reinstalling
   sudo apt install --reinstall sense-hat
   ```

2. **Permission denied on GPIO**
   ```bash
   # Add pi user to i2c group
   sudo usermod -a -G i2c,spi,gpio pi
   # Logout and login again
   ```

3. **AWS credentials error**
   ```bash
   # Verify .env file exists and has correct permissions
   ls -la ~/apps/weather_app/backend/src/weather/.env
   cat ~/apps/weather_app/backend/src/weather/.env
   ```

4. **uv command not found**
   ```bash
   # Add to PATH permanently
   echo 'source $HOME/.cargo/env' >> ~/.bashrc
   source ~/.bashrc
   ```

### No Data in S3

**Test S3 connection:**
```bash
cd ~/apps/weather_app/backend
uv run python test_s3_upload.py
```

**Check S3 permissions:**
- Your IAM user/role needs: `s3:PutObject`, `s3:GetObject`, `s3:ListBucket`

**Verify bucket exists:**
```bash
# Install AWS CLI
sudo apt install awscli

# Test access
aws s3 ls s3://your-bucket-name/
```

### Service Running But Not Uploading

**Check logs for errors:**
```bash
journalctl -u weather -f | grep -i error
```

**Common causes:**
- Network connectivity issues
- Invalid AWS credentials
- S3 bucket doesn't exist
- Incorrect region

### High CPU Usage

The Sense HAT sensors are polled every sample interval. If CPU is high:

1. Increase `SAMPLE_INTERVAL_SEC` (e.g., 1800 for 30 minutes)
2. Check for runaway processes: `htop`

## 📊 Monitoring

### View Real-Time Logs

```bash
# Follow service logs
journalctl -u weather -f

# Filter for S3 uploads only
journalctl -u weather -f | grep "Uploaded to S3"
```

### Check Sensor Readings

```bash
# Simple Python script to check readings
python3 << 'EOF'
from sense_hat import SenseHat
sense = SenseHat()
print(f"Temperature: {sense.get_temperature():.1f}°C")
print(f"Humidity: {sense.get_humidity():.1f}%")
print(f"Pressure: {sense.get_pressure():.1f} hPa")
EOF
```

### Performance Monitoring

```bash
# CPU and memory usage
top -p $(pgrep -f "uvicorn weather.api")

# Service uptime
systemctl status weather.service | grep Active
```

## 🔐 Security Best Practices

1. **Secure .env file:**
   ```bash
   chmod 600 ~/apps/weather_app/backend/src/weather/.env
   ```

2. **Use IAM roles with minimal permissions:**
   - Only grant S3 access to your specific bucket
   - Use access keys with limited scope

3. **Keep system updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Change default Pi password:**
   ```bash
   passwd
   ```

5. **Enable firewall (optional):**
   ```bash
   sudo apt install ufw
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 8000/tcp # API (if accessing from other devices)
   sudo ufw enable
   ```

## 🔄 Maintenance Commands

```bash
# Restart service
sudo systemctl restart weather.service

# Stop service
sudo systemctl stop weather.service

# Start service
sudo systemctl start weather.service

# Disable service (prevent auto-start)
sudo systemctl disable weather.service

# View service configuration
systemctl cat weather.service

# Edit service configuration
sudo systemctl edit --full weather.service
```

## 📈 Advanced Configuration

### Expose API to Local Network

The service already binds to `0.0.0.0:8000`, making it accessible from other devices:

```bash
# From another device on same network:
curl http://raspi.local:8000/latest
# or
curl http://192.168.x.x:8000/latest
```

### Add HTTPS with Nginx (Optional)

```bash
# Install nginx
sudo apt install nginx

# Configure reverse proxy
sudo nano /etc/nginx/sites-available/weather

# Add:
server {
    listen 80;
    server_name raspi.local;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/weather /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Log Rotation

Create `/etc/logrotate.d/weather`:
```bash
sudo nano /etc/logrotate.d/weather
```

Add:
```
/var/log/weather.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## 🌐 Accessing From Frontend

Once your Raspberry Pi is running:

1. **Find Pi's IP address:**
   ```bash
   hostname -I
   ```

2. **Update frontend `.env.local`:**
   ```bash
   # On your dev machine:
   echo "NEXT_PUBLIC_API_URL=http://raspi.local:8000" > frontend/.env.local
   # or use IP:
   echo "NEXT_PUBLIC_API_URL=http://192.168.x.x:8000" > frontend/.env.local
   ```

3. **Restart frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

## 📱 Useful Scripts

All these are in the `backend/` directory:

- `test_s3_upload.py` - Test S3 connectivity
- `list_s3_objects.py` - List uploaded readings
- `generate_mock_data.py` - Generate test data

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Check status | `sudo systemctl status weather` |
| View logs | `journalctl -u weather -f` |
| Restart service | `sudo systemctl restart weather` |
| Test endpoint | `curl http://localhost:8000/latest` |
| List S3 files | `cd backend && uv run python list_s3_objects.py` |
| Update code | `./scripts/deploy/rsync_deploy.sh` (from dev machine) |

---

**Need help?** Check the main [README.md](../README.md) or [GETTING_STARTED.md](GETTING_STARTED.md)
