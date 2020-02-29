from flask import Flask
from flask_restful import Api
import redis
from pymongo import MongoClient

from api.resources.auth import Login, Logout
from api.resources.event import EventList, Event
from api.resources.user import UserList, User

def create_app():
    app = Flask(__name__)

    app.config.from_pyfile(f"config/{app.config['ENV']}.cfg")

    app.redis = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])
    app.mongo = MongoClient(host=app.config['MONGO_DB_HOST'], port=int(app.config['MONGO_DB_PORT']))

    api = Api(app)

    api.add_resource(EventList, '/api/v1/events')
    api.add_resource(Event, '/api/v1/events/<string:id>')
    api.add_resource(UserList, '/api/v1/users')
    api.add_resource(User, '/api/v1/users/<string:id>')
    api.add_resource(Login, '/api/v1/auth/login')
    api.add_resource(Logout, '/api/v1/auth/logout')

    return app
