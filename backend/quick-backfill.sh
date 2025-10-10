#!/bin/bash
# Quick backfill helper script for common scenarios

set -e

cd "$(dirname "$0")"

echo "=================================="
echo "  Quick Backfill Helper"
echo "=================================="
echo ""
echo "Select backfill scenario:"
echo ""
echo "1. Preview last 24 hours (dry run)"
echo "2. Backfill last 24 hours"
echo "3. Backfill last 7 days"
echo "4. Backfill last 30 days"
echo "5. Custom (specify days)"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "🔍 Running dry run for last 24 hours..."
        python backfill_silver.py --days 1 --dry-run
        ;;
    2)
        echo ""
        echo "🚀 Backfilling last 24 hours..."
        read -p "Are you sure? This will write to S3. [y/N]: " confirm
        if [[ $confirm == [yY] ]]; then
            python backfill_silver.py --days 1
        else
            echo "Cancelled."
        fi
        ;;
    3)
        echo ""
        echo "🚀 Backfilling last 7 days..."
        read -p "Are you sure? This will write ~672 files to S3. [y/N]: " confirm
        if [[ $confirm == [yY] ]]; then
            python backfill_silver.py --days 7
        else
            echo "Cancelled."
        fi
        ;;
    4)
        echo ""
        echo "🚀 Backfilling last 30 days..."
        read -p "Are you sure? This will write ~2,880 files to S3. [y/N]: " confirm
        if [[ $confirm == [yY] ]]; then
            python backfill_silver.py --days 30
        else
            echo "Cancelled."
        fi
        ;;
    5)
        echo ""
        read -p "Enter number of days (1-30): " days
        if [[ $days -ge 1 ]] && [[ $days -le 30 ]]; then
            read -p "Dry run? [y/N]: " dryrun
            if [[ $dryrun == [yY] ]]; then
                python backfill_silver.py --days $days --dry-run
            else
                echo ""
                read -p "This will write to S3. Continue? [y/N]: " confirm
                if [[ $confirm == [yY] ]]; then
                    python backfill_silver.py --days $days
                else
                    echo "Cancelled."
                fi
            fi
        else
            echo "Invalid number of days. Must be between 1 and 30."
        fi
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "Done!"

