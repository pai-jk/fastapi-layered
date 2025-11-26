import logging
from typing import List, Optional

from src.app_orm_db.domain import UserProfile, UserRole
from src.app_orm_db.repository import UserRepository
from src.app_orm_db.settings import AppDBSettings

logger = logging.getLogger(__name__)


class AppDBService:
    """AppDB 서비스"""

    def __init__(self, settings: AppDBSettings, repository: UserRepository):
        self.settings = settings
        self.repository = repository

    async def create_user(
        self, user_name: str, email: str, roles: Optional[List[UserRole]] = None
    ) -> UserProfile:
        """User 생성"""
        if roles is None:
            roles = [UserRole.USER]

        new_user = UserProfile.new_user(user_name=user_name, email=email, roles=roles)

        logger.info(f"User 생성 요청: {user_name}")
        await self.repository.create(new_user)
        return new_user

    async def get_user(self, user_id: int) -> UserProfile:
        """User 조회"""
        logger.info(f"User 조회 요청: ID {user_id}")
        return await self.repository.get_by_id(user_id)

    async def get_users(self) -> List[UserProfile]:
        """User 목록 조회"""
        logger.info("User 목록 조회 요청")
        return await self.repository.find_all()

    async def update_user(
        self,
        user_id: int,
        user_name: Optional[str] = None,
        email: Optional[str] = None,
        roles: Optional[List[UserRole]] = None,
    ) -> UserProfile:
        """User 수정"""
        logger.info(f"User 수정 요청: ID {user_id}")

        user = await self.repository.get_by_id(user_id)

        # 변경된 필드만 업데이트
        if user_name is not None:
            user.user_name = user_name
        if email is not None:
            user.email = email
        if roles is not None:
            user.roles = roles

        await self.repository.update(user)
        return user

    async def delete_user(self, user_id: int) -> None:
        """User 삭제"""
        logger.info(f"User 삭제 요청: ID {user_id}")
        await self.repository.delete(user_id)
