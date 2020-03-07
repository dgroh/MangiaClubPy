from flask_restful import Api

from api.resources.auth import Login, Logout
from api.resources.event import EventList, Event
from api.resources.user import UserList, User
from api.resources.constants import Routes


def init_resources(app):
    api = Api(app)

    api.add_resource(EventList, Routes.GET_ALL_EVENTS_V1)
    api.add_resource(Event, Routes.GET_EVENT_BY_ID_V1)
    api.add_resource(UserList, Routes.GET_ALL_USERS_V1)
    api.add_resource(User, Routes.GET_USER_BY_ID_V1)
    api.add_resource(Login, Routes.LOGIN_V1)
    api.add_resource(Logout, Routes.LOGOUT_V1)