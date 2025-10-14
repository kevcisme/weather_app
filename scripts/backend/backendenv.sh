curl -LsSf https://astral.sh/uv/install.sh | sh
cd ~/apps/raspi-weather-station/backend
uv lock && uv sync
uv run uvicorn weather.api:app --host 0.0.0.0 --port 8000
