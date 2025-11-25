class BaseException(Exception):
    """기본 오류"""

    message: str = "Base error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ClientException(BaseException):
    """400 오류"""

    message: str = "Client error"


class ForbiddenException(BaseException):
    """403 오류"""

    message: str = "Forbidden error"


class NotFoundException(BaseException):
    """404 오류"""

    message: str = "Not found error"


class ServerException(BaseException):
    """500 오류"""

    message: str = "Internal server error"


class DatabaseException(BaseException):
    """데이터베이스 오류"""

    message: str = "Database error"


class DBIntegrityException(DatabaseException):
    """데이터베이스 정합성 오류"""

    message: str = "Database integrity error"


class UnknownException(BaseException):
    """알 수 없는 오류"""

    message: str = "Unknown error"
