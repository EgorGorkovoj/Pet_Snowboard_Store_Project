from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import TextErrorConstants
from src.crud.crud_product import category_crud


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
