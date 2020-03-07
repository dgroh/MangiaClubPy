import unittest
from unittest import mock

from flask import jsonify

from datetime import datetime, timedelta
from bson import ObjectId
import bcrypt
import jwt

from api import create_app
from api.resources.user import User
from api.resources.constants import HttpStatusCode, Routes

from tests.utils import CustomAssertions, create_token, create_user 


class TestUserMethods(unittest.TestCase, CustomAssertions):
    def setUp(self):
        self.app = create_app()

        create_user(self.app)

        self.user = User()

    def tearDown(self):
        pass

    def test_get_user_invalid_id(self):
        with self.app.test_client() as client:
            # Act
            response = client.get(f'{Routes.USERS_V1}/-1')
            
            # Assert
            self.assert_response(response, b'[HTTP_400_BAD_REQUEST]', HttpStatusCode.HTTP_400_BAD_REQUEST)

    def test_get_user_not_found(self):
        with self.app.test_client() as client:
            # Arrange
            random_id = str(ObjectId())

            # Act
            response = client.get(f'{Routes.USERS_V1}/{random_id}')
            
            # Assert
            self.assert_response(response, b'[HTTP_404_NOT_FOUND]', HttpStatusCode.HTTP_404_NOT_FOUND)

    def test_get_user_successful(self):
        with self.app.test_client() as client:
            # Arrange
            expected_user = self.app.mongo.db.users.find_one({ 'email': 'foo@foo.com' })
            expected_user['_id'] = str(expected_user['_id'])
            expected_user['hashed_password'] = expected_user['hashed_password'].decode('utf-8')
            expected_user['password_salt'] = expected_user['password_salt'].decode('utf-8')

            # Act
            response = client.get(f'{Routes.USERS_V1}/{expected_user["_id"]}')

            # Assert
            self.assert_response(response, jsonify({'data': expected_user}).data, HttpStatusCode.HTTP_200_OK)

    def test_put_user_without_token(self):
        with self.app.test_client() as client:
            # Arrange
            user = self.app.mongo.db.users.find_one({ 'email': 'foo@foo.com' })

            # Act
            response = client.put(f'{Routes.USERS_V1}/{str(user["_id"])}')
            
            # Assert
            self.assert_response(response, b'[HTTP_403_FORBIDDEN]', HttpStatusCode.HTTP_403_FORBIDDEN)

    def test_put_user_not_found(self):
        with self.app.test_client() as client:
            # Arrange
            random_id = str(ObjectId())

            user = { '_id': random_id, 'email': 'foo@foo.com', 'phone': '+4915162961189' }

            token = create_token(user, 60, self.app.config['SECRET_KEY'])

            self.app.redis.get.return_value = token

            # Act
            response = client.put(f'{Routes.USERS_V1}/{random_id}', headers={ 'Access-Token': token })
            
            # Assert
            self.assert_response(response, b'[INVALID_TOKEN]', HttpStatusCode.HTTP_400_BAD_REQUEST)

    def test_put_user_token_expired(self):
        with self.app.test_client() as client:
            # Arrange
            user = self.app.mongo.db.users.find_one({ 'email': 'foo@foo.com' })

            user_id = str(user['_id'])

            token = create_token(user, -1, self.app.config['SECRET_KEY'])

            self.app.redis.get.return_value = token

            # Act
            response = client.put(f'{Routes.USERS_V1}/{user_id}', headers={ 'Access-Token': token })
            
            # Assert
            self.assert_response(response, b'[INVALID_TOKEN]', HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_put_user_successful(self):
        with self.app.test_client() as client:
            # Arrange
            user = self.app.mongo.db.users.find_one({ 'email': 'foo@foo.com' })

            user_id = str(user['_id'])

            token = create_token(user, 60, self.app.config['SECRET_KEY'])

            self.app.redis.get.return_value = token

            fields = { 'phone': '+4915768985562' }

            # Act
            response = client.put(f'{Routes.USERS_V1}/{user_id}', json=fields, headers={ 'Access-Token': token })
            
            # Assert
            self.assert_response(response, b'', HttpStatusCode.HTTP_204_NO_CONTENT)

            user = self.app.mongo.db.users.find_one({ 'email': 'foo@foo.com' })
            # TODO: Review this syntax of accessing collection and potentially check phone against user 'collection-view / consolidate-collection'
            self.assertEqual(user['changes'][0]['fields']['phone'], fields['phone'])



# WIP
class TestUserListMethods(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_post_user_without_token(self):
        pass

    def test_post_user_already_exists(self):
        pass

    def test_post_user_successful(self):
        pass


if __name__ == '__main__':
    unittest.main()
