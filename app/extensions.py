import os
from flask_pymongo import MongoClient

if 'MONGO_DB_HOST' not in os.environ or 'MONGO_DB_PORT' not in os.environ:
    raise Exception('MONGO_DB_HOST and MONGO_DB_PORT environment variables musst be set')

mongo_client = MongoClient(os.getenv('MONGO_DB_HOST'), int(os.getenv('MONGO_DB_PORT')))