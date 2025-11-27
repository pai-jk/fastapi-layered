import abc
import logging
from contextlib import AbstractContextManager
from dataclasses import fields
from typing import Callable, Generic, List, Optional

import sqlalchemy
from sqlalchemy import asc, delete, desc, exists, func, inspect, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database.base import Base, Domain, DomainKey
from src.exceptions import AlreadyExistsException, NotFoundException

logger = logging.getLogger(__name__)


def reflect_domain(src, dst):
    """도메인 객체의 필드를 엔티티로 반영

    두 객체 간의 값을 동기화하여 도메인 객체의 값을 엔티티 객체에 복사합니다.

    Args:
        src: 복사할 대상 엔티티 객체
        dst: 값이 복사될 도메인 객체
    """

    for field in fields(dst):
        new_value = getattr(dst, field.name)
        setattr(src, field.name, new_value)


class BaseRepository(abc.ABC, Generic[DomainKey, Domain]):
    """기본 저장소 관리

    엔티티와 관련된 데이터베이스 CRUD 작업을 수행하는 기본 저장소 클래스입니다.

    Attrs:
        entity: 관리할 엔티티 클래스
        session_factory: 세션 생성 함수
    """

    entity: Base

    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[AsyncSession]]
    ):
        """BaseRepository 초기화

        Args:
            session_factory: 세션 생성 함수
        """
        logger.info(f"initialize Repository({self.entity.__name__})")
        self.session_factory = session_factory

    async def create(self, domain: Domain) -> None:
        """새로운 엔티티를 저장소에 저장

        Args:
            domain: 저장할 도메인 객체
        Raises:
            AlreadyExistsException: 엔티티가 이미 존재할 경우 발생
        """

        async with self.session_factory() as session:  # type: ignore
            await self._create(session, domain)
            await session.commit()

    async def update(self, domain: Domain) -> None:
        """엔티티 정보를 업데이트

        Args:
            domain: 업데이트할 도메인 객체
        Raises:
            NotFoundException: 엔티티가 존재하지 않을 경우 발생
        """

        async with self.session_factory() as session:  # type: ignore
            entity_primary_key = get_primary_key(self.entity, domain)
            try:
                entity = await self._get_by_id(session, entity_primary_key)
            except NotFoundException:
                raise NotFoundException(
                    f"{self.entity}의 {entity_primary_key}가 발견되지 않았습니다."
                )
            await self._update(session, entity, domain)
            await session.commit()

    async def update_field(self, key: DomainKey, **kwargs) -> bool:
        """특정 필드를 업데이트

        Args:
            key: 엔티티의 기본 키
            kwargs: 업데이트할 필드 값
        Raises:
            NotImplementedError: 아직 구현되지 않은 경우 발생
        """

        async with self.session_factory() as session:  # type: ignore
            criteria = create_id_criteria(self.entity, key)
            result = await session.execute(
                update(self.entity).filter(*criteria).values(**kwargs)  # type: ignore
            )
            await session.commit()
            return result.rowcount > 0

    async def update_fields_by(self, filters: dict, updates: dict) -> int:
        """지정된 필드 값 조건(filters)에 맞는 행들을 주어진 값(updates)으로 업데이트

        Args:
            filters (dict): WHERE 조건 필드-값 쌍
            updates (dict): SET 대상 필드-값 쌍

        Returns:
            int: 업데이트된 행 수
        """
        async with self.session_factory() as session:  # type: ignore
            criteria = create_field_criteria(self.entity, filters)
            stmt = update(self.entity).where(*criteria).values(**updates)  # type: ignore
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount

    async def save(self, domain: Domain) -> None:
        """엔티티 저장 또는 업데이트

        Args:
            domain: 저장할 도메인 객체
        """

        async with self.session_factory() as session:  # type: ignore
            entity_primary_key = get_primary_key(self.entity, domain)
            if entity := await self._find_by_id(session, entity_primary_key):
                await self._update(session, entity, domain)
            else:
                await self._create(session, domain)
            await session.commit()

    async def delete(self, key: DomainKey) -> None:
        """엔티티를 삭제

        Args:
            key: 삭제할 엔티티의 기본 키
        Raises:
            NotFoundException: 엔티티가 존재하지 않을 경우 발생
        """

        async with self.session_factory() as session:  # type: ignore
            criteria = create_id_criteria(self.entity, key)
            stmt = delete(self.entity).filter(*criteria)  # type: ignore
            if (await session.execute(stmt)).rowcount == 0:
                raise NotFoundException(f"{self.entity}의 {key}가 발견되지 않았습니다.")
            await session.commit()

    async def delete_by(self, **kwargs) -> None:
        """엔티티를 삭제

        Args:
            key: 삭제할 엔티티의 기본 키
        Raises:
            NotFoundException: 엔티티가 존재하지 않을 경우 발생
        """

        async with self.session_factory() as session:  # type: ignore
            criteria = create_field_criteria(self.entity, kwargs)
            stmt = delete(self.entity).filter(*criteria)  # type: ignore
            await session.execute(stmt)
            await session.commit()

    async def get_by_id(self, key: DomainKey) -> Domain:
        """기본 키를 통해 엔티티를 검색

        Args:
            key: 검색할 엔티티의 기본 키
        Returns:
            Domain: 검색된 도메인 객체
        Raises:
            NotFoundException: 엔티티를 찾지 못할 경우 발생
        """
        async with self.session_factory() as session:  # type: ignore
            try:
                entity = await self._get_by_id(session, key)
                if entity is None:
                    raise NotFoundException(
                        f"{self.entity}의 {key}가 발견되지 않았습니다."
                    )
            except sqlalchemy.orm.exc.NoResultFound:  # type: ignore
                raise NotFoundException(f"{self.entity}의 {key}가 발견되지 않았습니다.")
            return entity.to_domain()

    async def get_by_ids(self, keys: List[DomainKey]) -> List[Domain]:
        """여러 개의 기본 키를 통해 엔티티 리스트를 조회합니다.

        Args:
            keys (List[DomainKey]): 조회할 엔티티들의 기본 키 리스트

        Returns:
            List[Domain]: 검색된 도메인 객체 리스트

        Raises:
            NotFoundException: 어떤 엔티티도 조회되지 않은 경우
        """
        if not keys:
            return []

        async with self.session_factory() as session:  # type: ignore
            pk_field = self.entity.__mapper__.primary_key[0]

            stmt = (
                self._get_select_based_on_relationship()
                .where(pk_field.in_(keys))
                .distinct()
            )

            result = await session.execute(stmt)
            entities = result.scalars().all()

            if not entities:
                raise NotFoundException(
                    f"{self.entity}에서 {keys}에 해당하는 항목을 찾을 수 없습니다."
                )

            return [entity.to_domain() for entity in entities]

    async def find_by_id(self, key: DomainKey) -> Optional[Domain]:
        """기본 키로 엔티티를 검색하여 선택적으로 반환

        Args:
            key: 검색할 엔티티의 기본 키
        Returns:
            Optional[Domain]: 검색된 도메인 객체 또는 None
        """

        async with self.session_factory() as session:  # type: ignore
            if entity := await self._find_by_id(session, key):
                return entity.to_domain()
        return None

    async def find_all(self) -> List[Domain]:
        """모든 엔티티 목록을 반환

        Returns:
            List[Domain]: 엔티티 도메인 객체 리스트
        """

        async with self.session_factory() as session:  # type: ignore
            stmt = self._get_select_based_on_relationship()
            if hasattr(self.entity, "is_deleted"):
                stmt = stmt.where(self.entity.is_deleted == False)  # type: ignore

            result = await session.execute(stmt)
            entities = self._handle_scalars(result)
            return [entity.to_domain() for entity in entities]

    async def find_all_ordered(
        self, order: str = "created_at", direction: str = "desc"
    ) -> List[Domain]:
        """정렬 조건에 따라 모든 엔티티를 반환

        Args:
            order (str): 정렬 기준 필드명
            direction (str): 정렬 방향 ('asc' 또는 'desc')

        Returns:
            List[Domain]: 정렬된 도메인 객체 리스트

        Raises:
            ValueError: 존재하지 않는 필드로 정렬 시 예외 발생
        """
        async with self.session_factory() as session:  # type: ignore
            if not hasattr(self.entity, order):
                raise ValueError(
                    f"{self.entity.__name__}에 '{order}' 필드가 존재하지 않습니다."
                )

            order_column = getattr(self.entity, order)
            ordering = (
                asc(order_column) if direction.lower() == "asc" else desc(order_column)  # type: ignore
            )
            stmt = self._get_select_based_on_relationship().order_by(ordering)

            if hasattr(self.entity, "is_deleted"):
                stmt = stmt.where(self.entity.is_deleted == False)  # type: ignore

            result = await session.execute(stmt)
            entities = self._handle_scalars(result)
            return [entity.to_domain() for entity in entities]

    async def exist_by(self, **kwargs) -> bool:
        """주어진 필드를 기반으로 엔티티가 존재하는지 확인

        Args:
            kwargs: 검색할 필드와 값
        Returns:
            bool: 엔티티가 존재하는지 여부
        """
        async with self.session_factory() as session:  # type: ignore
            criteria = create_field_criteria(self.entity, kwargs)
            stmt = select(exists(self.entity)).where(*criteria)  # type: ignore
            result = await session.execute(stmt)
            return bool(result.scalar())

    async def count_by(self, **kwargs) -> int:
        async with self.session_factory() as session:  # type: ignore
            criteria = create_field_criteria(self.entity, kwargs)
            stmt = select(func.count()).select_from(self.entity).where(*criteria)  # type: ignore
            result = await session.execute(stmt)
            return result.scalar_one()

    async def count_by_like(self, **kwargs) -> int:
        """주어진 필드를 기반으로 LIKE 검색을 수행하여 개수를 반환

        Args:
            kwargs: 검색할 필드와 값 (LIKE 검색)
        Returns:
            int: 검색 조건에 맞는 엔티티 개수
        """
        async with self.session_factory() as session:  # type: ignore
            criteria = create_like_criteria(self.entity, kwargs)
            stmt = select(func.count()).select_from(self.entity).where(*criteria)  # type: ignore
            result = await session.execute(stmt)
            return result.scalar_one()

    async def get_by(self, **kwargs) -> Domain:
        """주어진 필드를 기반으로 엔터티 검색

        find_by vs get_by
        - find_by: 여러개의 엔터티를 검색 (없는 경우, 빈 리스트 반환)
        - get_by: 하나의 엔터티를 검색 (없는 경우, NotFoundException 발생)
        """
        domains = await self.find_by(**kwargs)
        if len(domains) == 0:
            raise NotFoundException(f"{self.entity}에서 {kwargs} 찾을 수 없습니다.")
        return domains[0]

    async def find_by(self, **kwargs) -> List[Domain]:
        """주어진 필드를 기반으로 엔티티를 검색

        Args:
            kwargs: 검색할 필드와 값
        Returns:
            List[Domain]: 검색된 도메인 객체 리스트
        """

        async with self.session_factory() as session:  # type: ignore
            criteria = create_field_criteria(self.entity, kwargs)
            stmt = self._get_select_based_on_relationship().filter(*criteria)
            result = await session.execute(stmt)
            entities = self._handle_scalars(result)
            return [entity.to_domain() for entity in entities]

    async def find_in(self, **kwargs) -> List[Domain]:
        """주어진 필드를 기반으로 IN 검색을 수행

        Args:
            kwargs: 검색할 필드와 값 (IN 검색)
        Returns:
            List[Domain]: 검색된 도메인 객체 리스트
        """

        async with self.session_factory() as session:  # type: ignore
            criteria = create_in_criteria(self.entity, kwargs)
            stmt = self._get_select_based_on_relationship().filter(*criteria)
            result = await session.execute(stmt)
            entities = self._handle_scalars(result)
            return [entity.to_domain() for entity in entities]

    async def find_by_like(self, **kwargs) -> List[Domain]:
        """주어진 필드를 기반으로 LIKE 검색을 수행

        Args:
            kwargs: 검색할 필드와 값 (LIKE 검색)
        Returns:
            List[Domain]: 검색된 도메인 객체 리스트
        """

        async with self.session_factory() as session:  # type: ignore
            criteria = create_like_criteria(self.entity, kwargs)
            stmt = self._get_select_based_on_relationship().filter(*criteria)
            result = await session.execute(stmt)
            entities = self._handle_scalars(result)
            return [entity.to_domain() for entity in entities]

    def _get_select_based_on_relationship(self):
        """엔티티의 관계 여부에 따라 적절한 select 문을 반환

        Returns:
            Select: 엔티티의 select 문
        """

        if self._has_relationships():
            return self._get_joined_select()
        else:
            return select(self.entity)  # type: ignore

    def _get_joined_select(self):
        """관계가 있는 엔티티를 위한 조인된 select 문을 반환

        Returns:
            Select: 조인된 select 문
        """

        query = select(self.entity)  # type: ignore
        for attr in inspect(self.entity).relationships:  # type: ignore
            query = query.options(joinedload(attr.class_attribute))
        return query

    def _has_relationships(self):
        """엔티티가 관계를 갖고 있는지 확인

        Returns:
            bool: 관계 여부
        """
        return bool(inspect(self.entity).relationships)  # type: ignore

    async def _get_by_id(self, session, key: DomainKey):
        """기본 키로 엔티티를 검색

        Args:
            session: 데이터베이스 세션
            key: 기본 키
        Returns:
            Entity: 검색된 엔티티 객체
        """

        criteria = create_id_criteria(self.entity, key)
        stmt = self._get_select_based_on_relationship().filter(*criteria)
        return self._handle_unique(await session.execute(stmt))

    async def _find_by_id(self, session, key: DomainKey):
        """기본 키로 엔티티를 검색하여 선택적으로 반환

        Args:
            session: 데이터베이스 세션
            key: 기본 키
        Returns:
            Optional[Entity]: 검색된 엔티티 객체 또는 None
        """

        criteria = create_id_criteria(self.entity, key)
        stmt = self._get_select_based_on_relationship().filter(*criteria)
        return (await session.execute(stmt)).scalars().one_or_none()

    async def _create(self, session, domain: Domain) -> None:
        """엔티티 생성

        Args:
            session: 데이터베이스 세션
            domain: 생성할 도메인 객체
        Raises:
            AlreadyExistsException: 엔티티가 이미 존재할 경우 발생
        """

        entity = self.entity.from_domain(domain)
        session.add(entity)
        try:
            await session.flush()
        except sqlalchemy.exc.IntegrityError as e:  # type: ignore
            # 중복 키 에러인 경우에만 AlreadyExistsException 발생
            if (
                "duplicate key" in str(e).lower()
                or "unique constraint" in str(e).lower()
            ):
                raise AlreadyExistsException(f"{domain} already exists")
            else:
                # 다른 제약 조건 위반은 원래 예외를 다시 발생
                raise

        if len(inspect(self.entity).relationships) > 0:  # type: ignore
            await session.refresh(entity)

        new_domain = entity.to_domain()
        reflect_domain(domain, new_domain)

    async def _update(self, session, entity, domain: Domain) -> None:
        """엔티티 업데이트

        Args:
            session: 데이터베이스 세션
            entity: 업데이트할 엔티티 객체
            domain: 업데이트할 도메인 객체
        """

        entity.update(domain)
        await session.flush()

    def _handle_scalars(self, result):
        """중복된 스칼라 값을 처리

        Args:
            result: 검색된 결과
        Returns:
            List: 중복 제거된 스칼라 리스트
        """

        scalars = result.scalars()
        if self._has_relationships():
            return self._remove_duplicates(scalars)
        else:
            return scalars.all()

    def _handle_unique(self, result):
        """중복된 결과를 처리하여 하나의 값을 반환

        Args:
            result: 검색된 결과
        Returns:
            Entity: 중복 제거된 엔티티 객체
        """

        if self._has_relationships():
            return result.scalars().first()
        else:
            return result.scalars().one()

    def _remove_duplicates(self, scalars):
        """조인된 로드로 인한 중복을 제거

        Args:
            scalars: 중복된 스칼라 값
        Returns:
            List: 중복 제거된 스칼라 값 리스트
        """
        return scalars.unique().all()


