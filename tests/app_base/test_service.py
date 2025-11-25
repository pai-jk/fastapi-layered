from unittest.mock import patch

import pytest

from src.app_base.service import AppBaseService
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


@pytest.fixture
def app_base_service():
    """AppBaseService 인스턴스 생성

    이 fixture는 각 테스트 메서드에서 사용할 AppBaseService 인스턴스를 생성합니다.
    AppBaseSettings를 사용하여 기본 설정으로 서비스를 초기화합니다.

    Args:
        없음 (pytest fixture 자동 주입)

    Returns:
        AppBaseService: 설정이 적용된 AppBaseService 인스턴스

    Example:
        ```python
        def test_hello(self, app_base_service):
            result = app_base_service.hello()
            assert result.message == "Hello, AppBaseService!"
        ```
    """
    settings = AppBaseSettings()
    return AppBaseService(settings)


class TestAppBaseServiceExceptions:
    """AppBaseService 예외 처리 테스트

    이 클래스는 AppBaseService의 각 예외 발생 메서드가 올바르게 동작하는지 테스트합니다.
    각 예외 타입별로 메시지가 정확히 전달되는지, 예외가 올바르게 발생하는지 검증합니다.
    """

    def test_raise_client_exception(self, app_base_service):
        """ClientException 발생 테스트

        Given: AppBaseService 인스턴스와 클라이언트 오류 메시지
        When: raise_client_exception 메서드를 호출
        Then: ClientException이 발생하고 메시지가 정확히 전달됨

        Args:
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(ClientException) as exc_info:
            app_base_service.raise_client_exception("테스트 클라이언트 오류")

        assert exc_info.value.message == "테스트 클라이언트 오류"

    def test_raise_forbidden_exception(self, app_base_service):
        """ForbiddenException 발생 테스트

        Given: AppBaseService 인스턴스와 접근 거부 메시지
        When: raise_forbidden_exception 메서드를 호출
        Then: ForbiddenException이 발생하고 메시지가 정확히 전달됨

        Args:
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(ForbiddenException) as exc_info:
            app_base_service.raise_forbidden_exception("테스트 접근 거부")

        assert exc_info.value.message == "테스트 접근 거부"

    def test_raise_not_found_exception(self, app_base_service):
        """NotFoundException 발생 테스트

        Given: AppBaseService 인스턴스와 리소스 이름
        When: raise_not_found_exception 메서드를 호출
        Then: NotFoundException이 발생하고 리소스 이름이 포함된 메시지가 전달됨

        Args:
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(NotFoundException) as exc_info:
            app_base_service.raise_not_found_exception("테스트 리소스")

        assert "테스트 리소스를 찾을 수 없습니다" in exc_info.value.message

    def test_raise_server_exception(self, app_base_service):
        """ServerException 발생 테스트

        Given: AppBaseService 인스턴스와 서버 오류 메시지
        When: raise_server_exception 메서드를 호출
        Then: ServerException이 발생하고 메시지가 정확히 전달됨

        Args:
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(ServerException) as exc_info:
            app_base_service.raise_server_exception("테스트 서버 오류")

        assert exc_info.value.message == "테스트 서버 오류"

    def test_raise_database_exception(self, app_base_service):
        """DatabaseException 발생 테스트

        Given: AppBaseService 인스턴스와 데이터베이스 오류 메시지
        When: raise_database_exception 메서드를 호출
        Then: DatabaseException이 발생하고 메시지가 정확히 전달됨

        Args:
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(DatabaseException) as exc_info:
            app_base_service.raise_database_exception("테스트 DB 오류")

        assert exc_info.value.message == "테스트 DB 오류"

    def test_raise_db_integrity_exception(self, app_base_service):
        """DBIntegrityException 발생 테스트

        Given: AppBaseService 인스턴스와 정합성 오류 메시지
        When: raise_db_integrity_exception 메서드를 호출
        Then: DBIntegrityException이 발생하고 메시지가 정확히 전달됨

        Args:
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(DBIntegrityException) as exc_info:
            app_base_service.raise_db_integrity_exception("테스트 정합성 오류")

        assert exc_info.value.message == "테스트 정합성 오류"

    def test_db_integrity_exception_inheritance(self, app_base_service):
        """DBIntegrityException이 DatabaseException을 상속하는지 테스트

        Given: AppBaseService 인스턴스
        When: raise_db_integrity_exception 메서드를 호출
        Then: DBIntegrityException이 DatabaseException으로도 캐치됨 (상속 관계 검증)

        Args:
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(DatabaseException):
            app_base_service.raise_db_integrity_exception("상속 테스트")


class TestAppBaseServiceLogging:
    """AppBaseService 로깅 테스트

    이 클래스는 AppBaseService의 각 예외 발생 메서드가 올바른 로그 레벨과 메시지로
    로깅하는지 테스트합니다. warning 레벨과 error 레벨, exc_info 파라미터 등을 검증합니다.
    """

    @patch("src.app_base.service.logger")
    def test_client_exception_logging(self, mock_logger, app_base_service):
        """ClientException 로깅 테스트

        Given: AppBaseService 인스턴스와 mock logger
        When: raise_client_exception 메서드를 호출
        Then: logger.warning이 한 번 호출되고 "ClientException 발생" 메시지가 포함됨

        Args:
            mock_logger: Mock된 logger 객체
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(ClientException):
            app_base_service.raise_client_exception("로깅 테스트")

        mock_logger.warning.assert_called_once()
        assert "ClientException 발생" in str(mock_logger.warning.call_args)

    @patch("src.app_base.service.logger")
    def test_forbidden_exception_logging(self, mock_logger, app_base_service):
        """ForbiddenException 로깅 테스트

        Given: AppBaseService 인스턴스와 mock logger
        When: raise_forbidden_exception 메서드를 호출
        Then: logger.warning이 한 번 호출되고 "ForbiddenException 발생" 메시지가 포함됨

        Args:
            mock_logger: Mock된 logger 객체
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(ForbiddenException):
            app_base_service.raise_forbidden_exception("로깅 테스트")

        mock_logger.warning.assert_called_once()
        assert "ForbiddenException 발생" in str(mock_logger.warning.call_args)

    @patch("src.app_base.service.logger")
    def test_not_found_exception_logging(self, mock_logger, app_base_service):
        """NotFoundException 로깅 테스트

        Given: AppBaseService 인스턴스와 mock logger
        When: raise_not_found_exception 메서드를 호출
        Then: logger.warning이 한 번 호출되고 "NotFoundException 발생" 메시지가 포함됨

        Args:
            mock_logger: Mock된 logger 객체
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(NotFoundException):
            app_base_service.raise_not_found_exception("리소스")

        mock_logger.warning.assert_called_once()
        assert "NotFoundException 발생" in str(mock_logger.warning.call_args)

    @patch("src.app_base.service.logger")
    def test_server_exception_logging(self, mock_logger, app_base_service):
        """ServerException 로깅 테스트

        Given: AppBaseService 인스턴스와 mock logger
        When: raise_server_exception 메서드를 호출
        Then:
            - logger.error가 한 번 호출됨
            - "ServerException 발생" 메시지가 포함됨
            - exc_info=True 파라미터가 전달됨 (예외 정보 포함)

        Args:
            mock_logger: Mock된 logger 객체
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(ServerException):
            app_base_service.raise_server_exception("로깅 테스트")

        mock_logger.error.assert_called_once()
        assert "ServerException 발생" in str(mock_logger.error.call_args)
        # exc_info=True 확인
        assert mock_logger.error.call_args[1]["exc_info"] is True

    @patch("src.app_base.service.logger")
    def test_database_exception_logging(self, mock_logger, app_base_service):
        """DatabaseException 로깅 테스트

        Given: AppBaseService 인스턴스와 mock logger
        When: raise_database_exception 메서드를 호출
        Then:
            - logger.error가 한 번 호출됨
            - "DatabaseException 발생" 메시지가 포함됨
            - exc_info=True 파라미터가 전달됨 (예외 정보 포함)

        Args:
            mock_logger: Mock된 logger 객체
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(DatabaseException):
            app_base_service.raise_database_exception("로깅 테스트")

        mock_logger.error.assert_called_once()
        assert "DatabaseException 발생" in str(mock_logger.error.call_args)
        assert mock_logger.error.call_args[1]["exc_info"] is True

    @patch("src.app_base.service.logger")
    def test_db_integrity_exception_logging(self, mock_logger, app_base_service):
        """DBIntegrityException 로깅 테스트

        Given: AppBaseService 인스턴스와 mock logger
        When: raise_db_integrity_exception 메서드를 호출
        Then:
            - logger.error가 한 번 호출됨
            - "DBIntegrityException 발생" 메시지가 포함됨
            - exc_info=True 파라미터가 전달됨 (예외 정보 포함)

        Args:
            mock_logger: Mock된 logger 객체
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(DBIntegrityException):
            app_base_service.raise_db_integrity_exception("로깅 테스트")

        mock_logger.error.assert_called_once()
        assert "DBIntegrityException 발생" in str(mock_logger.error.call_args)
        assert mock_logger.error.call_args[1]["exc_info"] is True


class TestAppBaseServiceScenarios:
    """AppBaseService 시나리오 테스트

    이 클래스는 simulate_error_scenario 메서드를 통해 다양한 오류 시나리오를
    시뮬레이션하고, 각 시나리오에 맞는 예외가 발생하고 로깅이 올바르게 수행되는지 테스트합니다.
    """

    @patch("src.app_base.service.logger")
    def test_simulate_client_error_scenario(self, mock_logger, app_base_service):
        """클라이언트 오류 시나리오 테스트

        Given: AppBaseService 인스턴스와 mock logger
        When: simulate_error_scenario("client_error")를 호출
        Then:
            - ClientException이 발생함
            - logger.info가 한 번 호출됨 (시나리오 시작 로그)
            - logger.warning이 한 번 호출됨 (예외 로그)

        Args:
            mock_logger: Mock된 logger 객체
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(ClientException):
            app_base_service.simulate_error_scenario("client_error")

        mock_logger.info.assert_called_once()
        mock_logger.warning.assert_called_once()

    @patch("src.app_base.service.logger")
    def test_simulate_forbidden_scenario(self, mock_logger, app_base_service):
        """접근 거부 시나리오 테스트

        Given: AppBaseService 인스턴스와 mock logger
        When: simulate_error_scenario("forbidden")를 호출
        Then:
            - ForbiddenException이 발생함
            - logger.info가 한 번 호출됨 (시나리오 시작 로그)
            - logger.warning이 한 번 호출됨 (예외 로그)

        Args:
            mock_logger: Mock된 logger 객체
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(ForbiddenException):
            app_base_service.simulate_error_scenario("forbidden")

        mock_logger.info.assert_called_once()
        mock_logger.warning.assert_called_once()

    @patch("src.app_base.service.logger")
    def test_simulate_not_found_scenario(self, mock_logger, app_base_service):
        """리소스 없음 시나리오 테스트

        Given: AppBaseService 인스턴스와 mock logger
        When: simulate_error_scenario("not_found")를 호출
        Then:
            - NotFoundException이 발생함
            - logger.info가 한 번 호출됨 (시나리오 시작 로그)
            - logger.warning이 한 번 호출됨 (예외 로그)

        Args:
            mock_logger: Mock된 logger 객체
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(NotFoundException):
            app_base_service.simulate_error_scenario("not_found")

        mock_logger.info.assert_called_once()
        mock_logger.warning.assert_called_once()

    @patch("src.app_base.service.logger")
    def test_simulate_server_error_scenario(self, mock_logger, app_base_service):
        """서버 오류 시나리오 테스트

        Given: AppBaseService 인스턴스와 mock logger
        When: simulate_error_scenario("server_error")를 호출
        Then:
            - ServerException이 발생함
            - logger.info가 한 번 호출됨 (시나리오 시작 로그)
            - logger.error가 2번 호출됨
              * 첫 번째: raise_server_exception 메서드 내부에서 로깅
              * 두 번째: simulate_error_scenario의 except 블록에서 로깅

        Args:
            mock_logger: Mock된 logger 객체
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(ServerException):
            app_base_service.simulate_error_scenario("server_error")

        mock_logger.info.assert_called_once()
        # 예외 발생 메서드와 simulate_error_scenario의 except 블록에서 각각 로깅되므로 2번 호출됨
        assert mock_logger.error.call_count == 2

    @patch("src.app_base.service.logger")
    def test_simulate_database_error_scenario(self, mock_logger, app_base_service):
        """데이터베이스 오류 시나리오 테스트

        Given: AppBaseService 인스턴스와 mock logger
        When: simulate_error_scenario("database_error")를 호출
        Then:
            - DatabaseException이 발생함
            - logger.info가 한 번 호출됨 (시나리오 시작 로그)
            - logger.error가 2번 호출됨
              * 첫 번째: raise_database_exception 메서드 내부에서 로깅
              * 두 번째: simulate_error_scenario의 except 블록에서 로깅

        Args:
            mock_logger: Mock된 logger 객체
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(DatabaseException):
            app_base_service.simulate_error_scenario("database_error")

        mock_logger.info.assert_called_once()
        # 예외 발생 메서드와 simulate_error_scenario의 except 블록에서 각각 로깅되므로 2번 호출됨
        assert mock_logger.error.call_count == 2

    @patch("src.app_base.service.logger")
    def test_simulate_integrity_error_scenario(self, mock_logger, app_base_service):
        """정합성 오류 시나리오 테스트

        Given: AppBaseService 인스턴스와 mock logger
        When: simulate_error_scenario("integrity_error")를 호출
        Then:
            - DBIntegrityException이 발생함
            - logger.info가 한 번 호출됨 (시나리오 시작 로그)
            - logger.error가 2번 호출됨
              * 첫 번째: raise_db_integrity_exception 메서드 내부에서 로깅
              * 두 번째: simulate_error_scenario의 except 블록에서 로깅

        Args:
            mock_logger: Mock된 logger 객체
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(DBIntegrityException):
            app_base_service.simulate_error_scenario("integrity_error")

        mock_logger.info.assert_called_once()
        # 예외 발생 메서드와 simulate_error_scenario의 except 블록에서 각각 로깅되므로 2번 호출됨
        assert mock_logger.error.call_count == 2

    @patch("src.app_base.service.logger")
    def test_simulate_unknown_scenario(self, mock_logger, app_base_service):
        """알 수 없는 시나리오 테스트

        Given: AppBaseService 인스턴스와 mock logger
        When: simulate_error_scenario("unknown")를 호출 (알 수 없는 시나리오)
        Then:
            - 예외가 발생하지 않고 문자열이 반환됨
            - 반환값이 "알 수 없는 시나리오: unknown"임
            - logger.info가 한 번 호출됨 (시나리오 시작 로그)
            - logger.warning이 한 번 호출됨 (알 수 없는 시나리오 경고)

        Args:
            mock_logger: Mock된 logger 객체
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(UnknownException):
            app_base_service.simulate_error_scenario("unknown")

        mock_logger.info.assert_called_once()
        mock_logger.error.call_count == 2


