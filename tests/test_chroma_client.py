import os
import tempfile
import yaml


def test_load_config():
    from chroma_client import load_config

    config_content = {
        "app": {"name": "Test App"},
        "server": {"host": "0.0.0.0", "port": 5000},
        "chromadb": {"path": "/test/path"},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_content, f)
        config_path = f.name

    old_path = os.environ.get("CONFIG_PATH")
    os.environ["CONFIG_PATH"] = config_path

    try:
        config = load_config()
        assert config["app"]["name"] == "Test App"
        assert config["server"]["port"] == 5000
    finally:
        os.unlink(config_path)
        if old_path:
            os.environ["CONFIG_PATH"] = old_path
        else:
            os.environ.pop("CONFIG_PATH", None)


def test_load_config_with_env_var():
    from chroma_client import load_config

    config_content = {
        "chromadb": {"path": "${TEST_CHROMA_PATH}"},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_content, f)
        config_path = f.name

    old_config_path = os.environ.get("CONFIG_PATH")
    old_chroma_path = os.environ.get("TEST_CHROMA_PATH")
    os.environ["CONFIG_PATH"] = config_path
    os.environ["TEST_CHROMA_PATH"] = "/custom/path"

    try:
        config = load_config()
        assert config["chromadb"]["path"] == "/custom/path"
    finally:
        os.unlink(config_path)
        if old_config_path:
            os.environ["CONFIG_PATH"] = old_config_path
        else:
            os.environ.pop("CONFIG_PATH", None)
        if old_chroma_path:
            os.environ["TEST_CHROMA_PATH"] = old_chroma_path
        else:
            os.environ.pop("TEST_CHROMA_PATH", None)
