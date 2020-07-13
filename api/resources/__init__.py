# -*- coding: utf-8 -*-
""" Resources module where the API routes are registered.
"""

from flask_restful import Api

from api.resources.auth import Login, Logout
from api.resources.events import EventList, Event
from api.resources.users import UserList, User
from api.resources.constants import Routes


def init_resources(app):
    """This function initializes the resources with the corresponding routes.
    """

    api = Api(app)

    api.add_resource(EventList, Routes.EVENTS_V1)
    api.add_resource(Event, f'{Routes.EVENTS_V1}/<string:id>')
    api.add_resource(UserList, Routes.USERS_V1)
    api.add_resource(User, f'{Routes.USERS_V1}/<string:id>')
    api.add_resource(Login, Routes.LOGIN_V1)
    api.add_resource(Logout, Routes.LOGOUT_V1)