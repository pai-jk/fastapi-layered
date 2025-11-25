import logging

from src.app_base.domain import HelloAppBaseDomain
from src.app_base.settings import AppBaseSettings
from src.exceptions import BaseException as AppBaseException
from src.exceptions import (
    ClientException,
    DatabaseException,
    DBIntegrityException,
    ForbiddenException,
    NotFoundException,
    ServerException,
    UnknownException,
)

logger = logging.getLogger(__name__)


class AppBaseService:
    """AppBase 서비스"""

    def __init__(self, settings: AppBaseSettings):
        self.settings = settings

    def hello(self) -> HelloAppBaseDomain:
        return HelloAppBaseDomain(message="Hello, AppBaseService!")

    def raise_client_exception(self, message: str = "잘못된 요청입니다") -> None:
        """400 오류 발생 샘플"""
        logger.warning(f"ClientException 발생: {message}")
        raise ClientException(message)

    def raise_forbidden_exception(self, message: str = "접근이 거부되었습니다") -> None:
        """403 오류 발생 샘플"""
        logger.warning(f"ForbiddenException 발생: {message}")
        raise ForbiddenException(message)

    def raise_not_found_exception(self, resource: str = "리소스") -> None:
        """404 오류 발생 샘플"""
        message = f"{resource}를 찾을 수 없습니다"
        logger.warning(f"NotFoundException 발생: {message}")
        raise NotFoundException(message)

    def raise_server_exception(
        self, message: str = "서버 내부 오류가 발생했습니다"
    ) -> None:
        """500 오류 발생 샘플"""
        logger.error(f"ServerException 발생: {message}", exc_info=True)
        raise ServerException(message)

    def raise_database_exception(
        self, message: str = "데이터베이스 오류가 발생했습니다"
    ) -> None:
        """데이터베이스 오류 발생 샘플"""
        logger.error(f"DatabaseException 발생: {message}", exc_info=True)
        raise DatabaseException(message)

    def raise_db_integrity_exception(
        self, message: str = "데이터베이스 정합성 오류가 발생했습니다"
    ) -> None:
        """데이터베이스 정합성 오류 발생 샘플"""
        logger.error(f"DBIntegrityException 발생: {message}", exc_info=True)
        raise DBIntegrityException(message)

    def raise_unknown_exception(
        self, message: str = "알 수 없는 오류가 발생했습니다"
    ) -> None:
        """알 수 없는 오류 발생 샘플"""
        logger.error(f"UnknownException 발생: {message}", exc_info=True)
        raise UnknownException(message)

    def simulate_error_scenario(self, scenario: str) -> str:
        """다양한 오류 시나리오 시뮬레이션"""
        logger.info(f"오류 시나리오 시뮬레이션 시작: {scenario}")

        try:
            if scenario == "client_error":
                self.raise_client_exception("TEST:클라이언트 요청 검증 실패")
            elif scenario == "forbidden":
                self.raise_forbidden_exception("TEST:권한이 없습니다")
            elif scenario == "not_found":
                self.raise_not_found_exception("TEST:사용자")
            elif scenario == "server_error":
                self.raise_server_exception("TEST:서버 처리 중 오류 발생")
            elif scenario == "database_error":
                self.raise_database_exception("TEST:데이터베이스 연결 실패")
            elif scenario == "integrity_error":
                self.raise_db_integrity_exception("TEST:중복된 키로 인한 정합성 오류")
            else:
                self.raise_unknown_exception("TEST:알 수 없는 시나리오")

            return "TEST:성공"
        except AppBaseException as e:
            logger.error(f"TEST:시나리오 실행 중 오류 발생: {e.message}", exc_info=True)
            raise e
