# import redis
# from src.utils.config import settings

# redis_client = redis.Redis(host=settings.REDIS_HOST, port=6379, decode_responses=True)

# STREAM_NAME = "conversation_stream"

# def publish_event(event: dict):
#     redis_client.xadd(STREAM_NAME, event)

# def create_consumer_group(group_name: str):
#     try:
#         redis_client.xgroup_create(STREAM_NAME, group_name, id="0", mkstream=True)
#     except redis.exceptions.ResponseError:
#         pass  # group already exists

import redis
from src.utils.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis_client():
    return redis_client

# def create_consumer_group(group_name: str):
#     try:
#         # Ensure stream exists by creating a dummy entry
#         redis_client.xadd("conversation_stream", {"init": "true"}, id="*")

#         redis_client.xgroup_create(
#             name="conversation_stream",
#             group=group_name,
#             id="0",
#             mkstream=True
#         )
#     except redis.exceptions.ResponseError as e:
#         if "BUSYGROUP" in str(e):
#             pass  # group already exists
#         else:
#             raise


def create_consumer_group(group_name: str):
    try:
        # Ensure stream exists
        redis_client.xadd("conversation_stream", {"init": "true"})

        # Correct argument order for redis-py
        redis_client.xgroup_create(
            "conversation_stream",   # stream name
            group_name,              # group name
            id="0",
            mkstream=True
        )
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            pass  # Group already exists
        else:
            raise