class TestAppBaseServiceIntegration:
    """AppBaseService 통합 테스트

    이 클래스는 예외 계층 구조, 기본 메시지 등 여러 기능이 함께 동작하는
    통합 시나리오를 테스트합니다.
    """

    def test_exception_hierarchy(self, app_base_service):
        """예외 계층 구조 테스트

        Given: AppBaseService 인스턴스
        When:
            - raise_db_integrity_exception을 호출하여 DBIntegrityException 발생
            - raise_client_exception을 호출하여 ClientException 발생
        Then:
            - DBIntegrityException이 DatabaseException으로도 캐치됨 (상속 관계)
            - ClientException이 AppBaseException으로도 캐치됨 (상속 관계)

        이 테스트는 예외의 상속 계층 구조가 올바르게 설계되었는지 검증합니다.

        Args:
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        # DBIntegrityException은 DatabaseException을 상속
        with pytest.raises(DatabaseException):
            app_base_service.raise_db_integrity_exception("계층 테스트")

        # 모든 예외는 AppBaseException을 상속
        with pytest.raises(AppBaseException):
            app_base_service.raise_client_exception("기본 예외 테스트")

    def test_default_messages(self, app_base_service):
        """기본 메시지 테스트

        Given: AppBaseService 인스턴스
        When: 각 예외 발생 메서드를 메시지 없이 호출 (기본값 사용)
        Then: 각 예외 타입에 맞는 기본 메시지가 설정됨

        이 테스트는 예외 발생 메서드들이 기본 메시지를 올바르게 사용하는지 검증합니다.

        Args:
            app_base_service: AppBaseService 인스턴스 (fixture)
        """
        with pytest.raises(ClientException) as exc_info:
            app_base_service.raise_client_exception()

        assert exc_info.value.message == "잘못된 요청입니다"

        with pytest.raises(ForbiddenException) as exc_info:
            app_base_service.raise_forbidden_exception()

        assert exc_info.value.message == "접근이 거부되었습니다"

        with pytest.raises(ServerException) as exc_info:
            app_base_service.raise_server_exception()

        assert exc_info.value.message == "서버 내부 오류가 발생했습니다"
