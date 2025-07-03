from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr

from src.core.database.annotations import created_at, int_pk, updated_at


class BoardShopBase(AsyncAttrs, DeclarativeBase):
    """
    Базовая модель проекта. Абстрактная модель.

    Поля:
        created_at: Дата создания объекта в БД. Автозаполнение.
        updated_at: Дата изменения объекта в БД. Автозаполнение.

    Задает наследникам имя таблицы в БД строчными буквами от названия модели.
    """

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int_pk]
    created_at: created_at
    updated_at: updated_at
