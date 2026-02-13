# import time
# import json

# from src.db.milvus import connect_milvus, get_or_create_collection, insert_embeddings

# from src.db.sqlite import initialize_tables
# from src.db.redis_client import create_consumer_group, get_redis_client

# from src.db.neo4j import init_constraints, upsert_conversation_graph
# from src.utils.intent import detect_intent
# from src.db.sqlite import update_user_metrics

# from src.utils.campaign import assign_campaign
# from src.db.neo4j import link_user_to_campaign
# from src.db.sqlite import increment_campaign_engagement


# STREAM_NAME = "conversation_stream"
# GROUP_NAME = "embedding_group"
# CONSUMER_NAME = "worker_1"


# import uuid
# from src.models.embedding_model import EmbeddingModel

# # create once (avoid reloading model repeatedly)
# embedder = EmbeddingModel()

# def process_message(message_data: dict):
#     # Choose what text to embed (simple: concat all messages)
#     texts = [m.get("content", "") for m in message_data.get("messages", [])]
#     full_text = " ".join([t for t in texts if t]).strip()

#     if not full_text:
#         print("Skipping empty text for embedding")
#         return

#     message_id = str(uuid.uuid4())

#     user_id = message_data.get("user_id", "unknown")

#     embedding = embedder.embed_text(full_text)

#     insert_embeddings([
#         {
#             "message_id": message_id,
#             "user_id": user_id,
#             "embedding": embedding
#         }])

#     print(f"✅ Inserted embedding into Milvus message_id={message_id} user_id={user_id}")

#     intent = detect_intent(full_text)

#     upsert_conversation_graph(
#         user_id=user_id,
#         session_id=message_data.get("session_id", "unknown"),
#         message_id=message_id,
#         text=full_text,
#         timestamp=str(message_data.get("timestamp")),
#         intent=intent,
#     )

#     print(f"✅ Upserted graph in Neo4j user_id={user_id} intent={intent}")

#     update_user_metrics(user_id, intent)
#     print(f"✅ Updated analytics for user={user_id} intent={intent}")

#     campaign_id = assign_campaign(intent)

#     link_user_to_campaign(user_id=user_id, campaign_id=campaign_id)
#     increment_campaign_engagement(user_id, campaign_id)
#     print(f"✅ Linked campaign {campaign_id} to user={user_id}")


# if __name__ == "__main__":
#     print("Initializing services...")

#     connect_milvus()
#     get_or_create_collection()
#     initialize_tables()
#     create_consumer_group(GROUP_NAME)
#     init_constraints()
#     redis_client = get_redis_client()

#     print("Pipeline worker running...")

#     while True:
#         try:
#             response = redis_client.xreadgroup(
#                 groupname=GROUP_NAME,
#                 consumername=CONSUMER_NAME,
#                 streams={STREAM_NAME: ">"},
#                 count=1,
#                 block=5000
#             )

#             if response:
#                 for stream, messages in response:
#                     for message_id, message_data in messages:
#                         # ✅ ignore bootstrap/init messages
#                         if "data" in message_data:
#                             data = json.loads(message_data["data"])
#                             process_message(data)
#                         else:
#                             print("Skipping non-data message:", message_data)

#                         # ✅ always acknowledge so it doesn't stay pending
#                         redis_client.xack(STREAM_NAME, GROUP_NAME, message_id)


#         except Exception as e:
#             print("Worker error:", e)
#             time.sleep(5)

import time
import json

from src.db.milvus import connect_milvus, get_or_create_collection
from src.db.sqlite import initialize_tables
from src.db.redis_client import create_consumer_group, get_redis_client
from src.db.neo4j import init_constraints

from src.pipeline.tasks.embedding_consumer import handle_embedding
from src.pipeline.tasks.graph_consumer import handle_graph_and_analytics

from src.utils.validators import validate_conversation
from src.utils.logger import get_logger
from src.utils.metrics import incr

STREAM_NAME = "conversation_stream"
GROUP_NAME = "embedding_group"
CONSUMER_NAME = "worker_1"

log = get_logger("worker")


if __name__ == "__main__":
    log.info("Initializing services...")

    connect_milvus()
    get_or_create_collection()

    initialize_tables()
    create_consumer_group(GROUP_NAME)
    init_constraints()

    redis_client = get_redis_client()
    log.info("Pipeline worker running...")

    while True:
        try:
            response = redis_client.xreadgroup(
                groupname=GROUP_NAME,
                consumername=CONSUMER_NAME,
                streams={STREAM_NAME: ">"},
                count=1,
                block=5000,
            )

            if not response:
                continue

            for stream, messages in response:
                for message_id, message_data in messages:
                    try:
                        # Ignore bootstrap/init messages
                        if "data" not in message_data:
                            log.info(f"Skipping non-data message: {message_data}")
                            redis_client.xack(STREAM_NAME, GROUP_NAME, message_id)
                            continue

                        data = json.loads(message_data["data"])
                        validate_conversation(data)

                        # 1) Embed + insert into Milvus
                        emb = handle_embedding(data)
                        if emb.get("skipped"):
                            redis_client.xack(STREAM_NAME, GROUP_NAME, message_id)
                            continue

                        # 2) Graph + analytics + campaign
                        handle_graph_and_analytics(
                            message_data=data,
                            message_id=emb["message_id"],
                            text=emb["text"],
                        )

                        redis_client.xack(STREAM_NAME, GROUP_NAME, message_id)
                        incr("worker.acked")

                    except Exception as e:
                        # IMPORTANT: ack anyway to prevent infinite pending loop
                        log.error(f"Message failed id={message_id} err={e}")
                        redis_client.xack(STREAM_NAME, GROUP_NAME, message_id)
                        incr("worker.failed")

        except Exception as e:
            log.error(f"Worker loop error: {e}")
            time.sleep(5)
