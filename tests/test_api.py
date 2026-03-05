import os
import sys
import tempfile
import pytest
import yaml


@pytest.fixture(scope="module")
def test_config():
    config_content = {
        "app": {"name": "Test", "debug": True},
        "server": {"host": "127.0.0.1", "port": 5000},
        "chromadb": {"path": tempfile.mkdtemp()},
        "ui": {"items_per_page": 10},
        "logging": {"level": "DEBUG"},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_content, f)
        config_path = f.name

    old_config_path = os.environ.get("CONFIG_PATH")
    os.environ["CONFIG_PATH"] = config_path
    os.environ["CHROMADB_PATH"] = config_content["chromadb"]["path"]

    yield config_path

    if old_config_path:
        os.environ["CONFIG_PATH"] = old_config_path
    else:
        os.environ.pop("CONFIG_PATH", None)
    os.unlink(config_path)


@pytest.fixture
def app(test_config):
    if "app" in sys.modules:
        del sys.modules["app"]
    if "chroma_client" in sys.modules:
        del sys.modules["chroma_client"]

    import app as flask_app

    flask_app.chroma_client = None

    yield flask_app.app


@pytest.fixture
def client(app):
    return app.test_client()


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200


def test_api_list_collections(client):
    response = client.get("/api/collections")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_api_create_collection(client):
    response = client.post("/api/collections", json={"name": "test_collection"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "test_collection"


def test_api_create_collection_missing_name(client):
    response = client.post("/api/collections", json={})
    assert response.status_code == 400


def test_api_get_collection(client):
    client.post("/api/collections", json={"name": "test_get"})
    response = client.get("/api/collections/test_get")
    assert response.status_code == 200


def test_api_get_collection_not_found(client):
    response = client.get("/api/collections/nonexistent")
    assert response.status_code == 404


def test_api_add_document(client):
    client.post("/api/collections", json={"name": "test_docs"})
    response = client.post(
        "/api/collections/test_docs/documents",
        json={"document": "Test document content"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"


def test_api_add_document_missing_content(client):
    client.post("/api/collections", json={"name": "test_docs2"})
    response = client.post("/api/collections/test_docs2/documents", json={})
    assert response.status_code == 400


def test_api_search(client):
    client.post("/api/collections", json={"name": "test_search"})
    client.post(
        "/api/collections/test_search/documents", json={"document": "Hello world"}
    )
    response = client.post(
        "/api/collections/test_search/search", json={"query": "hello"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_api_search_missing_query(client):
    client.post("/api/collections", json={"name": "test_search2"})
    response = client.post("/api/collections/test_search2/search", json={})
    assert response.status_code == 400


def test_api_delete_collection(client):
    client.post("/api/collections", json={"name": "to_delete"})
    response = client.delete("/api/collections/to_delete")
    assert response.status_code == 200
