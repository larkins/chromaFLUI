# Systemd Service

Install chromaflui as a user-level systemd service.

## Install

Set the `CHROMADB_PATH` environment variable and run the install script:

```bash
CHROMADB_PATH=/path/to/your/chromadb bash install.sh
```

Or add it to your `.env` file in the project root:

```
CHROMADB_PATH=/path/to/your/chromadb
```

Then run:

```bash
bash install.sh
```

This will:
- Read `CHROMADB_PATH` from environment or `.env` file
- Generate the service file with correct paths
- Copy the service file to `~/.config/systemd/user/`
- Enable the service to start on login

## Commands

```bash
systemctl --user start chromaflui     # Start service
systemctl --user stop chromaflui      # Stop service
systemctl --user restart chromaflui   # Restart service
systemctl --user status chromaflui    # Check status
journalctl --user -u chromaflui -f    # Follow logs
```

## Uninstall

```bash
bash uninstall.sh
```

## Updating CHROMADB_PATH

To change the ChromaDB path after installation:

```bash
# Update .env file
echo "CHROMADB_PATH=/new/path" > ../.env

# Reinstall the service
CHROMADB_PATH=/new/path bash install.sh
systemctl --user restart chromaflui
```
