from pymongo import MongoClient
import redis

from main import app

mongo = MongoClient(host=app.config['MONGO_DB_HOST'], port=int(app.config['MONGO_DB_HOST']))
redis = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])