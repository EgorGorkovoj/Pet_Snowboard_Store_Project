from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.core.constants import LengthConstants, TitleConstants


class CategoryCreateSchema(BaseModel):
    """
    Схема для создания новой категории.

    Поля:
        title: Название категории (обязательное поле, ограничено по длине).
        slug: Уникальный URL-идентификатор категории
              (обязательное поле, используется для адресов).
        parent_category_id: ID родительской категории, если есть.
    """

    title: str = Field(
        ..., max_length=LengthConstants.TITLE_LENGTH, title=TitleConstants.CATEGORY_NAME
    )
    slug: str = Field(..., max_length=LengthConstants.SLUG, title=TitleConstants.CATEGORY_SLUG)
    parent_category_id: int | None = Field(
        default=None, title=TitleConstants.PARENT_CATEGORY_NAME, examples=[None]
    )


class CategoryReadSchema(BaseModel):
    """
    Схема для чтения (отображения) категории.

    Поля:
        id: Уникальный идентификатор категории.
        title: Название категории.
        slug: URL-идентификатор категории.
        parent_category_id: Родитетельская категория.
    """

    id: int
    title: str
    slug: str
    parent_category_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
