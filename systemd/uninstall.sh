#!/bin/bash
set -e

SERVICE_NAME="chromaflui"

echo "Uninstalling $SERVICE_NAME user service..."

# Stop the service if running
systemctl --user stop "$SERVICE_NAME.service" 2>/dev/null || true

# Disable the service
systemctl --user disable "$SERVICE_NAME.service" 2>/dev/null || true

# Remove service file
rm -f ~/.config/systemd/user/"$SERVICE_NAME.service"

# Reload systemd daemon
systemctl --user daemon-reload

echo "Uninstallation complete!"
