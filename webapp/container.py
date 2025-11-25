import logging

from dependency_injector import containers, providers

from webapp.logger import initialize_logger
from webapp.settings import ApplicationSettings

logger = logging.getLogger(__name__)


class ApplicationContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["webapp"])
    settings = providers.Singleton(ApplicationSettings)
    logger = providers.Resource(initialize_logger)


def create_container() -> ApplicationContainer:
    container = ApplicationContainer()
    return container
