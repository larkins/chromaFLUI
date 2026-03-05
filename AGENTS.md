# AGENTS.md — ChromaDB Flask UI

Local browser UI for inspecting and managing ChromaDB databases. Built with Flask, no external dependencies beyond Python.

---

## Commands

### Setup
> Always use a virtual environment. Never install packages with system Python.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install flask python-dotenv pyyaml chromadb
```

### Run
```bash
source .venv/bin/activate
python app.py                    # Run Flask dev server
FLASK_DEBUG=1 python app.py     # Run with debug mode
```

### Lint & Type Check
```bash
pip install ruff black mypy
ruff check .                        # Lint
ruff check . --fix                 # Auto-fix lint issues
black .                             # Format
mypy . --ignore-missing-imports    # Type check
```

### Test
```bash
pip install pytest
python -m pytest tests/ -v
python -m pytest tests/ -v --tb=short  # With short traceback
python -m pytest tests/test_api.py -v  # Single test file
python -m pytest tests/test_api.py::test_list_collections -v  # Single test
```

---

## Code Style Guidelines

### General
- Max line length: 100 characters
- 4 spaces indentation (no tabs)
- Shebang `#!/usr/bin/env python` for scripts
- `set -e` in shell scripts
- Use `logging` module, not `print()` for production code

### Imports (ordered by specificity)
```python
import os
import sys
from pathlib import Path

import chromadb
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

from .local_module import something
```

### Naming
- `snake_case`: functions, variables, methods
- `PascalCase`: classes, exceptions
- `SCREAMING_SNAKE_CASE`: constants
- Prefix private with `_`
- Descriptive names (min 3 chars)

### Types
```python
def get_collection(name: str) -> dict[str, Any]:
    ...

def maybe_get() -> str | None:
    ...

DB_PATH: Final[str] = "./storage/chroma/mem0"
```

### Error Handling
```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except Exception as e:
    logger.exception("Unexpected error")
    return {"error": str(e)}, 500
```

### Functions
- Under 50 lines
- Single responsibility
- Early returns for guard clauses
- Type hints on all public functions

### Flask Routes
```python
@app.route("/api/collections")
def list_collections() -> tuple[str, int]:
    try:
        collections = get_all_collections()
        return jsonify(collections), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Documentation
- Docstrings for public APIs (Google-style preferred)
- Inline comments only for non-obvious logic

### Configuration
- `.env` for secrets and environment-specific values
- `config.yaml` for application settings
- `config.example.yaml` for template
- Never commit `.env` files

---

## Project Structure
```
chromaflui/
├── AGENTS.md               # This file
├── README.md               # Project documentation
├── .env                    # Local secrets (gitignored)
├── .env.example            # Template for .env
├── config.yaml             # Application config
├── config.example.yaml     # Template for config
├── .gitignore              # Git ignore rules
├── app.py                  # Flask application entry
├── requirements.txt        # pip dependencies
├── chroma_client.py        # ChromaDB client wrapper
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   └── collection.html
├── static/                 # CSS, JS, images
│   ├── css/
│   └── js/
└── tests/                  # pytest tests
    ├── __init__.py
    ├── test_api.py
    └── test_chroma_client.py
```

---

## Configuration

### .env (secrets, not committed)
```
FLASK_SECRET_KEY=your-secret-key-here
CHROMADB_PATH=/path/to/chromadb
```

### .env.example (template, committed)
```
FLASK_SECRET_KEY=change-me
CHROMADB_PATH=./storage/chroma/mem0
```

### config.yaml (application settings)
```yaml
app:
  name: ChromaDB Flask UI
  debug: false
  
server:
  host: "0.0.0.0"
  port: 5012

chromadb:
  path: "${CHROMADB_PATH}"  # References .env variable
  tenant: default_tenant
  database: default_database

ui:
  items_per_page: 50
  dark_mode: false
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web UI homepage |
| GET | `/api/collections` | List all collections |
| GET | `/api/collections/<name>` | Get collection details |
| GET | `/api/collections/<name>/documents` | List documents |
| POST | `/api/collections/<name>/search` | Semantic search |
| POST | `/api/collections/<name>/documents` | Add document |
| DELETE | `/api/collections/<name>/documents/<id>` | Delete document |
| POST | `/api/collections` | Create collection |
| DELETE | `/api/collections/<name>` | Delete collection |

---

## UI Features

### Collection Browser
- List all collections with document counts
- Click to view collection details
- Pagination for large collections

### Document Viewer
- Display document content and metadata
- Edit document metadata
- Delete documents

### Search Interface
- Semantic search input
- Filter by metadata
- Sort by relevance score

### Collection Management
- Create new collection
- Delete collection (with confirmation)
- View collection schema

---

## Connecting to ChromaDB

Set the `CHROMADB_PATH` environment variable to point to your ChromaDB storage directory:

```bash
export CHROMADB_PATH=/path/to/your/chromadb/storage
python app.py
```

Or configure it in `.env`:

```
CHROMADB_PATH=/path/to/your/chromadb/storage
```

Or set it directly in `config.yaml`:

```yaml
chromadb:
  path: "/path/to/your/chromadb/storage"
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| ChromaDB locked | Stop chroma-ui service: `systemctl --user stop chroma-ui` |
| Import errors | Activate venv: `source .venv/bin/activate` |
| Port 5012 in use | Change port in config.yaml or `flask run -p 5001` |
| No documents showing | Check CHROMADB_PATH points to correct directory |
| Permission denied | Ensure user has read/write access to ChromaDB path |

---

## Development Workflow

1. Create feature branch from `main`
2. Write tests first (TDD when practical)
3. Implement feature
4. Run `ruff check .` and fix issues
5. Run tests: `pytest tests/ -v`
6. All tests must pass before commit
7. Never commit `.env` or secrets
