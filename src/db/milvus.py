from __future__ import annotations

from typing import List, Dict, Any
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from src.utils.config import settings

COLLECTION_NAME = "user_embeddings"


def connect_milvus():
    connections.connect(
        alias="default",
        host=settings.MILVUS_HOST,
        port=settings.MILVUS_PORT,
    )


def list_collections():
    return utility.list_collections()


def get_or_create_collection() -> Collection:
    fields = [
        FieldSchema(name="message_id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
        FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
    ]
    schema = CollectionSchema(fields, description="User Embeddings")

    if COLLECTION_NAME not in list_collections():
        collection = Collection(name=COLLECTION_NAME, schema=schema)

        # HNSW index (good for local)
        index_params = {
            "metric_type": "L2",
            "index_type": "HNSW",
            "params": {"M": 16, "efConstruction": 200},
        }
        collection.create_index(field_name="embedding", index_params=index_params)
    else:
        collection = Collection(COLLECTION_NAME)

    # Make sure it's loaded for search
    collection.load()
    return collection


def insert_embeddings(rows: List[Dict[str, Any]]):
    """
    rows: [{message_id, user_id, embedding}, ...]
    """
    collection = get_or_create_collection()

    message_ids = [r["message_id"] for r in rows]
    user_ids = [r["user_id"] for r in rows]
    embeddings = [r["embedding"] for r in rows]

    collection.insert([message_ids, user_ids, embeddings])
    collection.flush()


def count_embeddings() -> int:
    collection = get_or_create_collection()
    return collection.num_entities

def get_collection():
    return Collection(COLLECTION_NAME)

def fetch_latest_embedding_for_user(user_id: str):
    collection = get_collection()
    collection.load()

    # Milvus doesn't guarantee "latest" without a timestamp field.
    # For prototype: fetch any one embedding for this user.
    expr = f'user_id == "{user_id}"'
    res = collection.query(expr=expr, output_fields=["message_id", "user_id", "embedding"], limit=1)

    if not res:
        return None
    return res[0]["embedding"]

def search_similar_users(query_embedding, top_k: int = 5):
    collection = get_collection()
    collection.load()

    search_params = {"metric_type": "L2", "params": {"ef": 64}}
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["user_id"],
    )

    user_ids = []
    for hit in results[0]:
        uid = hit.entity.get("user_id")
        if uid:
            user_ids.append(uid)

    # de-dup preserve order
    seen = set()
    out = []
    for u in user_ids:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out
