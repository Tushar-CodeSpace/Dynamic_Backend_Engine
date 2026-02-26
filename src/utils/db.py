from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class _MongoService:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI")
        self.mongo_db = os.getenv("MONGO_DB", "appdb")
        self.app_id = os.getenv("APP_ID")

        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def get_app_config(self):
        config = self.db["config"].find_one({"_id": self.app_id})
        if not config:
            raise RuntimeError(f"No config found for APP_ID: {self.app_id}")
        return config

    def close(self):
        self.client.close()


mongo = _MongoService()