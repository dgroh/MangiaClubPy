import unittest
from unittest import mock

import os
import mongomock

from api import create_app
from config import DevelopmentConfig, ProductionConfig, TestingConfig
from unittest.mock import NonCallableMock


class TestConfigMethods(unittest.TestCase):
    def test_create_app_config_is_production(self):
        # Arrange
        os.environ['FLASK_ENV'] = 'production'
        
        # Act
        app = create_app()

        # Assert
        self.__assert_attributes(ProductionConfig, app.config)

    def test_create_app_config_is_development(self):
        # Arrange
        os.environ['FLASK_ENV'] = 'development'
                
        # Act
        app = create_app()

        # Assert
        self.__assert_attributes(DevelopmentConfig, app.config)

    def test_create_app_config_is_testing(self):
        # Arrange
        os.environ['FLASK_ENV'] = 'testing'
        
        # Act
        app = create_app()

        # Assert
        self.assertIsInstance(app.mongo, type(mongomock.MongoClient()))
        self.assertTrue(issubclass(type(app.redis), mock.Mock))
        self.__assert_attributes(TestingConfig, app.config)

    def __assert_attributes(self, env_config, app_config):
        env_config_attrs = set(sorted(env_config.__dict__.items())[:-2])
        app_config_attrs = set(dict(app_config).items())

        self.assertTrue(env_config_attrs.issubset(app_config_attrs))


if __name__ == '__main__':
    unittest.main()
