from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler, set_rollback


class CustomResponse(Response):
    def __init__(self, data=None, status=None, template_name=None, headers=None, exception=False, content_type=None,
                 error_code=None, message=None):
        super().__init__(data, status, template_name, headers, exception, content_type)
        # custom field error_code, message
        self.error_code = error_code
        self.message = message


class WrittenException(APIException):
    # custom_exception_handler에서 로직 분기를 위한 클래
    error_code = 0
    message = ""


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            data = {'detail': exc.detail}

        set_rollback()
        # custom exception 로직
        if isinstance(exc, WrittenException):
            response = CustomResponse(data, status=exc.status_code, headers=headers, error_code=exc.error_code,
                                      message=exc.message)
            response.data['status_code'] = response.status_code
            response.data['errorcode'] = response.error_code
            response.data['message'] = response.message
            response.data['detail'] = "Written Custom Error"
            return response
        # 이 분기를 타면 기본 django 구현 로직과 같
        else:
            return Response(data, status=exc.status_code, headers=headers)

    return None


# 10000 : Users
class InvalidFacebookTokenException(WrittenException):
    status_code = 400
    error_code = 10001
    message = "Invalid facebook token"


class NicknameDuplicateException(WrittenException):
    status_code = 400
    error_code = 10002
    message = "Nickname duplicate"


class UserDoesNotExistException(WrittenException):
    status_code = 400
    error_code = 10003
    message = "User does not exist"


class UserNotAuthorizedException(WrittenException):
    status_code = 400
    error_code = 10004
    message = "User is not authorized"


class UserAlreadySignedUpException(WrittenException):
    status_code = 400
    error_code = 10005
    message = "User already signed up"


class UserNotSignedUpException(WrittenException):
    status_code = 400
    error_code = 10006
    message = "Not signed up"



# 20000 Postings
class TitleDoesNotExistException(WrittenException):
    status_code = 400
    error_code = 20002
    message = "Title does not exist"


class PostingDoesNotExistException(WrittenException):
    status_code = 400
    error_code = 20003
    message = "Posting does not exist"


class ContentIsEmptyException(WrittenException):
    status_code = 400
    error_code = 20004
    message = "Content is empty"


class TitleNameIsEmptyException(WrittenException):
    status_code = 400
    error_code = 20005
    message = "Title name is empty"

class TitleNameIsDuplicateException(WrittenException):
    status_code = 400
    error_code = 20006
    message = "Title name is duplicate"

# 30000 Subscriptions
class AlreadySubscribedException(WrittenException):
    status_code = 400
    error_code = 30001
    message = "User is already subscribed"


class AlreadyUnsubscribedException(WrittenException):
    status_code = 400
    error_code = 30002
    message = "User is not subscribed"


# 40000 Scraps
class AlreadyScrappedException(WrittenException):
    status_code = 400
    error_code = 40001
    message = "Posting is already scrapped"


class AlreadyUnscrappedException(WrittenException):
    status_code = 400
    error_code = 40002
    message = "Posting is not scrapped"
