from dependency_injector import containers, providers

from src.database.session_factory import SessionFactory
from src.database.settings import DatabaseSettings


class DatabaseContainer(containers.DeclarativeContainer):
    settings = providers.Singleton(DatabaseSettings)

    session_factory = providers.Singleton(SessionFactory, settings=settings)