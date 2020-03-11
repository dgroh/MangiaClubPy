# -*- coding: utf-8 -*-
""" DB module where database related instances occurs.

This module is responsible for holding methods that create instances of database stores.
"""

def init_db(app):
    """__This function initializes db instances for MongoDb and Redis.__
    
    The instances created here are stored in the app instance, 
    which can be used throughout the application
    
    __Example:__
    
    ```
    from flask import current_app as app

    app.mongo.db.users.find({})
    app.redis.setex(...)
    ```

    __Parameters:__

    app (app): The app instance
    """

    import redis
    from pymongo import MongoClient
    
    app.redis = redis.Redis(host=app.config.REDIS_HOST, port=app.config.REDIS_PORT)
    app.mongo = MongoClient(host=app.config.MONGO_DB_HOST, port=int(app.config.MONGO_DB_PORT))


def init_db_mock(app):
    """This function initializes mock instances for MongoDb and Redis.
    
    The mock instances created here are stored in the app instance, 
    which can be used throughout the tests.
    
    __Example:__

    ```
    from api import create_app

    app = create_app()
    app.mongo.db.users.find({})
    app.redis.setex(...)
    ```

    __Parameters:__

    app (app): The app instance
    """

    import mongomock
    from unittest import mock

    app.redis = mock.Mock()
    app.mongo = mongomock.MongoClient()
