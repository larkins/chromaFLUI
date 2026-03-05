#!/usr/bin/env python
import logging
import os
import re
from typing import Any
import uuid

import chromadb
import yaml
from chromadb.config import Settings

logger = logging.getLogger(__name__)


def load_config() -> dict[str, Any]:
    config_path = os.environ.get("CONFIG_PATH", "config.yaml")
    with open(config_path) as f:
        content = f.read()

    def replace_env_vars(text: str) -> str:
        pattern = r"\$\{([^}]+)\}"

        def replacer(match: re.Match[str]) -> str:
            var_name = match.group(1)
            return os.environ.get(var_name, "")

        return re.sub(pattern, replacer, text)

    content = replace_env_vars(content)
    return yaml.safe_load(content)


class ChromaClient:
    def __init__(self) -> None:
        self.config = load_config()
        chroma_config = self.config.get("chromadb", {})
        path = chroma_config.get("path", "./storage/chroma/mem0")

        self.client = chromadb.PersistentClient(
            path=path,
            settings=Settings(anonymized_telemetry=False),
        )
        self.tenant = chroma_config.get("tenant", "default_tenant")
        self.database = chroma_config.get("database", "default_database")
        logger.info(f"ChromaDB client initialized at path: {path}")

    def list_collections(self) -> list[dict[str, Any]]:
        collections = self.client.list_collections()
        result = []
        for col in collections:
            result.append(
                {
                    "name": col.name,
                    "id": str(col.id),
                    "count": col.count(),
                    "metadata": col.metadata or {},
                }
            )
        return result

    def get_collection(self, name: str) -> dict[str, Any] | None:
        try:
            col = self.client.get_collection(name=name)
            return {
                "name": col.name,
                "id": str(col.id),
                "count": col.count(),
                "metadata": col.metadata or {},
            }
        except Exception as e:
            logger.error(f"Error getting collection {name}: {e}")
            return None

    def get_documents(
        self,
        collection_name: str,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        col = self.client.get_collection(name=collection_name)
        total = col.count()

        result = col.get(
            limit=limit,
            offset=offset,
            include=["documents", "metadatas"],
        )

        documents = []
        ids = result.get("ids") or []
        docs = result.get("documents") or []
        metadatas = result.get("metadatas") or []
        embeddings = result.get("embeddings")
        if embeddings is None:
            embeddings = []

        for idx, doc_id in enumerate(ids):
            doc_data: dict[str, Any] = {
                "id": doc_id,
                "document": docs[idx] if docs and idx < len(docs) else None,
                "metadata": (
                    metadatas[idx] if metadatas and idx < len(metadatas) else {}
                ),
            }
            if len(embeddings) > 0 and idx < len(embeddings):
                doc_data["has_embedding"] = True
            documents.append(doc_data)

        return {
            "documents": documents,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 10,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        col = self.client.get_collection(name=collection_name)
        result = col.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        documents = []
        ids_list = result.get("ids") or [[]]
        docs_list = result.get("documents") or [[]]
        metadatas_list = result.get("metadatas") or [[]]
        distances_list = result.get("distances") or [[]]

        ids = ids_list[0] if ids_list else []
        docs = docs_list[0] if docs_list else []
        metadatas = metadatas_list[0] if metadatas_list else []
        distances = distances_list[0] if distances_list else []

        for idx, doc_id in enumerate(ids):
            documents.append(
                {
                    "id": doc_id,
                    "document": docs[idx] if docs and idx < len(docs) else None,
                    "metadata": (
                        metadatas[idx] if metadatas and idx < len(metadatas) else {}
                    ),
                    "distance": (
                        distances[idx] if distances and idx < len(distances) else None
                    ),
                }
            )

        return documents

    def add_document(
        self,
        collection_name: str,
        document: str,
        metadata: dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> dict[str, Any]:
        col = self.client.get_collection(name=collection_name)
        final_id = doc_id or str(uuid.uuid4())
        col.add(
            documents=[document],
            metadatas=[metadata] if metadata else None,
            ids=[final_id],
        )
        return {"status": "success", "id": final_id, "document": document}

    def delete_document(self, collection_name: str, doc_id: str) -> dict[str, Any]:
        col = self.client.get_collection(name=collection_name)
        col.delete(ids=[doc_id])
        return {"status": "success", "deleted_id": doc_id}

    def create_collection(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        col = self.client.create_collection(name=name, metadata=metadata)
        return {
            "name": col.name,
            "id": str(col.id),
            "metadata": col.metadata or {},
        }

    def delete_collection(self, name: str) -> dict[str, Any]:
        self.client.delete_collection(name=name)
        return {"status": "success", "deleted_collection": name}
