import os
from flask_pymongo import MongoClient

db = MongoClient(host=os.getenv("MONGO_DB_HOST"))