from dependency_injector import containers, providers

from src.app_base.service import AppBaseService
from src.app_base.settings import AppBaseSettings


class AppBaseContainer(containers.DeclarativeContainer):
    """AppBase 컨테이너"""

    settings = providers.Singleton(AppBaseSettings)

    app_base_service = providers.Factory(AppBaseService, settings=settings)
