from pymongo import AsyncMongoClient
from config.general_config import env_config
from config.constants import DATABASE_URI, DATABASE_NAME

class DBManager:
    def __init__(self, uri: str, database_name: str):
        self.client = AsyncMongoClient(uri)
        self.db = self.client[database_name]

db_manager = DBManager(uri=env_config[DATABASE_URI], database_name=env_config[DATABASE_NAME])