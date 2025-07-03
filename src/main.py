from fastapi import FastAPI

from src.api.v1.router import main_router
from src.core.config.app import settings
from src.core.config.logging import LoggingMidleware

app_v1 = FastAPI(title=settings.app_title, description=settings.app_description)

app_v1.router.include_router(main_router)
app_v1.middleware('http')(LoggingMidleware())


def main():
    """Функция запустит управляющую функцию. Для доступа извне."""
    pass


if __name__ == '__main__':
    main()
