import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "appdb")
APP_ID = os.getenv("APP_ID")

_client = MongoClient(MONGO_URI)
_db = _client[MONGO_DB]

def get_app_config():
    config = _db["config"].find_one({"_id": APP_ID})
    if not config:
        raise RuntimeError(f"No config found for APP_ID :: {APP_ID}")
    
    return config


def get_db():
    global _client, _db

    if _db is None:
        if not MONGO_URI:
            raise RuntimeError("MONGO_URI not set in environment")

        if not MONGO_DB:
            raise RuntimeError("MONGO_DB not set in environment")

        _client = MongoClient(
            MONGO_URI,
            maxPoolSize=50,
            minPoolSize=5,
            serverSelectionTimeoutMS=5000
        )

        _db = _client[MONGO_DB]

    return _db




def close_db():
    _client.close()
