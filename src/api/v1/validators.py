from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import TextErrorConstants
from src.crud.crud_attribute import attribute_option_crud
from src.crud.crud_brand import brand_crud
from src.crud.crud_product import category_crud, product_option_crud


async def validate_unique_category_title(
    session: AsyncSession, title_category: str, slug_category: str
) -> None:
    """
    Валидирует уникальность названия и слага категории.

    Назначение:
        Проверяет, существует ли уже категория с указанным названием или слагом.
        Если такая категория найдена, выбрасывает HTTP-исключение 400.

    Аргументы:
        session (AsyncSession): Асинхронная сессия базы данных.
        title_category (str): Название категории.
        slug_category (str): Слаг категории.

    Исключения:
        HTTPException: Если категория с таким названием или слагом уже существует.
    """

    result = await category_crud.get_category_by_title_or_slug(
        session=session, title_category=title_category, slug_category=slug_category
    )

    if result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=TextErrorConstants.FOUND_CATEGORY_BY_ID_OR_SLUG,
        )


async def check_brand_by_exist_of_the_name_in_bd(
    self, session: AsyncSession, brand_name: str
) -> None:
    """
    Проверяет, существует ли бренд с указанным названием в базе данных.

    Если бренд найден, выбрасывает исключение с кодом 404.

    Параметры:
        session (AsyncSession): Асинхронная сессия базы данных.
        brand_name (str): Название бренда для проверки.

    Исключения:
        HTTPException: Статус 404, если бренд с таким названием уже существует.
    """

    result = await brand_crud.get_brand_by_name(session=session, brand_name=brand_name)
    if result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=TextErrorConstants.FOUND_BRAND_BY_NAME.format(brand_title=brand_name),
        )


async def validate_unique_article_product(session: AsyncSession, article: str) -> None:
    """
    Проверяет уникальность артикула варианта товара.

    Если в базе уже существует вариант с таким артикулом — выбрасывается ошибка 400.

    Параметры:
        session (AsyncSession): Сессия базы данных.
        article (str): Артикул варианта товара.

    Исключения:
        HTTPException: Статус 400, если артикул уже существует.
    """

    result = await product_option_crud.get_product_option_by_article(
        session=session, article=article
    )
    if result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=TextErrorConstants.FOUND_ARTICLE.format(article=article),
        )


async def check_on_duplicate_attributes_for_one_option_product(
    session: AsyncSession, prod_option_id: int, attr_id: int
) -> None:
    """
    Проверяет, привязан ли уже указанный атрибут к варианту товара.

    Если у указанного варианта уже есть такой атрибут — выбрасывается ошибка 400.

    Параметры:
        session (AsyncSession): Сессия базы данных.
        prod_option_id (int): ID варианта продукта.
        attr_id (int): ID атрибута (характеристики).

    Исключения:
        HTTPException: Статус 400, если атрибут уже существует у этого варианта.
    """

    result = await attribute_option_crud.get_attr_by_option_product(
        session=session, prod_option_id=prod_option_id, attr_id=attr_id
    )
    if result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=TextErrorConstants.FOUND_ATTR_FOR_OPTION_PRODUCT,
        )


async def check_product_category_inclusion(product_category_id: int, category_id: int) -> None:
    """Проверка что продукт принадлежит к категории"""
    if product_category_id != category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=TextErrorConstants.PRODUCT_NOT_FOUND_IN_CATEGORY,
        )
