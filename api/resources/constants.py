class HttpStatusCode:
    """
    This class defines all constants for HTTP Status Codes to be used throughout the API.
    """

    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204

    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_409_CONFLICT = 409

    HTTP_500_INTERNAL_SERVER_ERROR = 500


class Routes:
    """
    This class defines all constants for the routes of the API Resources.
    """

    EVENTS_V1 = '/api/v1/events'
    USERS_V1 = '/api/v1/users'
    LOGIN_V1 = '/api/v1/auth/login'
    LOGOUT_V1 = '/api/v1/auth/logout'
