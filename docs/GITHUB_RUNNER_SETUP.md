# GitHub Actions Self-Hosted Runner Setup

## ✅ Phase 1 Complete!

The GitHub Actions runner has been downloaded and extracted on your Raspberry Pi at `/home/pi/actions-runner`.

## 📝 Next Steps

### Step 1: Get Your GitHub Registration Token

1. Go to your GitHub repository: **https://github.com/YOUR_USERNAME/weather_app**
2. Click **Settings** (top menu)
3. Click **Actions** (left sidebar)
4. Click **Runners** (left sidebar under Actions)
5. Click the green **"New self-hosted runner"** button
6. Select **Linux** as the OS
7. Select **ARM64** as the architecture
8. Look for the **"Configure"** section
9. Copy the **token** from the command that looks like:
   ```bash
   ./config.sh --url https://github.com/YOUR_USERNAME/weather_app --token ABCDEF123456...
   ```
   The token is the long string after `--token`

### Step 2: Configure the Runner on Your Pi

You have two options:

#### Option A: Use the Helper Script (Easier)

```bash
ssh pi@192.168.86.49
bash ~/configure-runner.sh YOUR_GITHUB_TOKEN https://github.com/YOUR_USERNAME/weather_app
```

This script will:
- Configure the runner with your repository
- Set up sudo permissions for service management
- Install the runner as a systemd service
- Start the runner automatically

#### Option B: Manual Configuration

```bash
ssh pi@192.168.86.49
cd ~/actions-runner

# Configure
./config.sh --url https://github.com/YOUR_USERNAME/weather_app --token YOUR_TOKEN

# Set up sudo permissions
echo "$USER ALL=(ALL) NOPASSWD: /bin/systemctl restart weather.service, /bin/systemctl restart weather-frontend.service" | sudo tee /etc/sudoers.d/github-runner
sudo chmod 0440 /etc/sudoers.d/github-runner

# Install as service
sudo ./svc.sh install
sudo ./svc.sh start
```

### Step 3: Verify the Runner is Connected

1. Go back to your GitHub repository
2. Go to **Settings → Actions → Runners**
3. You should see your runner listed with a green "Idle" status

## 🔧 Managing Your Runner

### Check Status
```bash
ssh pi@192.168.86.49 'sudo ~/actions-runner/svc.sh status'
```

### Stop Runner
```bash
ssh pi@192.168.86.49 'sudo ~/actions-runner/svc.sh stop'
```

### Start Runner
```bash
ssh pi@192.168.86.49 'sudo ~/actions-runner/svc.sh start'
```

### View Logs
```bash
ssh pi@192.168.86.49 'journalctl -u actions.runner.* -f'
```

## 🚀 What's Next?

Once your runner is connected and showing as "Idle" in GitHub:
- **Phase 2**: Create GitHub Actions workflow files
- **Phase 3**: Test automated deployment

## 📚 Quick Reference

| Task | Command |
|------|---------|
| Setup runner | `bash ~/apps/weather_app/scripts/setup/setup-github-runner.sh` |
| Configure runner | `bash ~/apps/weather_app/scripts/setup/configure-runner.sh TOKEN REPO_URL` |
| Check runner status | `sudo ~/actions-runner/svc.sh status` |
| View runner logs | `journalctl -u actions.runner.* -f` |
| Restart runner | `sudo ~/actions-runner/svc.sh stop && sudo ~/actions-runner/svc.sh start` |

## 🐛 Troubleshooting

### Runner not showing in GitHub
- Check if the service is running: `sudo ~/actions-runner/svc.sh status`
- Check logs: `journalctl -u actions.runner.* -f`
- Verify network connectivity: `ping github.com`

### Service fails to start
- Check configuration: `cd ~/actions-runner && ./config.sh --help`
- Verify token hasn't expired (tokens expire after 1 hour)
- Try reconfiguring with a fresh token

### Permission denied when restarting services
- Verify sudo permissions: `sudo cat /etc/sudoers.d/github-runner`
- Should contain: `pi ALL=(ALL) NOPASSWD: /bin/systemctl restart weather.service...`

