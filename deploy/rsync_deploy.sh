#!/usr/bin/env bash
set -euo pipefail
RSPI=pi@raspi.local
rsync -az --delete backend/  $RSPI:~/apps/weather_app/backend/
rsync -az --delete deploy/   $RSPI:~/apps/weather_app/deploy/
ssh $RSPI 'cd ~/apps/weather_app/backend && uv lock && uv sync && sudo systemctl restart weather.service'
