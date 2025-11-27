from dependency_injector import containers, providers

from src.app_query_db.service import AppQueryDBService
from src.app_query_db.settings import AppQueryDBSettings
from src.database.container import DatabaseContainer


class AppQueryDBContainer(containers.DeclarativeContainer):
    """AppQueryDB 컨테이너"""

    settings = providers.Singleton(AppQueryDBSettings)
    database = providers.Container(DatabaseContainer)

    app_query_db_service = providers.Factory(
        AppQueryDBService,
        settings=settings,
        session_factory=database.session_factory,
    )
