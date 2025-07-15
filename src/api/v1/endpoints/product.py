from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.validators import validate_unique_category_title
from src.core.database.db_depends import get_async_session
from src.crud.crud_product import category_crud
from src.schemas.product import CategoryCreateSchema, CategoryReadSchema

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
