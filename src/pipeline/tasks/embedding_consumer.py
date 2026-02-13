import uuid
from typing import Any, Dict, Optional

from src.models.embedding_model import EmbeddingModel
from src.db.milvus import insert_embeddings
from src.utils.logger import get_logger
from src.utils.metrics import incr, timer

log = get_logger("embedding_consumer")

# load once
_embedder: Optional[EmbeddingModel] = None


def _get_embedder() -> EmbeddingModel:
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingModel()
    return _embedder


def build_text(message_data: Dict[str, Any]) -> str:
    texts = [m.get("content", "") for m in message_data.get("messages", [])]
    full_text = " ".join([t for t in texts if isinstance(t, str) and t.strip()]).strip()
    return full_text


def handle_embedding(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns:
      {
        "message_id": "...",
        "user_id": "...",
        "text": "...",
        "embedding": [...]
      }
    """
    user_id = message_data.get("user_id", "unknown")
    full_text = build_text(message_data)

    if not full_text:
        incr("embedding.skipped_empty_text", tags={"user_id": user_id})
        log.warning("Skipping empty text for embedding")
        return {"skipped": True, "reason": "empty_text", "user_id": user_id}

    message_id = str(uuid.uuid4())
    embedder = _get_embedder()

    with timer("embedding.generate", tags={"user_id": user_id}):
        embedding = embedder.embed_text(full_text)

    with timer("milvus.insert", tags={"user_id": user_id}):
        insert_embeddings([{
            "message_id": message_id,
            "user_id": user_id,
            "embedding": embedding
        }])

    incr("embedding.inserted", tags={"user_id": user_id})
    log.info(f"Inserted embedding message_id={message_id} user_id={user_id}")

    return {
        "message_id": message_id,
        "user_id": user_id,
        "text": full_text,
        "embedding": embedding,
        "skipped": False
    }
