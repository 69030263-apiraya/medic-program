import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

if getattr(sys, "frozen", False):
    application_dir = Path(sys.executable).resolve().parent
    config_dirs = (application_dir, application_dir.parent)
else:
    application_dir = Path(__file__).resolve().parents[1]
    config_dirs = (application_dir,)

for config_dir in config_dirs:
    env_file = config_dir / ".env"
    if env_file.is_file():
        load_dotenv(env_file)
        if os.environ.get("MONGODB_URI"):
            break

mongo_client: MongoClient | None = None


def get_users_collection() -> Collection:
    return get_auth_database()["users"]


def get_user_logs_collection() -> Collection:
    return get_auth_database()["user_logs"]


def get_medicine_types_collection() -> Collection:
    return get_medicine_database()["medicine_type"]


def get_medicines_collection() -> Collection:
    return get_medicine_database()["medicines"]


def get_user_medicines_collection() -> Collection:
    return get_database("mymed")["user_medicine"]


def get_auth_database() -> Database:
    return get_database("auth")


def get_medicine_database() -> Database:
    return get_database("medicine")


def get_database(database_name: str) -> Database:
    global mongo_client

    mongo_uri = os.environ.get("MONGODB_URI")
    if not mongo_uri:
        raise RuntimeError("MONGODB_URI is not configured.")

    if mongo_client is None:
        mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

    return mongo_client[database_name]
