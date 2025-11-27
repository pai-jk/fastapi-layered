import logging

from dependency_injector import containers, providers

from src.app_base.container import AppBaseContainer
from src.app_orm_db.container import AppDBContainer
from src.app_query_db.container import AppQueryDBContainer
from webapp.logger import initialize_logger
from webapp.settings import ApplicationSettings

logger = logging.getLogger(__name__)


class ApplicationContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["webapp"])
    settings = providers.Singleton(ApplicationSettings)
    logger = providers.Resource(initialize_logger)

    app_base_container = providers.Container(AppBaseContainer)
    app_db_container = providers.Container(AppDBContainer)
    app_query_db_container = providers.Container(AppQueryDBContainer)


def create_container() -> ApplicationContainer:
    container = ApplicationContainer()
    return container
