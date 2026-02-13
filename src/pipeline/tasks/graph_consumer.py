# from typing import Any, Dict

# from src.db.neo4j import upsert_conversation_graph
# from src.db.sqlite import update_user_metrics, increment_campaign_engagement
# from src.utils.intent import detect_intent
# from src.utils.logger import get_logger
# from src.utils.metrics import incr, timer

# log = get_logger("graph_consumer")

from typing import Any, Dict

from src.db.neo4j import upsert_conversation_graph, link_user_to_campaign
from src.db.sqlite import update_user_metrics, increment_campaign_engagement
from src.utils.intent import detect_intent
from src.utils.campaign import assign_campaign

from src.utils.logger import get_logger
from src.utils.metrics import incr, timer

log = get_logger("graph_consumer")

def handle_graph_and_analytics(message_data: Dict[str, Any], message_id: str, text: str) -> Dict[str, Any]:
    user_id = message_data.get("user_id", "unknown")
    session_id = message_data.get("session_id", "unknown")
    timestamp = str(message_data.get("timestamp"))

    intent = detect_intent(text)

    with timer("neo4j.upsert", tags={"user_id": user_id, "intent": intent}):
        upsert_conversation_graph(
            user_id=user_id,
            session_id=session_id,
            message_id=message_id,
            text=text,
            timestamp=timestamp,
            intent=intent,
        )

    with timer("sqlite.update_metrics", tags={"user_id": user_id, "intent": intent}):
        update_user_metrics(user_id, intent)

    campaign_id = assign_campaign(intent)

    with timer("campaign.link", tags={"user_id": user_id, "campaign_id": campaign_id}):
        link_user_to_campaign(user_id=user_id, campaign_id=campaign_id)
        increment_campaign_engagement(user_id, campaign_id)

    incr("graph.upserted", tags={"user_id": user_id, "intent": intent})
    log.info(f"Upserted graph + analytics + campaign user_id={user_id} intent={intent} campaign={campaign_id}")

    return {"user_id": user_id, "intent": intent, "campaign_id": campaign_id}

# def handle_graph_and_analytics(message_data: Dict[str, Any], message_id: str, text: str) -> Dict[str, Any]:
#     """
#     - Detect intent
#     - Upsert graph in Neo4j
#     - Update SQLite analytics tables
#     - Increment engagement_metrics for a demo campaign
#     """
#     user_id = message_data.get("user_id", "unknown")
#     session_id = message_data.get("session_id", "unknown")
#     timestamp = str(message_data.get("timestamp"))

#     intent = detect_intent(text)

#     with timer("neo4j.upsert", tags={"user_id": user_id, "intent": intent}):
#         upsert_conversation_graph(
#             user_id=user_id,
#             session_id=session_id,
#             message_id=message_id,
#             text=text,
#             timestamp=timestamp,
#             intent=intent,
#         )

#     with timer("sqlite.update_metrics", tags={"user_id": user_id, "intent": intent}):
#         update_user_metrics(user_id=user_id, intent=intent)

#     # Demo engagement: always increment a default campaign (replace later with real logic)
#     with timer("sqlite.engagement_increment", tags={"user_id": user_id}):
#         increment_campaign_engagement(user_id=user_id, campaign_id="campaign_reco_1")

#     incr("graph.upserted", tags={"user_id": user_id, "intent": intent})
#     log.info(f"Upserted graph + metrics user_id={user_id} intent={intent}")

#     return {"user_id": user_id, "intent": intent}
