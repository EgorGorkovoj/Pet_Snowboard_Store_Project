from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr

from src.core.database.annotations import created_at, updated_at


class BoardShopBase(AsyncAttrs, DeclarativeBase):
    """
    Базовая модель проекта.

    Поля:
        created_at: Дата создания объекта в БД. Автозаполнение.
        updated_at: Дата изменения объекта в БД. Автозаполнение.

    Задает наследникам имя таблицы в БД строчными буквами от названия модели.
    """

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    created_at: created_at
    updated_at: updated_at
