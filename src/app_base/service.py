from src.app_base.domain import HelloAppBaseDomain
from src.app_base.settings import AppBaseSettings


class AppBaseService:
    """AppBase 서비스"""

    def __init__(self, settings: AppBaseSettings):
        self.settings = settings

    def hello(self) -> HelloAppBaseDomain:
        return HelloAppBaseDomain(message="Hello, AppBaseService!")
