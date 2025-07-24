from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.core.constants import LengthConstants, TitleConstants
from src.schemas.attribute import AttributeReadSchema


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


class ProductOptionAttributeCreate(BaseModel):
    """
    Схема создания одного атрибута варианта продукта.

    Назначение:
        Используется при создании опций товара,
        чтобы задать дополнительные характеристики (например, цвет, жесткость и т.д.).

    Поля:
        name: Название характеристики (атрибута).
        value: Значение для указанной характеристики.
    """

    name: str = Field(
        ..., max_length=LengthConstants.ATTRIBUTE_LENGTH, title=TitleConstants.ATTRIBUTE_NAME
    )
    value: str = Field(
        ..., max_length=LengthConstants.ATTRIBUTE_LENGTH, title=TitleConstants.ATTRIBUTE_VALUE
    )


class ProductOptionCreate(BaseModel):
    """
    Схема создания одного варинта товара.

    Назначение:
        Представляет один вариант товара, отличающийся, например,
        артикулом, ценой, характеристиками.

    Поля:
        article: Уникальный артикул товара.
        amount: Количество единиц на складе.
        price: Цена варианта товара.
        additional_attributes: Список дополнительных атрибутыов (например: цвет, ростовка).
    """

    article: str = Field(
        ..., max_length=LengthConstants.ARTICLE_LENGTH, title=TitleConstants.ARTICLE_TITLE
    )
    amount: int = Field(..., title=TitleConstants.AMOUNT_TITLE)
    price: Decimal = Field(..., title=TitleConstants.PRICE_TITLE)
    additional_attributes: List[ProductOptionAttributeCreate]

    @model_validator(mode='after')
    def check_duplicate_attribute_names(self) -> 'ProductOptionCreate':
        """
        Валидатор для проверки уникальности названий атрибутов.
        """
        repeat = set()
        for attr in self.additional_attributes:
            if attr.name.lower() in repeat:
                raise ValueError(f'Атрибут с названием "{attr.name}" указан несколько раз.')
            repeat.add(attr.name.lower())
        return self


class ProductCreateSchema(BaseModel):
    """
    Схема создания основного товара.

    Назначение:
        Используется для создания товара вместе с одной или несколькими опциями (вариантами).

    Поля:
        title: Название товара.
        description: Описание товара (опционально).
        category_id: ID категории, к которой принадлежит товар.
        brand_name: Название бренда товара. Если бренд отсутствует, он будет создан.
        model: Название модели (опционально).
        season: Сезон (например, 2024).
        product_options: Список опций (вариантов) товара.
    """

    title: str = Field(
        ..., max_length=LengthConstants.TITLE_LENGTH, title=TitleConstants.PRODUCT_TITLE
    )
    description: Optional[str] = Field(
        None,
        max_length=LengthConstants.DESCRIPTION_LENGTH,
        title=TitleConstants.PRODUCT_DESCRIPTION,
    )
    category_id: int = Field(..., title=TitleConstants.PRODUCT_CATEGORY)
    brand_name: str = Field(
        ..., max_length=LengthConstants.BRAND_LENGTH, title=TitleConstants.PRODUCT_BRAND
    )
    model: Optional[str] = Field(
        None, max_length=LengthConstants.MODEL_LENGTH, title=TitleConstants.PRODUCT_MODEL
    )
    season: int = Field(..., title=TitleConstants.PRODUCT_SEASON)
    product_options: List[ProductOptionCreate]


class ProductOptionReadSchema(BaseModel):
    """
    Схема для отображения варианта товара.

    Поля:
        article: Артикул варианта товара.
        amount: Количество на складе.
        price: Цена.
        attributes: Список характеристик варианта товара.
    """

    article: str
    amount: int
    price: Decimal
    attributes: List[AttributeReadSchema]


class ProductReadSchema(BaseModel):
    """
    Схема для отображения основного товара и его опций.

    Назначение:
        Используется как ответная модель после создания товара или при запросе информации о нем.

    Поля:
        id: Уникальный идентификатор товара.
        name: Название товара.
        description: Описание товара.
        category_name: Название категории, к которой относится товар.
        brand_name: Название бренда.
        season: Сезон.
        options: Список всех доступных вариантов (опций) товара.
    """

    id: int
    name: str
    description: Optional[str] = None
    category_name: str
    brand_name: str
    season: Optional[int] = None
    options: List[ProductOptionReadSchema]
