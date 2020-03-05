class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = ''
    MONGO_DB_HOST = ''
    MONGO_DB_PORT = ''
    REDIS_HOST = ''
    REDIS_PORT = ''


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SECRET_KEY = '15f15fe69236803afdfe9f9109622a09048b9d8e53dc98142ab8e858175c1681'
    MONGO_DB_HOST = "localhost"
    MONGO_DB_PORT = "27017"
    REDIS_HOST = "localhost"
    REDIS_PORT = "6379"


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    SECRET_KEY = ''
    MONGO_DB_HOST = ''
    MONGO_DB_PORT = ''
    REDIS_HOST = ''
    REDIS_PORT = ''
