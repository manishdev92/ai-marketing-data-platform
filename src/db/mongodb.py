# from pymongo import MongoClient
# from src.utils.config import settings

# client = MongoClient(settings.MONGO_URI)
# db = client["marketing_platform"]

# conversations_collection = db["conversations"]

# def insert_conversation(data: dict):
#     return conversations_collection.insert_one(data)

from pymongo import MongoClient
from src.utils.config import settings

client = MongoClient(settings.MONGO_URI)
db = client["marketing_db"]

def get_mongo_collection(name: str):
    return db[name]
