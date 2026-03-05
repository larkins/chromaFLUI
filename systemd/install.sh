#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="chromaflui"
SERVICE_FILE="$SCRIPT_DIR/$SERVICE_NAME.service"

echo "Installing $SERVICE_NAME as user service..."

# Check for CHROMADB_PATH
if [ -z "$CHROMADB_PATH" ]; then
    # Try to read from .env file
    if [ -f "$PROJECT_DIR/.env" ]; then
        CHROMADB_PATH=$(grep -E "^CHROMADB_PATH=" "$PROJECT_DIR/.env" | cut -d'=' -f2- || true)
    fi
    
    if [ -z "$CHROMADB_PATH" ]; then
        echo ""
        echo "Error: CHROMADB_PATH not set."
        echo ""
        echo "Set it via environment variable:"
        echo "  CHROMADB_PATH=/path/to/chromadb bash install.sh"
        echo ""
        echo "Or add to .env file:"
        echo "  CHROMADB_PATH=/path/to/chromadb"
        exit 1
    fi
fi

echo "Using CHROMADB_PATH: $CHROMADB_PATH"

# Create service file from template
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=ChromaDB Flask UI
After=network.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/.venv/bin:/usr/bin"
Environment="CONFIG_PATH=$PROJECT_DIR/config.yaml"
Environment="CHROMADB_PATH=$CHROMADB_PATH"
ExecStart=$PROJECT_DIR/.venv/bin/python app.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

# Copy service file to systemd user directory
mkdir -p ~/.config/systemd/user
cp "$SERVICE_FILE" ~/.config/systemd/user/

# Reload systemd daemon
systemctl --user daemon-reload

# Enable the service
systemctl --user enable "$SERVICE_NAME.service"

echo ""
echo "Installation complete!"
echo ""
echo "Commands:"
echo "  Start:   systemctl --user start $SERVICE_NAME"
echo "  Stop:    systemctl --user stop $SERVICE_NAME"
echo "  Status:  systemctl --user status $SERVICE_NAME"
echo "  Logs:    journalctl --user -u $SERVICE_NAME -f"
echo ""
echo "The service will start automatically on login."
echo "To start now: systemctl --user start $SERVICE_NAME"
