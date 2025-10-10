#!/bin/bash

# Script to watch deployment and verify daily stats are working

PI_HOST="192.168.86.49"
PI_USER="pi"

echo "⏳ Waiting for deployment to complete..."
echo "This will check every 10 seconds for the next 2 minutes"
echo ""

for i in {1..12}; do
    echo "Check $i/12..."
    
    # Check if the new code is deployed by looking at git log
    LATEST_COMMIT=$(ssh ${PI_USER}@${PI_HOST} "cd /home/pi/actions-runner/_work/weather_app/weather_app 2>/dev/null && git log -1 --oneline 2>/dev/null" 2>/dev/null)
    echo "  Latest commit: $LATEST_COMMIT"
    
    # Check if service is running
    SERVICE_STATUS=$(ssh ${PI_USER}@${PI_HOST} "systemctl is-active weather.service" 2>/dev/null)
    echo "  Service status: $SERVICE_STATUS"
    
    # If service is active, check the logs for our new debug output
    if [ "$SERVICE_STATUS" = "active" ]; then
        echo "  Checking for daily stats in recent logs..."
        STATS=$(ssh ${PI_USER}@${PI_HOST} "journalctl -u weather.service -n 20 --no-pager 2>/dev/null | grep -i 'sample timestamps\|after filtering'" 2>/dev/null | tail -2)
        if [ ! -z "$STATS" ]; then
            echo "  ✅ Found new logging!"
            echo "$STATS" | sed 's/^/    /'
            echo ""
            echo "🎉 Deployment appears to be complete!"
            echo ""
            echo "Testing endpoint..."
            RESULT=$(ssh ${PI_USER}@${PI_HOST} "curl -s http://localhost:8000/latest" 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"Daily stats: min={d.get('daily_temp_min')}, max={d.get('daily_temp_max')}, avg={d.get('daily_temp_avg')}\")" 2>/dev/null)
            echo "$RESULT"
            
            if [[ "$RESULT" == *"None"* ]]; then
                echo ""
                echo "⚠️  Daily stats are still None - checking logs for why..."
                ssh ${PI_USER}@${PI_HOST} "journalctl -u weather.service -n 10 --no-pager | grep -i 'filtering\|readings from today'"
            else
                echo ""
                echo "✅ SUCCESS! Daily stats are now populated!"
            fi
            exit 0
        fi
    fi
    
    if [ $i -lt 12 ]; then
        sleep 10
    fi
done

echo ""
echo "⏱️  Timed out waiting for deployment. Check manually with:"
echo "   ssh ${PI_USER}@${PI_HOST} 'sudo systemctl status weather.service'"

