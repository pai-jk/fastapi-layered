## AppBaseService 테스트 모듈

이 모듈은 AppBaseService의 모든 기능을 테스트합니다.

테스트 구조:
- TestAppBaseServiceExceptions: 예외 발생 메서드 테스트
- TestAppBaseServiceLogging: 로깅 기능 테스트
- TestAppBaseServiceScenarios: 시나리오 기반 통합 테스트
- TestAppBaseServiceIntegration: 예외 계층 구조 및 기본값 테스트

다른 서비스에 대한 테스트 작성 가이드:
=====================================

1. 테스트 파일 구조
   - 파일명: tests/test_<service_name>_service.py
   - 패턴: test_<모듈명>_service.py

2. 기본 테스트 클래스 구조
   ```python
   @pytest.fixture
   def <service_name>_service():
       """<ServiceName>Service 인스턴스 생성

       Returns:
           <ServiceName>Service: 설정이 적용된 서비스 인스턴스
       """
       settings = <ServiceName>Settings()
       return <ServiceName>Service(settings)

   class Test<ServiceName>ServiceExceptions:
       """<ServiceName>Service 예외 처리 테스트"""
       # 예외 발생 메서드 테스트

   class Test<ServiceName>ServiceLogging:
       """<ServiceName>Service 로깅 테스트"""
       # 로깅 기능 테스트

   class Test<ServiceName>ServiceScenarios:
       """<ServiceName>Service 시나리오 테스트"""
       # 비즈니스 로직 시나리오 테스트

   class Test<ServiceName>ServiceIntegration:
       """<ServiceName>Service 통합 테스트"""
       # 통합 테스트
   ```

3. 테스트 작성 원칙
   - 각 메서드는 하나의 기능만 테스트
   - Given-When-Then 패턴 사용
   - Mock을 사용하여 외부 의존성 격리
   - 예외 케이스도 반드시 테스트
   - 로깅이 있는 경우 로깅도 검증

4. Mock 사용 예시
   ```python
   @patch("src.<module>.service.logger")
   def test_method_logging(self, mock_logger, <service>_service):
       """메서드 로깅 테스트"""
       # Given: 테스트 준비
       # When: 메서드 실행
       # Then: 로깅 검증
       mock_logger.info.assert_called_once()
   ```

5. 예외 테스트 예시
   ```python
   def test_raise_exception(self, <service>_service):
       """예외 발생 테스트"""
       # Given: 예외 조건
       # When: 예외 발생 메서드 호출
       with pytest.raises(<ExceptionType>) as exc_info:
           <service>_service.raise_<exception>()
       # Then: 예외 메시지 검증
       assert exc_info.value.message == "예상 메시지"
   ```

6. 시나리오 테스트 예시
   ```python
   @patch("src.<module>.service.logger")
   def test_scenario(self, mock_logger, <service>_service):
       """시나리오 테스트"""
       # Given: 시나리오 조건
       # When: 시나리오 실행
       result = <service>_service.simulate_scenario("scenario_name")
       # Then: 결과 및 로깅 검증
       assert result == "예상 결과"
       mock_logger.info.assert_called_once()
   ```

7. 통합 테스트 예시
   ```python
   def test_integration(self, <service>_service):
       """통합 테스트"""
       # 여러 메서드를 조합하여 실제 사용 시나리오 테스트
       # 예외 계층 구조, 기본값, 의존성 등 검증
   ```