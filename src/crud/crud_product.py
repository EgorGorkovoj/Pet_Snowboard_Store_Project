from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

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


category_crud = CategoryCRUD(Category)
