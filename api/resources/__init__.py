from flask_restful import Api

from .auth import Login, Logout
from .event import EventList, Event
from .user import UserList, User


def init_resources(app):
    api = Api(app)

    api.add_resource(EventList, '/api/v1/events')
    api.add_resource(Event, '/api/v1/events/<string:id>')
    api.add_resource(UserList, '/api/v1/users')
    api.add_resource(User, '/api/v1/users/<string:id>')
    api.add_resource(Login, '/api/v1/auth/login')
    api.add_resource(Logout, '/api/v1/auth/logout')