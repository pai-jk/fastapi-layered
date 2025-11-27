import logging
from typing import List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.app_query_db.settings import AppQueryDBSettings
from src.database.session_factory import SessionFactory

logger = logging.getLogger(__name__)


class AppQueryDBService:
    """AppDB 서비스"""

    def __init__(self, settings: AppQueryDBSettings, session_factory: SessionFactory):
        self.settings = settings
        self.session_factory = session_factory

    async def run_query(self, query: str) -> List[dict]:
        """Query 실행"""
        logger.info(f"Query 실행: {query}")
        session: AsyncSession
        async with self.session_factory() as session:
            result = await session.execute(text(query))
            return [dict(row) for row in result.mappings()]

    async def get_users(self) -> List[dict]:
        """Users 조회"""
        query = "SELECT * FROM users"
        return await self.run_query(query)

    async def get_user(self, user_id: int) -> List[dict]:
        """User 조회"""
        query = f"SELECT * FROM users WHERE id = {user_id}"
        return await self.run_query(query)

    async def create_user(self, user_name: str, email: str) -> List[dict]:
        """User 생성"""
        query = (
            f"INSERT INTO users (user_name, email) VALUES ('{user_name}', '{email}')"
        )
        return await self.run_query(query)

    async def update_user(
        self,
        user_id: int,
        user_name: str | None = None,
        email: str | None = None,
    ) -> List[dict]:
        """User 수정"""
        query = f"UPDATE users SET user_name = '{user_name}', email = '{email}' WHERE id = {user_id}"
        return await self.run_query(query)

    async def delete_user(self, user_id: int) -> List[dict]:
        """User 삭제"""
        query = f"DELETE FROM users WHERE id = {user_id}"
        return await self.run_query(query)
