from src.app_db.domain import UserProfile
from src.app_db.entities import UserEntity
from src.database.repository import BaseRepository


class UserRepository(BaseRepository[int, UserProfile]):
    """사용자 저장소"""

    entity = UserEntity  # type: ignore
