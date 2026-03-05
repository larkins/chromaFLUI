# ChromaDB Flask UI

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A lightweight, local browser UI for inspecting and managing ChromaDB vector databases. Built with Flask, no external dependencies beyond Python.

## Features

- **Collection Browser** - View all collections with document counts and metadata
- **Document Viewer** - Browse documents with pagination, view content and metadata
- **Semantic Search** - Query collections using natural language
- **Document Management** - Add and delete documents through the UI or API
- **Collection Management** - Create and delete collections
- **REST API** - Full API for programmatic access
- **Systemd Support** - Run as a user service on Linux

## Requirements

- Python 3.10+
- ChromaDB database (local persistent storage)

## Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/larkins/chromaFLUI.git
cd chromaFLUI

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and set CHROMADB_PATH to your ChromaDB location

# Run
python app.py
```

Open http://localhost:5012 in your browser.

### Systemd Service (Linux)

Run as a background service:

```bash
bash systemd/install.sh
systemctl --user start chromaflui
```

Commands:

| Action | Command |
|--------|---------|
| Start | `systemctl --user start chromaflui` |
| Stop | `systemctl --user stop chromaflui` |
| Status | `systemctl --user status chromaflui` |
| Logs | `journalctl --user -u chromaflui -f` |
| Uninstall | `bash systemd/uninstall.sh` |

## Configuration

### Environment Variables (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_SECRET_KEY` | Secret key for sessions | Required |
| `CHROMADB_PATH` | Path to ChromaDB storage | Required |

### config.yaml

```yaml
app:
  name: ChromaDB Flask UI
  debug: false

server:
  host: "0.0.0.0"
  port: 5012

chromadb:
  path: "${CHROMADB_PATH}"
  tenant: default_tenant
  database: default_database

ui:
  items_per_page: 50
  dark_mode: false
  show_scores: true

logging:
  level: INFO
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web UI homepage |
| GET | `/api/collections` | List all collections |
| GET | `/api/collections/<name>` | Get collection details |
| GET | `/api/collections/<name>/documents` | List documents (params: `limit`, `offset`) |
| POST | `/api/collections/<name>/search` | Semantic search (body: `query`, `n_results`, `where`) |
| POST | `/api/collections/<name>/documents` | Add document (body: `document`, `id`, `metadata`) |
| DELETE | `/api/collections/<name>/documents/<id>` | Delete document |
| POST | `/api/collections` | Create collection (body: `name`, `metadata`) |
| DELETE | `/api/collections/<name>` | Delete collection |

### Example: Search

```bash
curl -X POST http://localhost:5012/api/collections/memories/search \
  -H "Content-Type: application/json" \
  -d '{"query": "python programming", "n_results": 5}'
```

## Development

### Setup

```bash
pip install -r requirements.txt
pip install pytest ruff black mypy
```

### Test

```bash
python -m pytest tests/ -v
```

### Lint & Format

```bash
ruff check .
black .
mypy . --ignore-missing-imports
```

## Project Structure

```
chromaFLUI/
├── app.py              # Flask application
├── chroma_client.py    # ChromaDB client wrapper
├── config.yaml         # Application config
├── .env                # Environment variables
├── requirements.txt    # Dependencies
├── templates/          # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   └── collection.html
├── static/             # CSS and JavaScript
│   ├── css/style.css
│   └── js/app.js
├── systemd/            # Systemd service files
│   ├── chromaflui.service
│   ├── install.sh
│   └── uninstall.sh
└── tests/              # Test suite
    ├── test_api.py
    └── test_chroma_client.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ChromaDB locked | Only one process can access ChromaDB at a time. Stop other services using it. |
| Import errors | Ensure virtual environment is activated: `source .venv/bin/activate` |
| Port 5012 in use | Change `port` in `config.yaml` |
| No documents showing | Verify `CHROMADB_PATH` points to correct directory |
| Permission denied | Ensure user has read/write access to ChromaDB path |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and lint (`pytest tests/ -v && ruff check .`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Acknowledgments

Built with [OpenCode](https://opencode.ai) + [GLM-5](https://huggingface.co/zai-org/GLM-5).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
