from dependency_injector import containers, providers

from src.app_db.repository import UserRepository
from src.app_db.service import AppDBService
from src.app_db.settings import AppDBSettings
from src.database.container import DatabaseContainer
from src.database.session_factory import SessionFactory


class AppDBContainer(containers.DeclarativeContainer):
    """AppDB 컨테이너"""

    settings = providers.Singleton(AppDBSettings)
    database = providers.Container(DatabaseContainer)
    session_factory: providers.Singleton[SessionFactory] = providers.Singleton(
        SessionFactory, settings=database.settings
    )
    repository: providers.Factory[UserRepository] = providers.Factory(
        UserRepository, session_factory=session_factory
    )

    app_db_service = providers.Factory(
        AppDBService,
        settings=settings,
        repository=repository,
    )
