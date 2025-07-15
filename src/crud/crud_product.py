from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.constants import TextErrorConstants
from src.crud.crud_base import CRUDBase
from src.models.product import Category


class CategoryCRUD(CRUDBase):
    """
    CRUD-класс для работы с моделью Category.

    Назначение:
        Реализует операции создания, чтения, обновления и удаления (CRUD)
        категорий товаров в базе данных. Используется в сервисах и роутерах,
        где требуется взаимодействие с сущностью Category через асинхронную сессию.

    Наследует:
        CRUDBase — базовый класс с общими методами для всех моделей.
    """

    async def get_category_by_title_or_slug(
        self, session: AsyncSession, title_category: str, slug_category: str
    ) -> Optional[Category]:
        """
        Получает категорию по названию или слагу.

        Назначение:
            Используется для проверки существования категории перед созданием новой.
            Это позволяет обеспечить уникальность названия и slug.

        Аргументы:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            title_category (str): Название категории для поиска.
            slug_category (str): Слаг категории для поиска.

        Возвращает:
            Optional[Category]: Найденная категория или None, если совпадений нет.
        """
        query_category = await session.execute(
            select(Category).where(
                or_(Category.title == title_category, Category.slug == slug_category)
            )
        )
        return query_category.scalars().first()

    async def get_all_main_categories(self, session: AsyncSession) -> List[str]:
        """
        Получает список названий всех главных категорий (без родителя).

        Аргументы:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.

        Возвращает:
            List[str]: Список названий главных категорий.

        Исключения:
            HTTPException: Если не найдено ни одной главной категории.
        """
        categories = await session.execute(
            select(Category.title).where(Category.parent_category_id.is_(None))
        )
        titles = categories.scalars().all()

        if not titles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=TextErrorConstants.MAIN_CATEGORY_NOT_FOUND,
            )
        return titles  # type: ignore

    async def get_subcategories_by_parent_title(
        self, session: AsyncSession, parent_title: str
    ) -> List[str]:
        """
        Получает подкатегории по названию родительской категории.

        Аргументы:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            parent_title (str): Название родительской категории.

        Возвращает:
            List[str]: Названия подкатегорий.

        Исключения:
            HTTPException: Если родительская категория не найдена.
        """
        result = await session.execute(
            select(Category)
            .where(Category.title == parent_title)
            .options(selectinload(Category.categories))
        )
        parent_сategories = result.scalars().first()

        if not parent_сategories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=TextErrorConstants.PARENT_CATEGORY_NOT_FOUND.format(
                    parent_title=parent_title
                ),
            )

        return [subcategory.title for subcategory in parent_сategories.categories]


category_crud = CategoryCRUD(Category)
