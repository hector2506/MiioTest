from pathlib import Path
import environ
import os
from pymongo import MongoClient


BASE_DIR = Path(__file__).resolve().parent.parent
env_file = os.path.join(BASE_DIR, ".env")
environ.Env.read_env(env_file)
env = os.environ


def get_db_handle(db_name):
    client = MongoClient(env.get("MONGO_DB_PORT"))
    db_handle = client[db_name]
    return db_handle, client


def get_collection_handle(db_handle, collection_name):
    return db_handle[collection_name]