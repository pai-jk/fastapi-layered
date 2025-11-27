"""AppDB 라우터"""

from fastapi import APIRouter, Depends
from src.app_query_db.service import AppQueryDBService

from webapp.dependency import app_db_service_dependency
from webapp.dto import CreateUserDTO, OkDTO, UpdateUserDTO

router = APIRouter()


@router.post("/query/users", response_model=OkDTO, status_code=201)
async def create_user_query(
    user_data: CreateUserDTO,
    service: AppQueryDBService = Depends(app_db_service_dependency),
) -> OkDTO:
    """User 생성"""
    user_domain = await service.create_user(user_data.name, user_data.email)
    return OkDTO(content=user_domain)


@router.get("/query/users/{user_id}", response_model=OkDTO)
async def get_user_query(
    user_id: int,
    service: AppQueryDBService = Depends(app_db_service_dependency),
) -> OkDTO:
    """User 조회"""
    user_domain = await service.get_user(user_id)
    return OkDTO(content=user_domain)


@router.get("/query/users", response_model=OkDTO)
async def get_users_query(
    service: AppQueryDBService = Depends(app_db_service_dependency),
) -> OkDTO:
    """User 목록 조회"""
    result = await service.get_users()
    return OkDTO(content=result)


@router.put("/query/users/{user_id}", response_model=OkDTO)
async def update_user_query(
    user_id: int,
    user_data: UpdateUserDTO,
    service: AppQueryDBService = Depends(app_db_service_dependency),
) -> OkDTO:
    """User 수정"""
    user_domain = await service.update_user(user_id, user_data.name, user_data.email)
    return OkDTO(content=user_domain)


@router.delete("/query/users/{user_id}")
async def delete_user_query(
    user_id: int,
    service: AppQueryDBService = Depends(app_db_service_dependency),
) -> OkDTO:
    """User 삭제"""
    result = await service.delete_user(user_id)
    return OkDTO(content=result)
