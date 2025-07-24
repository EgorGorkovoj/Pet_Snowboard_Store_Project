from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.logging import logger
from src.core.constants import TextErrorConstants
from src.crud.crud_base import CRUDBase
from src.models.product import Brand


class BrandCRUD(CRUDBase):
    """
    CRUD-класс для работы с моделью Brand.

    Назначение:
        Управляет созданием и получением брендов товаров.
    """

    async def get_brand_by_name(self, session: AsyncSession, brand_name: str) -> Optional[Brand]:
        """
        Получает бренд по его названию.

        Параметры:
            session (AsyncSession): Сессия SQLAlchemy.
            brand_name (str): Название бренда.

        Возвращает:
            Optional[Brand]: Найденный бренд или None, если бренд отсутствует.
        """
        result = await session.execute(select(Brand).where(Brand.name == brand_name))
        return result.scalars().first()

    async def create_brand_by_name_from_product(
        self, session: AsyncSession, brand_name: str, auto_commit: bool = True
    ) -> Brand:
        """
        Создает новый бренд, если он не найден в базе.

        Назначение:
            Используется при создании нового товара. Если бренд отсутствует,
            он автоматически добавляется в таблицу.

        Параметры:
            session (AsyncSession): Сессия SQLAlchemy.
            brand_name (str): Название бренда, который нужно создать.
            auto_commit (bool): Выполнить commit автоматически (по умолчанию True).

        Возвращает:
            Brand: Созданный объект бренда.
        """

        db_obj = Brand(name=brand_name)
        try:
            session.add(db_obj)
            if auto_commit:
                await session.commit()
                await session.refresh(db_obj)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return db_obj


brand_crud = BrandCRUD(Brand)
