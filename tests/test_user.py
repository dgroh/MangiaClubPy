import unittest

from flask import jsonify

from bson import ObjectId

from api import create_app
from api.resources.constants import HttpStatusCode, Routes

from tests.utils import CustomAssertions, create_token, create_user


class TestUserMethods(unittest.TestCase, CustomAssertions):
    def setUp(self):
        self.app = create_app()

        create_user(self.app)

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
            expected_user = self.app.mongo.db.users.find_one({'email': 'foo@foo.com'})
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
            user = self.app.mongo.db.users.find_one({'email': 'foo@foo.com'})

            # Act
            response = client.put(f'{Routes.USERS_V1}/{str(user["_id"])}')

            # Assert
            self.assert_response(response, b'[HTTP_403_FORBIDDEN]', HttpStatusCode.HTTP_403_FORBIDDEN)

    def test_put_user_not_found(self):
        with self.app.test_client() as client:
            # Arrange
            random_id = str(ObjectId())

            user = {'_id': random_id, 'email': 'foo@foo.com', 'phone': '+4915162961189'}

            token = create_token(user, 60, self.app.config['SECRET_KEY'])

            self.app.redis.get.return_value = token

            # Act
            response = client.put(f'{Routes.USERS_V1}/{random_id}', headers={'Access-Token': token})

            # Assert
            self.assert_response(response, b'[INVALID_TOKEN]', HttpStatusCode.HTTP_400_BAD_REQUEST)

    def test_put_user_token_expired(self):
        with self.app.test_client() as client:
            # Arrange
            user = self.app.mongo.db.users.find_one({'email': 'foo@foo.com'})

            user_id = str(user['_id'])

            token = create_token(user, -1, self.app.config['SECRET_KEY'])

            self.app.redis.get.return_value = token

            # Act
            response = client.put(f'{Routes.USERS_V1}/{user_id}', headers={'Access-Token': token})

            # Assert
            self.assert_response(response, b'[INVALID_TOKEN]', HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_put_user_successful(self):
        with self.app.test_client() as client:
            # Arrange
            user = self.app.mongo.db.users.find_one({'email': 'foo@foo.com'})

            user_id = str(user['_id'])

            token = create_token(user, 60, self.app.config['SECRET_KEY'])

            self.app.redis.get.return_value = token

            fields = {'phone': '+4915768985562'}

            # Act
            response = client.put(f'{Routes.USERS_V1}/{user_id}', json=fields, headers={'Access-Token': token})

            # Assert
            self.assert_response(response, b'', HttpStatusCode.HTTP_204_NO_CONTENT)

            user = self.app.mongo.db.users.find_one({'email': 'foo@foo.com'})
            # TODO: Review this syntax of accessing collection and potentially check phone against user 'collection-view / consolidate-collection'
            self.assertEqual(user['changes'][0]['fields']['phone'], fields['phone'])


class TestUserListMethods(unittest.TestCase, CustomAssertions):
    def setUp(self):
        self.app = create_app()

        create_user(self.app)

    def tearDown(self):
        pass

    def test_get_users_sucessful(self):
        with self.app.test_client() as client:
            # Arrange
            collection = self.app.mongo.db.users.find()

            users = []

            for user in collection:
                user['_id'] = str(user['_id'])
                user['hashed_password'] = user['hashed_password'].decode('utf-8')
                user['password_salt'] = user['password_salt'].decode('utf-8')

            users.append(user)

            # Act
            response = client.get(Routes.USERS_V1)

            # Assert
            self.assert_response(response, jsonify({'data': users}).data, HttpStatusCode.HTTP_200_OK)

    def test_post_user_without_request_args(self):
        with self.app.test_client() as client:
            # Act
            response = client.post(Routes.USERS_V1)

            # Assert
            self.assertIsNotNone(response.json['message'].get('email'))

    def test_post_user_already_exists(self):
        with self.app.test_client() as client:
            # Arrange
            user = {
                'email': 'foo@foo.com',
                'first_name': 'foo 2',
                'last_name': 'foo 2',
                'password': '654321',
                'phone': '+49157518975'
            }

            # Act
            response = client.post(Routes.USERS_V1, json=user)

            # Assert
            self.assert_response(response, b'[HTTP_409_CONFLICT]', HttpStatusCode.HTTP_409_CONFLICT)

    def test_post_user_successful(self):
        with self.app.test_client() as client:
            # Arrange
            user = {
                'email': 'foo2@foo.com',
                'first_name': 'foo 2',
                'last_name': 'foo 2',
                'password': '654321',
                'phone': '+49157518975'
            }

            # Act
            response = client.post(Routes.USERS_V1, json=user)

            # Assert
            self.assert_response(response, b'[HTTP_201_CREATED]', HttpStatusCode.HTTP_201_CREATED)


if __name__ == '__main__':
    unittest.main()
