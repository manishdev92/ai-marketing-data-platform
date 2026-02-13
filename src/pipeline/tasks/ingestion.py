import json
import copy
from fastapi.encoders import jsonable_encoder
from src.db.mongodb import get_mongo_collection
from src.db.redis_client import get_redis_client
from src.pipeline.lineage import track_event

STREAM_NAME = "conversation_stream"

def ingest_conversation(conversation: dict):

    # 1️⃣ Make JSON-safe version
    conversation_json = jsonable_encoder(conversation)

    # 2️⃣ Insert a COPY into Mongo (so mutation doesn't affect Redis copy)
    collection = get_mongo_collection("conversations")
    mongo_data = copy.deepcopy(conversation_json)
    result = collection.insert_one(mongo_data)

    # 3️⃣ Publish ORIGINAL json-safe data (without _id)
    redis_client = get_redis_client()
    redis_client.xadd(
    STREAM_NAME,
    {"data": json.dumps(conversation_json, default=str)}
)


    # 4️⃣ Track lineage
    track_event(
        event_type="conversation_ingested",
        metadata={
            "mongo_id": str(result.inserted_id),
            "stream": STREAM_NAME
        }
    )

    return {
        "status": "ingested",
        "mongo_id": str(result.inserted_id)
    }
