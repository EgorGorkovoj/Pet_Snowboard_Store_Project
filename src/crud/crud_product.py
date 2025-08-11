from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config.logging import logger
from src.core.constants import TextErrorConstants
from src.crud.crud_base import CRUDBase
from src.models.attribute import CategoryAttribute, ProductOptionAttribute
from src.models.product import Category, Product, ProductOption
from src.schemas.product import ProductCreateSchema, ProductOptionCreate


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

    async def attach_attribute_if_not_exists(
        self, session: AsyncSession, category_id: int, attribute_id: int, auto_commit: bool = False
    ) -> None:
        """
        Привязывает атрибут к категории, если такая связь ещё не существует.

        Аргументы:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            category_id (int): Идентификатор категории.
            attribute_id (int): Идентификатор атрибута.
            auto_commit (bool, optional): Автоматически выполнить коммит после добавления.
                                          По умолчанию False.

        Возвращает:
            None

        Исключения:
            Любые исключения, возникающие при работе с базой данных,
            будут залогированы и выброшены.
        """

        exists = await session.execute(
            select(CategoryAttribute).where(
                CategoryAttribute.category_id == category_id,
                CategoryAttribute.attribute_id == attribute_id,
            )
        )
        if not exists.scalars().first():
            try:
                session.add(CategoryAttribute(category_id=category_id, attribute_id=attribute_id))
                if auto_commit:
                    await session.commit()
            except Exception as error:
                await session.rollback()
                logger.error(
                    f'{TextErrorConstants.CREATE_SERVER_LOG} \
                      {CategoryAttribute.__name__}: {error}'
                )
                raise error


class ProductCRUD(CRUDBase):
    """
    CRUD-класс для управления основными объектами продуктов.

    Назначение:
        Позволяет получать и создавать записи товаров в базе данных.
    """

    async def get_product_by_name_and_season(
        self, session: AsyncSession, title_product: str, season: int
    ) -> Optional[Product]:
        """
        Получает продукт по его названию и сезону.

        Параметры:
            session (AsyncSession): Активная сессия базы данных.
            title_product (str): Название продукта.
            season (int): Сезон продукта.

        Возвращает:
            Optional[Product]: Найденный продукт или None, если не найден.
        """
        result = await session.execute(
            select(Product).where(and_(Product.title == title_product, Product.season == season))
        )
        return result.scalars().first()

    async def get_all_products_by_category(
        self,
        session: AsyncSession,
        category_id: int,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Product]:
        """
        Получает список продуктов, принадлежащих указанной категории.

        Параметры:
            session (AsyncSession): Асинхронная сессия базы данных.
            category_id (int): Идентификатор категории, по которой осуществляется фильтрация.
            limit (int, по умолчанию 10): Количество возвращаемых записей (пагинация).
            offset (int, по умолчанию 0): Смещение начала выборки (пагинация).

        Возвращает:
            List[Product]: Список объектов Product, соответствующих категории и пагинации.

        Примечание:
            Также загружается связанный объект бренда с помощью selectinload(Product.brand).
        """

        query = (
            select(Product)
            .where(Product.category_id == category_id)
            .options(selectinload(Product.brand))
        )
        if filters:
            query = self._apply_filters_by_attribute(query=query, filters=filters)
            query = query.distinct()
        query = self._apply_limit_offset(query=query, limit=limit, offset=offset)
        result = await session.execute(query)
        return result.scalars().all()  # type: ignore

    async def create_product(
        self,
        session: AsyncSession,
        product_schema: ProductCreateSchema,
        brand_id: int,
        auto_commit: bool = True,
    ) -> Product:
        """
        Создаёт новый продукт в базе данных на основе входной схемы.

        Назначение:
            Основной метод для создания товара, исключая связанные опции.

        Параметры:
            session (AsyncSession): Активная сессия базы данных.
            product_schema (ProductCreateSchema): Схема с данными о продукте.
            brand_id (int): Идентификатор бренда, связанного с товаром.
            auto_commit (bool): Нужно ли сразу выполнить commit (по умолчанию True).

        Возвращает:
            Product: Созданный объект товара.
        """

        obj_data = product_schema.model_dump(exclude={'product_options', 'brand_name'})
        obj_data['brand_id'] = brand_id
        db_obj = self.model(**obj_data)
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


class ProductOptionCRUD(CRUDBase):
    """
    CRUD-класс для работы с вариантами продукта (например, по размерам, артикулам и т.п.).

    Назначение:
        Управляет созданием и получением вариантов товаров, связанных с основным продуктом.
    """

    async def get_product_option_by_article(
        self, session: AsyncSession, article: str
    ) -> Optional[ProductOption]:
        """
        Получает вариант продукта по артикулу.

        Параметры:
            session (AsyncSession): Активная сессия базы данных.
            article (str): Артикул варианта продукта.

        Возвращает:
            Optional[ProductOption]: Найденный вариант или None.
        """
        result = await session.execute(
            select(ProductOption).where(ProductOption.article == article)
        )
        return result.scalars().first()

    async def get_products_options_with_attributes(
        self, session: AsyncSession, product_id: int
    ) -> List[ProductOption]:
        """
        Получает все варианты товара с их характеристиками и названиями характеристик
        (оптимизировано через selectinload).

        Параметры:
            session (AsyncSession): Активная сессия базы данных.
            product_id (int): Идентификатор продукта.

        Возвращает:
            List[ProductOption]: Список вариантов продукта с атрибутами и их названиями.
        """

        result = await session.execute(
            select(ProductOption)
            .where(ProductOption.product_id == product_id)
            .options(
                selectinload(ProductOption.product),
                selectinload(ProductOption.attributes).selectinload(
                    ProductOptionAttribute.attribute
                ),
            )
        )
        return result.scalars().all()  # type: ignore

    async def get_product_option_by_id(
        self, session: AsyncSession, product_id: int, product_option_id: int
    ) -> Optional[ProductOption]:
        """
        Получает один вариант товара.

        Параметры:
            session (AsyncSession): Активная сессия базы данных.
            product_id (int): Идентификатор  продукта.
            product_option_id (int): Идентификатор варианта продукта.

        Возвращает:
            ProductOption: Вариант продукта.
        """

        result = await session.execute(
            select(ProductOption).where(
                and_(ProductOption.product_id == product_id, ProductOption.id == product_option_id)
            )
        )
        product_option = result.scalars().first()
        if not product_option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=TextErrorConstants.PRODUCT_OPTION_NOT_FOUND,
            )
        return product_option

    async def create_product_option(
        self,
        session: AsyncSession,
        product_id: int,
        product_option_in_bd: ProductOptionCreate,
        auto_commit: bool = True,
    ) -> ProductOption:
        """
        Создаёт вариант продукта и связывает его с основным товаром.

        Назначение:
            Используется при создании товара с несколькими артикулами, размерами и т.п.

        Параметры:
            session (AsyncSession): Активная сессия базы данных.
            product_id (int): ID продукта, к которому относится вариант.
            product_option_in_bd (ProductOptionCreate): Схема с данными варианта.
            auto_commit (bool): Нужно ли выполнять commit автоматически.

        Возвращает:
            ProductOption: Созданный вариант продукта.
        """

        obj_data = product_option_in_bd.model_dump(exclude={'additional_attributes'})
        obj_data['product_id'] = product_id
        db_obj = self.model(**obj_data)
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


category_crud = CategoryCRUD(Category)
product_crud = ProductCRUD(Product)
product_option_crud = ProductOptionCRUD(ProductOption)
