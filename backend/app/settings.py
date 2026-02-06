from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    DEBUG: bool = False
    PGHOST: str
    PGDATABASE: str
    PGUSER: str
    PGPASSWORD: str
    PGPORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return (f'postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}')


class Settings(DatabaseSettings):
    DEBUG: bool = False



settings = Settings()