from fastapi import APIRouter, HTTPException
from src.api.schemas import ConversationCreate
from src.pipeline.tasks.ingestion import ingest_conversation

from src.db.milvus import connect_milvus, fetch_latest_embedding_for_user, search_similar_users
from src.db.neo4j import get_campaigns_for_users
from src.db.sqlite import get_campaign_scores

router = APIRouter()

@router.post("/conversations")
def create_conversation(conversation: ConversationCreate):
    return ingest_conversation(conversation.dict())

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/recommendations/{user_id}")
def recommendations(user_id: str):
    connect_milvus()

    emb = fetch_latest_embedding_for_user(user_id)
    if emb is None:
        raise HTTPException(status_code=404, detail=f"No embedding found for user_id={user_id}")

    similar_users = search_similar_users(emb, top_k=5)

    # remove self if returned
    similar_users = [u for u in similar_users if u != user_id]

    campaign_edges = get_campaigns_for_users(similar_users)
    campaign_ids = list({row["campaign_id"] for row in campaign_edges})

    scores = get_campaign_scores(campaign_ids)

    ranked = sorted(
        [{"campaign_id": cid, "score": scores.get(cid, 0)} for cid in campaign_ids],
        key=lambda x: x["score"],
        reverse=True
    )

    return {
        "user_id": user_id,
        "similar_users": similar_users,
        "recommendations": ranked[:5]
    }
