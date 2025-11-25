import logging

from dependency_injector import containers, providers

from src.app_base.container import AppBaseContainer
from webapp.logger import initialize_logger
from webapp.settings import ApplicationSettings

logger = logging.getLogger(__name__)


class ApplicationContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["webapp"])
    settings = providers.Singleton(ApplicationSettings)
    logger = providers.Resource(initialize_logger)

    app_base_container = providers.Container(AppBaseContainer)


def create_container() -> ApplicationContainer:
    container = ApplicationContainer()
    return container
