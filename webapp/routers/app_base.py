from fastapi import APIRouter, Depends

from src.app_base.service import AppBaseService
from webapp.dependency import app_base_service_dependency
from webapp.dto import HelloAppBaseDTO

router = APIRouter()


@router.get("/hello-app-base")
async def hello_app_base(
    service: AppBaseService = Depends(app_base_service_dependency),
) -> HelloAppBaseDTO:
    hello_app_base_domain = service.hello()
    return HelloAppBaseDTO.from_domain(hello_app_base_domain)
