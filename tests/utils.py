import unittest


class CustomAssertions:
    def __init__(self):
        unittest.TestCase.maxDiff = None

    """
    A class to store custom assertions.
    """

    def assert_response(self, response, data: bytes, status_code: int):
        """
        Asserts a response message based on the message and status code returned from the test_client.
        
        Keyword arguments:

        :param response: The response result of the client call
        :param bytes data: The message data expected from the response
        :param int status_code: The http status code expected from the response


        ```
        def test_name(self):
            with self.app.test_client() as client:
                # Act
                response = client.delete('/route/to/the/endpoint')

                # Assert
                self.assert_response(response, 'Access Forbidden', 403)
        ```


        """
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status_code)
