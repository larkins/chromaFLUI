#!/usr/bin/env python
import logging
import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from chroma_client import ChromaClient, load_config

load_dotenv()

config = load_config()
logging.basicConfig(
    level=getattr(logging, config.get("logging", {}).get("level", "INFO")),
    format=config.get("logging", {}).get(
        "format",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    ),
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

chroma_client: ChromaClient | None = None


def get_client() -> ChromaClient:
    global chroma_client
    if chroma_client is None:
        chroma_client = ChromaClient()
    return chroma_client


@app.route("/")
def index() -> str:
    try:
        client = get_client()
        collections = client.list_collections()
        return render_template("index.html", collections=collections)
    except Exception as e:
        logger.exception("Error loading index")
        return render_template("index.html", collections=[], error=str(e))


@app.route("/collection/<name>")
def collection_view(name: str) -> str:
    try:
        client = get_client()
        collection = client.get_collection(name)
        if collection is None:
            return render_template("collection.html", error="Collection not found")

        page = request.args.get("page", 1, type=int)
        per_page = config.get("ui", {}).get("items_per_page", 50)
        offset = (page - 1) * per_page

        documents_data = client.get_documents(name, limit=per_page, offset=offset)
        total_pages = (documents_data["total"] + per_page - 1) // per_page

        return render_template(
            "collection.html",
            collection=collection,
            documents=documents_data["documents"],
            total=documents_data["total"],
            page=page,
            total_pages=total_pages,
            per_page=per_page,
        )
    except Exception as e:
        logger.exception(f"Error loading collection {name}")
        return render_template("collection.html", error=str(e))


@app.route("/api/collections")
def api_list_collections() -> tuple[Any, int]:
    try:
        client = get_client()
        collections = client.list_collections()
        return jsonify(collections), 200
    except Exception as e:
        logger.exception("Error listing collections")
        return jsonify({"error": str(e)}), 500


@app.route("/api/collections/<name>")
def api_get_collection(name: str) -> tuple[Any, int]:
    try:
        client = get_client()
        collection = client.get_collection(name)
        if collection is None:
            return jsonify({"error": "Collection not found"}), 404
        return jsonify(collection), 200
    except Exception as e:
        logger.exception(f"Error getting collection {name}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/collections/<name>/documents")
def api_get_documents(name: str) -> tuple[Any, int]:
    try:
        client = get_client()
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        documents = client.get_documents(name, limit=limit, offset=offset)
        return jsonify(documents), 200
    except Exception as e:
        logger.exception(f"Error getting documents from {name}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/collections/<name>/search", methods=["POST"])
def api_search(name: str) -> tuple[Any, int]:
    try:
        client = get_client()
        data = request.get_json() or {}
        query = data.get("query", "")
        n_results = data.get("n_results", 10)
        where = data.get("where")

        if not query:
            return jsonify({"error": "Query is required"}), 400

        results = client.search(name, query, n_results=n_results, where=where)
        return jsonify(results), 200
    except Exception as e:
        logger.exception(f"Error searching in {name}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/collections/<name>/documents", methods=["POST"])
def api_add_document(name: str) -> tuple[Any, int]:
    try:
        client = get_client()
        data = request.get_json() or {}
        document = data.get("document")
        metadata = data.get("metadata")
        doc_id = data.get("id")

        if not document:
            return jsonify({"error": "Document content is required"}), 400

        result = client.add_document(name, document, metadata=metadata, doc_id=doc_id)
        return jsonify(result), 201
    except Exception as e:
        logger.exception(f"Error adding document to {name}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/collections/<name>/documents/<doc_id>", methods=["DELETE"])
def api_delete_document(name: str, doc_id: str) -> tuple[Any, int]:
    try:
        client = get_client()
        result = client.delete_document(name, doc_id)
        return jsonify(result), 200
    except Exception as e:
        logger.exception(f"Error deleting document {doc_id} from {name}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/collections", methods=["POST"])
def api_create_collection() -> tuple[Any, int]:
    try:
        client = get_client()
        data = request.get_json() or {}
        name = data.get("name")
        metadata = data.get("metadata")

        if not name:
            return jsonify({"error": "Collection name is required"}), 400

        result = client.create_collection(name, metadata=metadata)
        return jsonify(result), 201
    except Exception as e:
        logger.exception("Error creating collection")
        return jsonify({"error": str(e)}), 500


@app.route("/api/collections/<name>", methods=["DELETE"])
def api_delete_collection(name: str) -> tuple[Any, int]:
    try:
        client = get_client()
        result = client.delete_collection(name)
        return jsonify(result), 200
    except Exception as e:
        logger.exception(f"Error deleting collection {name}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    server_config = config.get("server", {})
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 5000)
    debug = config.get("app", {}).get("debug", False) or os.environ.get(
        "FLASK_DEBUG", ""
    ).lower() in ("1", "true")

    logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