def create_id_criteria(entity: Base, key: DomainKey):
    """엔티티의 기본 키를 기반으로 필터링 조건을 생성

    기본 키가 여러 개인 경우, 해당 키와 값 쌍에 대한 필터링 조건을 생성합니다.

    Args:
        entity (Base): 필터링할 엔티티 클래스
        key (DomainKey): 필터링할 기본 키 값

    Returns:
        List[sqlalchemy.sql.elements.BinaryExpression]: SQLAlchemy 필터링 조건 목록
    """

    primary_keys = inspect(entity).primary_key  # type: ignore
    if len(primary_keys) == 1:
        return [primary_keys[0] == key]
    else:
        return [primary_key == k for primary_key, k in zip(primary_keys, key)]  # type: ignore


def create_field_criteria(entity, kwargs):
    """주어진 필드 값으로 필터링 조건을 생성

    Args:
        entity: 필터링할 엔티티 클래스
        kwargs: 필터링할 필드와 값의 쌍

    Returns:
        List[sqlalchemy.sql.elements.BinaryExpression]: SQLAlchemy 필터링 조건 목록
    """

    return [getattr(entity, key) == value for key, value in kwargs.items()]


def create_in_criteria(entity, kwargs):
    """주어진 필드를 기반으로 IN 검색을 위한 조건을 생성

    Args:
        entity: 필터링할 엔티티 클래스
        kwargs: 검색할 필드와 값 (IN 검색)
    """
    return [getattr(entity, key).in_(value) for key, value in kwargs.items()]


def create_like_criteria(entity, kwargs):
    """주어진 필드를 기반으로 LIKE 검색을 위한 조건을 생성

    Args:
        entity: 필터링할 엔티티 클래스
        kwargs: 검색할 필드와 값 (LIKE 검색)

    Returns:
        List[sqlalchemy.sql.elements.BinaryExpression]: SQLAlchemy LIKE 검색 조건 목록
    """
    from sqlalchemy import String, Text

    criteria = []
    for key, value in kwargs.items():
        column = getattr(entity, key)
        # 문자열 타입인 경우에만 LIKE 검색 적용
        if isinstance(column.type, (String, Text)):
            criteria.append(column.like(f"%{value}%"))
        else:
            # 정수형 등 다른 타입은 정확한 일치 검색
            criteria.append(column == value)

    return criteria


def get_primary_key(entity: Base, domain: Domain):
    """도메인 객체의 기본 키 값을 반환

    엔티티에서 도메인 객체로 변환한 후 기본 키 값을 반환합니다.

    Args:
        entity (Base): 기본 키를 가져올 엔티티 클래스
        domain (Domain): 기본 키를 추출할 도메인 객체

    Returns:
        DomainKey: 엔티티의 기본 키 값
    """

    return entity.from_domain(domain).primary_key()
