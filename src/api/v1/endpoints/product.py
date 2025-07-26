from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.validators import (
    check_on_duplicate_attributes_for_one_option_product,
    check_product_category_inclusion,
    validate_unique_article_product,
    validate_unique_category_title,
)
from src.core.database.db_depends import get_async_session
from src.crud.crud_attribute import attribute_crud, attribute_option_crud
from src.crud.crud_brand import brand_crud
from src.crud.crud_product import category_crud, product_crud, product_option_crud
from src.schemas.product import (
    AttributeReadSchema,
    CategoryCreateSchema,
    CategoryReadSchema,
    ProductCreateSchema,
    ProductOptionReadSchema,
    ProductReadSchema,
)

router = APIRouter()

# TODO: подключить пользователей!


@router.post('/categories', status_code=status.HTTP_201_CREATED, response_model=CategoryReadSchema)
async def create_categories(
    object_in: CategoryCreateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> CategoryReadSchema:
    """
    Создание новой категории товаров.

    Доступно только админам!

    Назначение:
        Обрабатывает запрос на создание новой категории. Проверяет уникальность
        названия и slug перед сохранением. Может создавать как основную категорию,
        так и подкатегорию, если указан ID родительской категории.

    Параметры:
        object_in (CategoryCreateSchema): Данные категории, переданные в теле запроса.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        CategoryReadSchema: Созданная категория с её ID, названием,
                            slug и ID родительской категории (если есть).
    """
    await validate_unique_category_title(
        session=session, title_category=object_in.title, slug_category=object_in.slug
    )
    db_obj = await category_crud.create(session=session, obj_in=object_in)

    return db_obj


@router.get('/categories', status_code=status.HTTP_200_OK, response_model=List[str])
async def get_the_main_categories(
    session: AsyncSession = Depends(get_async_session),
) -> List[str]:
    """
    Получает список всех главных категорий.

    Назначение:
        Используется для отображения основных (корневых) категорий товаров.

    Аргументы:
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с БД.

    Возвращает:
        List[str]: Список названий всех главных категорий.

    Исключения:
        HTTPException: 404, если в базе не найдено ни одной главной категории.
    """
    db_objects = await category_crud.get_all_main_categories(session=session)
    return db_objects


@router.get(
    '/categories/{parent_title}/subcategories',
    status_code=status.HTTP_200_OK,
    response_model=List[str],
)
async def get_subcategories_by_parent(
    parent_title: str, session: AsyncSession = Depends(get_async_session)
) -> List[str]:
    """
    Получает список подкатегорий по названию родительской категории.

    Аргументы:
        parent_title (str): Название родительской категории.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        List[str]: Названия подкатегорий.
    """
    return await category_crud.get_subcategories_by_parent_title(
        session=session, parent_title=parent_title
    )


@router.post('/product', status_code=status.HTTP_201_CREATED, response_model=ProductReadSchema)
async def create_product(
    product: ProductCreateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> ProductReadSchema:
    """
    Создаёт новый товар с вариантами и характеристиками.

    Только для администраторов!
    Категория должна быть создана заранее в базе данных.

    Поведение:
    - Если бренд не существует, создаётся автоматически.
    - Если товар с таким названием и сезоном уже есть — используется существующий.
    - Создаются варианты товара (артикулы).
    - Каждая характеристика (атрибут) создаётся при необходимости.
    - Автоматически привязывает найденные или озданные атрибуты к категории товара
      через модель "CategoryAttribute", если они ещё не привязаны.

    Параметры:
        product (ProductCreateSchema): Схема с данными о товаре, вариантах и атрибутах.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        ProductReadSchema: Сериализованный объект товара с вариантами и атрибутами.
    """
    category = await category_crud.get_or_404(session=session, obj_id=product.category_id)
    brand = await brand_crud.get_brand_by_name(session=session, brand_name=product.brand_name)
    if not brand:
        brand = await brand_crud.create_brand_by_name_from_product(
            session=session, brand_name=product.brand_name, auto_commit=True
        )
    product_in_bd = await product_crud.get_product_by_name_and_season(
        session=session, title_product=product.title, season=product.season
    )
    if not product_in_bd:
        product_in_bd = await product_crud.create_product(
            session=session, product_schema=product, brand_id=brand.id
        )

    optional_read_list: List[ProductOptionReadSchema] = []

    for product_option in product.product_options:
        await validate_unique_article_product(session=session, article=product_option.article)
        prod_create = await product_option_crud.create_product_option(
            session=session,
            product_id=product_in_bd.id,
            product_option_in_bd=product_option,
            auto_commit=False,
        )
        await session.flush()
        attribute_read_list: List[AttributeReadSchema] = []
        for attribute in product_option.additional_attributes:
            attribute_in_bd = await attribute_crud.get_attr_by_name(
                session=session, attr_name=attribute.name
            )
            if not attribute_in_bd:
                attribute_in_bd = await attribute_crud.create_attr_by_name(
                    session=session, attr_name=attribute.name, auto_commit=False
                )
                await session.flush()
            await category_crud.attach_attribute_if_not_exists(
                session=session,
                category_id=category.id,
                attribute_id=attribute_in_bd.id,
                auto_commit=False,
            )
            await check_on_duplicate_attributes_for_one_option_product(
                session=session, prod_option_id=prod_create.id, attr_id=attribute_in_bd.id
            )
            attr_val_in_bd = await attribute_option_crud.create_attr_and_value_for_option_product(
                session=session,
                prod_option_id=prod_create.id,
                attr_id=attribute_in_bd.id,
                value=attribute.value,
                auto_commit=False,
            )
            attribute_read_list.append(
                AttributeReadSchema(name=attribute_in_bd.name, value=attr_val_in_bd.value)
            )
        optional_read_list.append(
            ProductOptionReadSchema(
                article=product_option.article,
                amount=product_option.amount,
                price=product_option.price,
                attributes=attribute_read_list,
            )
        )
    await session.commit()

    product_read = ProductReadSchema(
        id=product_in_bd.id,
        name=product_in_bd.title,
        description=product_in_bd.description,
        category_name=category.title,
        brand_name=brand.name,
        season=product_in_bd.season,
        options=optional_read_list,
    )
    return product_read


@router.get(
    '/categories/{category_slug}/{product_id}',
    status_code=status.HTTP_200_OK,
    response_model=ProductReadSchema,
)
async def get_product_by_category(
    category_slug: str, product_id: int, session: AsyncSession = Depends(get_async_session)
) -> ProductReadSchema:
    """
    Получить продукт, относящийся к определённой категории.

    Проверяет, что продукт с указанным ID принадлежит категории с заданным slug.
    Если категория или продукт не найдены, возвращает ошибку 404.
    Загружает бренд, варианты продукта и их атрибуты.

    Параметры:
        category_slug (str): Слаг категории.
        product_id (int): Идентификатор продукта.
        session (AsyncSession): Асинхронная сессия базы данных.

    Возвращает:
        ProductReadSchema: Сериализованные данные продукта с вариантами и атрибутами.
    """

    category = await category_crud.get_by_slug(session=session, slug=category_slug, raise_404=True)
    product = await product_crud.get_or_404(session=session, obj_id=product_id)
    await check_product_category_inclusion(
        product_category_id=product.category_id,
        category_id=category.id,  # type: ignore
    )

    brand = await brand_crud.get_or_404(session=session, obj_id=product.brand_id)

    options_in_db = await product_option_crud.get_product_options_with_attributes(
        session=session, product_id=product.id
    )

    option_read_list = []
    for option in options_in_db:
        attributes_in_db = await attribute_option_crud.get_attributes_by_variant_id(
            session=session, variant_id=option.id
        )
        print(attributes_in_db[0].attribute.name)
        attr_read = [
            AttributeReadSchema(name=attr.attribute.name, value=attr.value)
            for attr in attributes_in_db
        ]

        option_read_list.append(
            ProductOptionReadSchema(
                article=option.article,
                amount=option.amount,
                price=option.price,
                attributes=attr_read,
            )
        )

    return ProductReadSchema(
        id=product.id,
        name=product.title,
        description=product.description,
        category_name=category.title,  # type: ignore
        brand_name=brand.name,
        season=product.season,
        options=option_read_list,
    )
