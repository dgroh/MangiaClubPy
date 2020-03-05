def init_db(app):
    import redis
    from pymongo import MongoClient
    
    app.redis = redis.Redis(host=app.config.REDIS_HOST, port=app.config.REDIS_PORT)
    app.mongo = MongoClient(host=app.config.MONGO_DB_HOST, port=int(app.config.MONGO_DB_PORT))


def init_db_mock(app):
    import mongomock
    from unittest import mock

    app.redis = mock.Mock()
    app.mongo = mongomock.MongoClient()
