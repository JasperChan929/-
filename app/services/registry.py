import json
import os
from typing import List, Dict, Any

from app.core.config import settings


def ensure_registry():
    os.makedirs(settings.REGISTRY_DIR, exist_ok=True)
    if not os.path.exists(settings.REGISTRY_FILE):
        with open(settings.REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def read_registry() -> List[Dict[str, Any]]:
    ensure_registry()
    with open(settings.REGISTRY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def write_registry(data: List[Dict[str, Any]]) -> None:
    ensure_registry()
    with open(settings.REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_document_record(record: Dict[str, Any]) -> None:
    data = read_registry()
    data.append(record)
    write_registry(data)


def list_documents() -> List[Dict[str, Any]]:
    return read_registry()


def get_document_record(doc_id: str):
    data = read_registry()
    for item in data:
        if item["doc_id"] == doc_id:
            return item
    return None


def delete_document_record(doc_id: str) -> bool:
    data = read_registry()
    new_data = [item for item in data if item["doc_id"] != doc_id]
    deleted = len(new_data) != len(data)
    if deleted:
        write_registry(new_data)
    return deleted


def reset_registry():
    write_registry([])