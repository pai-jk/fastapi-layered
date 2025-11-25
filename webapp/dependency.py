from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from src.app1.service import App1Service
from webapp.container import ApplicationContainer


@inject
def app1_service_dependency(
    service: App1Service = Depends(
        Provide[ApplicationContainer.app1_container.service]
    ),
) -> App1Service:
    return service
