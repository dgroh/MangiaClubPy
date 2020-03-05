from flask import Flask

from config import ProductionConfig, TestingConfig, DevelopmentConfig

def create_app():
    app = Flask(__name__)

    config = ProductionConfig

    if app.config['ENV'] is 'development':
        config = DevelopmentConfig
    if app.config['ENV'] is 'testing':
        config = TestingConfig

    app.config.from_object(config)

    if not isinstance(config, type(TestingConfig)):
        from api.resources import init_resources
        from api.db import init_db

        init_db(app)
        init_resources(app)
    else:
        from api.db import init_db_mock
        init_db_mock(app)

    return app
