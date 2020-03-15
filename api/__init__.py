# -*- coding: utf-8 -*-
""" API module where app creation occurs.
"""

from flask import Flask
from api.resources import init_resources

from config import ProductionConfig, TestingConfig, DevelopmentConfig


def create_app():
    """This function initializes the app.
    
    The app will be as a [Flask](https://palletsprojects.com/p/flask/) app initialized.
    
    In addition all the api routes and databases will be initialized here.

    The list of routes and the initialization method for them can be found here: `api.resources`

    The database initialization methods can be found here: `api.db`
    """

    app = Flask(__name__)

    init_resources(app)
    
    config = ProductionConfig

    if app.config['ENV'] == 'development':
        config = DevelopmentConfig
    elif app.config['ENV'] == 'testing':
        config = TestingConfig

    app.config.from_object(config)

    if app.config['ENV'] == 'testing':
        from api.db import init_db_mock
        init_db_mock(app)
    else:
        from api.db import init_db
        init_db(app)

    return app
