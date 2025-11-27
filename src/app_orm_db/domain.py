from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class UserRole(str, Enum):
    """사용자 역할"""

    ADMIN = "ADMIN"
    USER = "USER"


@dataclass
class UserProfile:
    user_id: Optional[int]
    user_name: str
    email: str
    roles: List[UserRole]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def new_user(
        user_name: str,
        email: str,
        roles: List[UserRole],
    ) -> "UserProfile":
        """새로운 계정 생성"""
        return UserProfile(
            user_id=None,
            user_name=user_name,
            email=email,
            roles=roles,
            is_deleted=False,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def delete(self) -> "UserProfile":
        self.is_deleted = True
        self.updated_at = datetime.now(tz=timezone.utc)
        return self

    def update(self, user: "UserProfile") -> "UserProfile":
        self.user_name = user.user_name
        self.email = user.email
        self.roles = user.roles
        self.updated_at = datetime.now(tz=timezone.utc)
        return self
