# CI/CD Pipeline Setup Guide

Complete guide for your GitHub Actions CI/CD pipeline on Raspberry Pi.

## 🎯 Overview

Your CI/CD pipeline automatically deploys code changes from GitHub to your Raspberry Pi whenever you push to the `main` or `master` branch.

### Architecture

```
┌─────────────────────────────────────────────────┐
│  Your Mac (Development)                         │
│  ├─ Edit code                                   │
│  ├─ git commit                                  │
│  └─ git push origin main                        │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  GitHub Repository                              │
│  └─ Triggers workflow                           │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  Raspberry Pi (192.168.86.49)                   │
│  ├─ GitHub Actions Runner (self-hosted)         │
│  ├─ Checks out code                             │
│  ├─ Installs dependencies                       │
│  ├─ Builds frontend                             │
│  ├─ Restarts services                           │
│  └─ Runs health checks                          │
└─────────────────────────────────────────────────┘
```

## ✅ Current Status

- [x] Phase 1: GitHub Actions runner installed on Pi
- [x] Phase 2: Workflow files created
- [ ] Phase 3: Services configured for runner workspace
- [ ] Phase 4: First deployment tested

## 📁 Workflow Files

Three workflow files have been created:

### 1. `deploy.yml` - Full Deployment
**Triggers:** Any push to main/master, or manual trigger  
**What it does:**
- Deploys both backend and frontend
- Restarts both services
- Runs health checks on both

**Use when:** You want to deploy everything

### 2. `deploy-backend.yml` - Backend Only
**Triggers:** Push to main/master that changes `backend/**` files  
**What it does:**
- Deploys only backend
- Restarts backend service
- Runs backend health check

**Use when:** You only changed Python/backend code

### 3. `deploy-frontend.yml` - Frontend Only
**Triggers:** Push to main/master that changes `frontend/**` files  
**What it does:**
- Deploys only frontend
- Restarts frontend service
- Runs frontend health check

**Use when:** You only changed React/frontend code

## 🚀 Phase 3: Update Services for Runner

Before the workflows will work, you need to update your systemd services to point to the GitHub runner's workspace.

### Current Setup (Old)
- Code location: `/home/pi/apps/weather_app/`
- Deployed via: `rsync_deploy.sh` script

### New Setup (CI/CD)
- Code location: `/home/pi/actions-runner/_work/weather_app/weather_app/`
- Deployed via: GitHub Actions workflows

### Switch to New Setup

Run this on your Pi:

```bash
ssh pi@192.168.86.49

# Navigate to your current app directory
cd ~/apps/weather_app

# Pull the latest changes (includes new service files)
git pull

# Run the switch script
chmod +x deploy/switch-to-runner-services.sh
bash deploy/switch-to-runner-services.sh
```

