from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Определяет конфигурацию проекта.

    В случае отсутствия явного значения параметра - пытается извлечь его значение
    из переменной окружения с аналогичным названием, но записанной в верхнем регистре,
    располагающейся в файле с переменными окружения.

    При наличии явного значения параметра и аналогичной переменной окружения в файле
    с переменными окружения - будет перезаписано значением из файла с переменными окружения.
    """

    app_title: str
    app_description: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    port_db_postgres: str
    db_type: str
    db_api: str
    db_host: str

    @property
    def database_url(self):
        return (
            f'{self.db_type}+{self.db_api}://'
            f'{self.postgres_user}:{self.postgres_password}@'
            f'{self.db_host}:{self.port_db_postgres}'
            f'/{self.postgres_db}'
        )

    model_config = ConfigDict(env_file='.env', extra='ignore')


settings = Settings()
