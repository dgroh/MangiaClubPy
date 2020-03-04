from flask import Flask
import redis
from pymongo import MongoClient

from .api import init_app


def create_app():
    app = Flask(__name__)

    app.config.from_pyfile(f"config/{app.config['ENV']}.cfg")

    app.redis = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])
    app.mongo = MongoClient(host=app.config['MONGO_DB_HOST'], port=int(app.config['MONGO_DB_PORT']))

    init_app(app)

    return app
