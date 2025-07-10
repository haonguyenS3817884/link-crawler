from pymongo import InsertOne, errors
from database import db_manager
from config.constants import WAITING_URLS_COLLECTION
from .models import CreateWaitingUrl

waiting_urls_collection = db_manager.db[WAITING_URLS_COLLECTION]

async def insert_url(payload: CreateWaitingUrl):
    try:
        payload_dict = payload.model_dump()
        await waiting_urls_collection.insert_one(payload_dict)
        print(f"{payload.url} is inserted")
    except errors.DuplicateKeyError as e:
        print(f"Failed to insert duplicate url: {e}")
    except Exception as e:
        print(f"Failed to insert url: {e}")

async def insert_urls(payloads: list[CreateWaitingUrl]):
    payload_insert_operations = [InsertOne(payload.model_dump()) for payload in payloads]
    return await waiting_urls_collection.bulk_write(payload_insert_operations, ordered=False)