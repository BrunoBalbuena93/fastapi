from dataclasses import dataclass
from os import getenv
app_name = 'bookstore'

from dotenv import load_dotenv
# Import env variables
load_dotenv(f'{app_name}.env')

@dataclass
class PostgresqlConfig:
    host: str = getenv('DB_HOST', '127.0.0.1')
    port: int = getenv('DB_PORT', 5432)
    user: str = getenv('DB_USER')
    password: str = getenv('DB_PASSWORD')
    database: str = getenv('DB_NAME', 'bookstore_fastapi')

    @property
    def db_url(self) -> str:
        return f'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'


@dataclass
class Config:
    '''
    '''
    db_config: PostgresqlConfig = PostgresqlConfig()



config = Config()
