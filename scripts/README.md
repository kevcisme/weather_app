# Scripts

This directory contains all shell scripts organized by function.

## Directory Structure

### `deploy/`
Deployment and production-related scripts:
- `rsync_deploy.sh` - Quick deployment to Pi
- `rsync_deploy_configurable.sh` - Configurable deployment
- `first-time-deploy.sh` - Initial deployment setup
- `test-deployment.sh` - Test deployment workflow
- `watch-deployment.sh` - Watch deployment progress
- `config/` - Configuration files (systemd services, nginx)

### `maintenance/`
Maintenance and monitoring scripts:
- `check-status.sh` - Check overall system status
- `check-backend.sh` - Check backend service
- `restart_services.sh` - Restart all services
- `fix-data-collection.sh` - Fix data collection issues
- `fix-sense-hat.sh` - Fix Sense HAT issues
- `switch-to-runner-services.sh` - Switch to CI/CD runner services
- `uninstall-runner.sh` - Remove GitHub runner

### `setup/`
Initial setup and configuration scripts:
- `setup-pi.sh` - Complete Pi setup
- `setup-frontend.sh` - Frontend setup
- `setup-nginx.sh` - nginx configuration
- `setup-github-runner.sh` - GitHub Actions runner setup
- `configure-runner.sh` - Configure GitHub runner
- `enableservice.sh` - Enable systemd services
- `update-sudo-permissions.sh` - Update sudo permissions

### `dev/`
Development and testing scripts:
- `start-dev.sh` - Start local development environment
- `dev-frontend-with-pi.sh` - Frontend dev with Pi backend
- `test-from-mac.sh` - Test Pi from Mac
- `debug-daily-stats.sh` - Debug daily statistics

### `backend/`
Backend-specific scripts:
- `backendenv.sh` - Backend environment setup
- `quick-backfill.sh` - Quick data backfill
- `quick-ssh.sh` - Quick SSH to Pi

## Usage

All scripts should be run from the project root directory:

```bash
# Example: Deploy to Pi
./scripts/deploy/rsync_deploy.sh

# Example: Start development
./scripts/dev/start-dev.sh

# Example: Check status
./scripts/maintenance/check-status.sh
```

## Configuration Files

The `deploy/config/` directory contains:
- `*.service` - systemd service files
- `nginx-weather.conf` - nginx configuration

These are deployed to the Pi and installed in system locations.

