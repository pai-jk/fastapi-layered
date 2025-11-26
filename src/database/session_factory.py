import asyncio
import logging
from contextlib import AbstractContextManager, asynccontextmanager
from typing import Callable

import sqlalchemy.exc
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from src.database.base import Base
from src.database.settings import DatabaseSettings
from src.exceptions import DatabaseException, DBIntegrityException, NotFoundException

logger = logging.getLogger(__name__)


class SessionFactory:
    """비동기 데이터베이스 클래스"""

    def __init__(self, settings: DatabaseSettings):
        logger.info(f"initialize SessionFactory({settings.DB_TYPE})")
        if settings.DB_TYPE.startswith("sqlite"):
            self._engine = create_async_engine(settings.DB_TYPE)
        elif settings.DB_TYPE.startswith("postgresql"):
            url = URL.create(
                "postgresql+psycopg",
                username=settings.DB_USER,
                password=settings.DB_PASSWORD,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
            )
            self._engine = create_async_engine(
                url,
                echo=settings.DB_ECHO,
                pool_size=5,
                max_overflow=0,
                pool_recycle=30 * 60,
            )
        else:
            raise DatabaseException(
                f"지원하지 않는 database type입니다. {settings.DB_TYPE}"
            )

        self._session_factory = async_scoped_session(
            async_sessionmaker(
                autocommit=False,
                bind=self._engine,
            ),
            scopefunc=asyncio.current_task,
        )

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @asynccontextmanager  # type: ignore
    async def __call__(self) -> Callable[..., AbstractContextManager[AsyncSession]]:  # type: ignore
        session: AsyncSession = self._session_factory()
        try:
            yield session  # type: ignore
        except sqlalchemy.exc.NoResultFound:
            await session.rollback()
            raise NotFoundException("데이터를 못발견했아요")
        except sqlalchemy.exc.IntegrityError:
            await session.rollback()
            raise DBIntegrityException("데이터를 못발견했아요")
        except Exception as e:
            logger.exception("Session rollback because of exception")
            await session.rollback()
            raise e
        finally:
            await session.close()
            await self._session_factory.remove()

    async def connect(self):
        return await self._engine.connect()
