from flask_restful import Api

from api.resources.auth import Login, Logout
from api.resources.event import EventList, Event
from api.resources.user import UserList, User
from api.resources.constants import Routes


def init_resources(app):
    api = Api(app)

    api.add_resource(EventList, Routes.EVENTS_V1)
    api.add_resource(Event, f'{Routes.EVENTS_V1}/<string:id>')
    api.add_resource(UserList, Routes.USERS_V1)
    api.add_resource(User, f'{Routes.USERS_V1}/<string:id>')
    api.add_resource(Login, Routes.LOGIN_V1)
    api.add_resource(Logout, Routes.LOGOUT_V1)