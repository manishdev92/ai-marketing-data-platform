from __future__ import annotations

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """
    Local-friendly embedding generator.
    We use a lightweight sentence-transformers model (usually 384-d),
    then pad/truncate to 1024 dims to satisfy the assignment requirement.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", target_dim: int = 1024):
        self.model = SentenceTransformer(model_name)
        self.target_dim = target_dim

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        vecs = self.model.encode(texts, normalize_embeddings=True)
        vecs = np.asarray(vecs, dtype=np.float32)

        # Ensure shape: (n, d)
        if vecs.ndim == 1:
            vecs = vecs.reshape(1, -1)

        d = vecs.shape[1]

        if d == self.target_dim:
            out = vecs
        elif d < self.target_dim:
            pad = np.zeros((vecs.shape[0], self.target_dim - d), dtype=np.float32)
            out = np.concatenate([vecs, pad], axis=1)
        else:
            out = vecs[:, : self.target_dim]

        return out.tolist()

    def embed_text(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]
