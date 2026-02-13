from typing import Any, Dict, List


def validate_conversation(payload: Dict[str, Any]) -> None:
    """
    Raises ValueError if payload is invalid.
    Keep it strict enough to avoid garbage entering embeddings/graph.
    """
    if not isinstance(payload, dict):
        raise ValueError("conversation payload must be a dict")

    user_id = payload.get("user_id")
    session_id = payload.get("session_id")
    messages = payload.get("messages")

    if not user_id or not isinstance(user_id, str):
        raise ValueError("user_id must be a non-empty string")

    if not session_id or not isinstance(session_id, str):
        raise ValueError("session_id must be a non-empty string")

    if not isinstance(messages, list) or len(messages) == 0:
        raise ValueError("messages must be a non-empty list")

    for i, m in enumerate(messages):
        if not isinstance(m, dict):
            raise ValueError(f"messages[{i}] must be an object")
        role = m.get("role")
        content = m.get("content")
        if role not in ("user", "assistant", "system"):
            raise ValueError(f"messages[{i}].role must be user|assistant|system")
        if not content or not isinstance(content, str) or not content.strip():
            raise ValueError(f"messages[{i}].content must be a non-empty string")
