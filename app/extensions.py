import os
from flask_pymongo import MongoClient

mongo_client = MongoClient(host=os.getenv("MONGO_DB_HOST"))