This will:
1. Stop current services
2. Update service files to point to runner workspace
3. Reload systemd
4. Enable services (they'll start after first deployment)

## 📦 Phase 4: First Deployment

After switching services, commit and push your workflow files:

```bash
# On your Mac
cd /Users/kevincoyle/side-projects/weather_app

# Stage the workflow files
git add .github/workflows/
git add deploy/weather-runner.service
git add deploy/weather-frontend-runner.service
git add deploy/switch-to-runner-services.sh
git add CI_CD_SETUP.md
git add GITHUB_RUNNER_SETUP.md

# Commit
git commit -m "Add GitHub Actions CI/CD pipeline"

# Push (this will trigger the first deployment!)
git push origin main
```

### What Happens Next

1. **GitHub receives your push**
2. **Workflow is triggered** on your Pi's runner
3. **Runner checks out code** to `~/actions-runner/_work/weather_app/weather_app/`
4. **Backend deployment:**
   - Installs dependencies with `uv sync`
   - Restarts `weather.service`
5. **Frontend deployment:**
   - Installs dependencies with `npm ci`
   - Builds production bundle with `npm run build`
   - Restarts `weather-frontend.service`
6. **Health checks:**
   - Tests backend at `http://localhost:8000/latest`
   - Tests frontend at `http://localhost:3000`
7. **Success!** 🎉

### Monitor the Deployment

#### Watch in GitHub
1. Go to your repository
2. Click **Actions** tab
3. See your workflow running in real-time

#### Watch on Pi (Optional)
```bash
ssh pi@192.168.86.49

# Watch runner logs
journalctl -u actions.runner.kevcisme-weather_app.pi-weather-station.service -f

# Watch service logs
journalctl -u weather.service -u weather-frontend.service -f
```

## 🎉 Usage After Setup

Once everything is configured, your workflow is simple:

```bash
# Edit your code
vim backend/src/weather/api.py

# Commit changes
git add .
git commit -m "Add new API endpoint"

# Push to GitHub
git push origin main

# ✨ Automatic deployment happens!
```

You can watch the deployment progress in GitHub → Actions tab.

## 🔧 Manual Deployment Trigger

You can also trigger deployments manually without pushing code:

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select a workflow (e.g., "Deploy to Raspberry Pi")
4. Click **Run workflow** button
5. Select branch and click **Run workflow**

## 📊 Monitoring

### Check Deployment Status
**GitHub:** Repository → Actions tab

### Check Service Status
```bash
ssh pi@192.168.86.49 'sudo systemctl status weather.service weather-frontend.service'
```

### View Service Logs
```bash
# Backend logs
ssh pi@192.168.86.49 'journalctl -u weather.service -f'

# Frontend logs
ssh pi@192.168.86.49 'journalctl -u weather-frontend.service -f'

# Both
ssh pi@192.168.86.49 'journalctl -u weather.service -u weather-frontend.service -f'
```

### Check Runner Status
```bash
ssh pi@192.168.86.49 'cd ~/actions-runner && sudo ./svc.sh status'
```

## 🐛 Troubleshooting

### Workflow doesn't trigger
- Check that your branch name is `main` or `master`
- Verify the runner shows as "Idle" in GitHub → Settings → Actions → Runners
- Check runner is running: `ssh pi@192.168.86.49 'systemctl status actions.runner.*'`

### Deployment fails at "Deploy Backend" step
- SSH to Pi and check: `cd ~/actions-runner/_work/weather_app/weather_app/backend && uv sync`
- Verify uv is installed: `ssh pi@192.168.86.49 'which uv'`

### Deployment fails at "Deploy Frontend" step
- Check Node.js is installed: `ssh pi@192.168.86.49 'node --version'`
- Check npm is working: `ssh pi@192.168.86.49 'npm --version'`

### Health checks fail
- Check services are running: `ssh pi@192.168.86.49 'sudo systemctl status weather.service weather-frontend.service'`
- Check service logs: `ssh pi@192.168.86.49 'journalctl -u weather.service -n 50'`
- Verify ports aren't blocked: `ssh pi@192.168.86.49 'curl http://localhost:8000/latest'`

### "Permission denied" when restarting services
- Verify sudo permissions: `ssh pi@192.168.86.49 'sudo cat /etc/sudoers.d/github-runner'`
- Should contain line about systemctl restart commands

## 🔄 Rollback

If a deployment breaks something, you can quickly rollback:

### Option 1: Revert Git Commit
```bash
# On your Mac
git revert HEAD
git push origin main
# This triggers a new deployment with the reverted code
```

### Option 2: Manual Rollback on Pi
```bash
ssh pi@192.168.86.49

# Go to runner workspace
cd ~/actions-runner/_work/weather_app/weather_app

# Checkout previous commit
git checkout HEAD~1

# Restart services
sudo systemctl restart weather.service weather-frontend.service
```

## 🔐 Security Notes

- ✅ No public ports opened on Pi
- ✅ No credentials in repository (uses .env files on Pi)
- ✅ Runner uses same user permissions as manual deployment
- ✅ HTTPS communication with GitHub

## 📚 Quick Reference

| Task | Command |
|------|---------|
| Trigger deployment | `git push origin main` |
| Manual trigger | GitHub → Actions → Run workflow |
| Check runner | `ssh pi@192.168.86.49 'cd ~/actions-runner && sudo ./svc.sh status'` |
| View workflow logs | GitHub → Actions → Click on workflow run |
| View service logs | `ssh pi@192.168.86.49 'journalctl -u weather.service -f'` |
| Restart runner | `ssh pi@192.168.86.49 'cd ~/actions-runner && sudo ./svc.sh stop && sudo ./svc.sh start'` |

## 📖 Related Documentation

- [GITHUB_RUNNER_SETUP.md](GITHUB_RUNNER_SETUP.md) - Runner installation details
- [DEPLOYMENT.md](DEPLOYMENT.md) - Manual deployment reference
- [README.md](README.md) - Project overview

