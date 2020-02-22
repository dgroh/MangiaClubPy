import os
from flask_pymongo import MongoClient

mongo_db_host = os.getenv("MONGO_DB_HOST")
mongo_db_port = os.getenv("MONGO_DB_PORT")

mongo_client = MongoClient(mongo_db_host, int(mongo_db_port))