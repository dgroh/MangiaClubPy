from flask import Flask
from api.resources import init_resources

from config import ProductionConfig, TestingConfig, DevelopmentConfig


def create_app():
    app = Flask(__name__)

    init_resources(app)
    
    config = ProductionConfig

    if app.config['ENV'] is 'development':
        config = DevelopmentConfig
    elif app.config['ENV'] is 'testing':
        config = TestingConfig

    app.config.from_object(config)

    # TODO: This code smells. Consider moving this responsability to the config object.    
    if app.config['ENV'] == 'testing':
        from api.db import init_db_mock
        init_db_mock(app)
    else:
        from api.db import init_db
        init_db(app)

    return app
