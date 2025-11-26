from datetime import datetime
from typing import List

from sqlalchemy import JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.app_db.domain import UserProfile, UserRole
from src.database.base import Base


class UserEntity(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(nullable=False, unique=False)
    roles: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=False)
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    @staticmethod
    def from_domain(domain: UserProfile) -> "UserEntity":
        return UserEntity(
            user_id=domain.user_id,
            user_name=domain.user_name,
            roles=domain.roles,
            email=domain.email,
            is_deleted=domain.is_deleted,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )

    def to_domain(self) -> UserProfile:
        return UserProfile(
            user_id=self.user_id,
            user_name=self.user_name,
            roles=[UserRole(role) for role in self.roles],
            email=self.email,
            is_deleted=self.is_deleted,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def update(self, domain: UserProfile) -> None:
        self.user_name = domain.user_name
        self.email = domain.email
        self.roles = [role.value for role in domain.roles]
        self.is_deleted = domain.is_deleted
        self.updated_at = domain.updated_at

    def primary_key(self) -> int:
        return self.user_id
