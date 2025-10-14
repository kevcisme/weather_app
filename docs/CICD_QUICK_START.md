# CI/CD Quick Start Guide

🎉 Your CI/CD pipeline is **almost ready**! Follow these steps to complete the setup.

## ✅ What's Done

- [x] GitHub Actions runner installed on Raspberry Pi
- [x] Runner service running and connected to GitHub
- [x] Workflow files created (`.github/workflows/`)
- [x] Service files created for runner workspace
- [x] Helper scripts created

## 🚀 Next Steps (5 minutes)

### Step 1: Update Services on Pi (2 min)

The services need to point to the GitHub runner's workspace instead of `~/apps/weather_app/`:

```bash
# SSH to your Pi
ssh pi@192.168.86.49

# Navigate to current app directory
cd ~/apps/weather_app

# Pull latest changes (needed to get new service files)
git pull

# Run the switch script
bash scripts/maintenance/switch-to-runner-services.sh
```

This updates your systemd services to use the runner workspace. Services will start after the first deployment.

### Step 2: Commit and Push Workflow Files (1 min)

Back on your Mac:

```bash
cd /Users/kevincoyle/side-projects/weather_app

# Add all the new CI/CD files
git add .github/workflows/
git add scripts/deploy/config/weather-runner.service
git add scripts/deploy/config/weather-frontend-runner.service
git add scripts/maintenance/switch-to-runner-services.sh
git add scripts/deploy/test-deployment.sh
git add scripts/maintenance/uninstall-runner.sh
git add CI_CD_SETUP.md
git add GITHUB_RUNNER_SETUP.md
git add CICD_QUICK_START.md

# Commit
git commit -m "Add GitHub Actions CI/CD pipeline"

# Push - this triggers your first automated deployment! 🚀
git push origin main
```

### Step 3: Watch the Magic! (2 min)

**Option A: Watch in GitHub**
1. Go to: https://github.com/kevcisme/weather_app/actions
2. You'll see your workflow running
3. Click on it to see real-time logs

**Option B: Watch on Pi**
```bash
ssh pi@192.168.86.49 'journalctl -u actions.runner.kevcisme-weather_app.pi-weather-station.service -f'
```

### Step 4: Verify It Works

After the workflow completes (about 1-2 minutes):

```bash
# Check services are running
ssh pi@192.168.86.49 'sudo systemctl status weather.service weather-frontend.service'

# Test the endpoints
curl http://192.168.86.49:8000/latest
curl http://192.168.86.49:3000
```

Or just visit in your browser:
- **Dashboard:** http://192.168.86.49:3000
- **API:** http://192.168.86.49:8000/latest

## 🎉 You're Done!

From now on, every time you push to `main` or `master`:
1. GitHub Actions automatically runs
2. Code is deployed to your Pi
3. Services are restarted
4. Health checks verify everything works

## 📝 Daily Usage

```bash
# Make changes
vim backend/src/weather/api.py

# Commit and push
git add .
git commit -m "Add new feature"
git push origin main

# ✨ Deployment happens automatically!
```

Watch progress: https://github.com/kevcisme/weather_app/actions

## 🧪 Test Your Pipeline

Want to test without making real changes?

```bash
./scripts/deploy/test-deployment.sh
```

This creates a harmless test commit and pushes it, triggering a deployment.

## 🔍 What Gets Deployed When

- **Backend changes** (`backend/**`) → Runs `deploy-backend.yml`
- **Frontend changes** (`frontend/**`) → Runs `deploy-frontend.yml`  
- **Everything else** → Runs `deploy.yml` (full deployment)
- **Manual trigger** → You choose which workflow to run

## 📊 Monitor Your Deployments

### View in GitHub
https://github.com/kevcisme/weather_app/actions

### View Service Logs on Pi
```bash
# Backend
ssh pi@192.168.86.49 'journalctl -u weather.service -f'

# Frontend
ssh pi@192.168.86.49 'journalctl -u weather-frontend.service -f'

# Both
ssh pi@192.168.86.49 'journalctl -u weather.service -u weather-frontend.service -f'
```

## 🐛 If Something Goes Wrong

### Deployment fails?
1. Check GitHub Actions logs: Repository → Actions → Click failed workflow
2. Check service status: `ssh pi@192.168.86.49 'sudo systemctl status weather.service'`
3. Check service logs: `ssh pi@192.168.86.49 'journalctl -u weather.service -n 50'`

### Runner not responding?
```bash
# Check runner status
ssh pi@192.168.86.49 'cd ~/actions-runner && sudo ./svc.sh status'

# Restart if needed
ssh pi@192.168.86.49 'cd ~/actions-runner && sudo ./svc.sh stop && sudo ./svc.sh start'
```

### Need to rollback?
```bash
git revert HEAD
git push origin main
```

## 📚 More Information

- **[CI_CD_SETUP.md](CI_CD_SETUP.md)** - Detailed CI/CD documentation
- **[GITHUB_RUNNER_SETUP.md](GITHUB_RUNNER_SETUP.md)** - Runner setup details
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Manual deployment reference

## 🎯 Key Points

✅ **Zero cost** - Uses your Pi's compute, not GitHub's  
✅ **No public ports** - Pi doesn't need to be internet-accessible  
✅ **Automatic** - Push to deploy  
✅ **Safe** - Health checks catch errors  
✅ **Fast** - Deploys in ~1-2 minutes  

---

**Ready?** Run Step 1 on your Pi, then Step 2 on your Mac! 🚀

