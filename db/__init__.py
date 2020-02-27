import os
import redis
from flask_pymongo import MongoClient

if 'MONGO_DB_HOST' not in os.environ or 'MONGO_DB_PORT' not in os.environ:
    raise Exception('MONGO_DB_HOST and MONGO_DB_PORT environment variables musst be set')

mongo = MongoClient(host=os.getenv('MONGO_DB_HOST'), port=int(os.getenv('MONGO_DB_PORT')))
redis = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'))