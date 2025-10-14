sudo cp deploy/weather.service /etc/systemd/system/weather.service
sudo systemctl daemon-reload
sudo systemctl enable --now weather.service
