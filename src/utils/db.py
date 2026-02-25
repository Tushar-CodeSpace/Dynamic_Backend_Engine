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


def close_db():
    _client.close()
