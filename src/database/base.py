from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

DomainKey = TypeVar("DomainKey")
Domain = TypeVar("Domain")


class Base(AsyncAttrs, DeclarativeBase, Generic[DomainKey, Domain]):
    """엔티티에 대한 기본 설정(exceptions 설정)을 정의"""

    __abstract__ = True

    @staticmethod
    def from_domain(domain: Domain):
        """도메인 객체를 엔티티로 변환합니다."""
        raise NotImplementedError("from_domain method is not implemented")

    def to_domain(self) -> Domain:
        """엔티티 객체를 도메인 객체로 변환합니다."""
        raise NotImplementedError("to_domain method is not implemented")

    def update(self, domain: Domain):
        """도메인 객체로 엔티티의 값을 업데이트합니다."""
        raise NotImplementedError("update method is not implemented")

    def primary_key(self) -> DomainKey:
        """엔티티의 기본 키를 반환합니다."""
        raise NotImplementedError("primary_key method is not implemented")
