import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

mongo_client: MongoClient | None = None


def get_users_collection() -> Collection:
    return get_auth_database()["users"]


def get_user_logs_collection() -> Collection:
    return get_auth_database()["user_logs"]


def get_auth_database() -> Database:
    global mongo_client

    mongo_uri = os.environ.get("MONGODB_URI")
    if not mongo_uri:
        raise RuntimeError("MONGODB_URI is not configured.")

    if mongo_client is None:
        mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

    return mongo_client["auth"]
