from fastapi import FastAPI

from src.config import settings

app_v1 = FastAPI(title=settings.app_title, description=settings.app_description)

# app_v1.router.include_router()


def main():
    """Функция запустит управляющую функцию. Для доступа извне."""
    pass


if __name__ == '__main__':
    main()
