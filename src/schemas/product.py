from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.core.constants import LengthConstants, TitleConstants
from src.schemas.attribute import AttributeReadSchema


class ProductBaseReadSchema(BaseModel):
    """
    Схема для отображения основного товара и его опций.

    Назначение:
        Используется для краткого отображения информации о товаре.
        Например используется в отображение списка товаров.

    Поля:
        id: Уникальный идентификатор товара.
        name: Название товара.
        description: Описание товара.
        brand_name: Название бренда.
        season: Сезон.
    """

    id: int
    title: str
    category_name: str
    description: Optional[str] = None
    brand_name: str
    season: Optional[int] = None


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

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


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
    amount: int = Field(..., ge=0, title=TitleConstants.AMOUNT_TITLE)
    price: Decimal = Field(..., ge=0, title=TitleConstants.PRICE_TITLE)
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

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


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

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class ProductOptionAttributeUpdateSchema(BaseModel):
    """
    Схема обновления отдельного атрибута варианта товара.

    Назначение:
        Используется для изменения значения конкретной характеристики (атрибута)
        варианта товара, например, цвета, размера, материала.

    Поля:
        name (Optional[str]): Имя атрибута (например, "Цвет").
        value (Optional[str]): Значение атрибута (например, "Красный").
    Ограничения:
        - Лишние пробелы в начале и конце будут удалены (str_strip_whitespace=True).
        - Нельзя передавать поля, которых нет в схеме (extra='forbid').
    """

    name: Optional[str] = Field(
        None, max_length=LengthConstants.ATTRIBUTE_LENGTH, title=TitleConstants.ATTRIBUTE_NAME
    )
    value: Optional[str] = Field(
        None, max_length=LengthConstants.ATTRIBUTE_LENGTH, title=TitleConstants.ATTRIBUTE_VALUE
    )

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class ProductOptionUpdateSchema(BaseModel):
    """
    Схема обновления варианта товара.

    Назначение:
        Применяется при частичном или полном обновлении информации о конкретном варианте товара
        (артикул, цена, количество, набор характеристик).

    Поля:
        article (Optional[str]): Артикул варианта товара (уникальный код, заданный магазином).
        amount (Optional[int]): Количество товара на складе. Должно быть ≥ 0.
        price (Optional[Decimal]): Цена варианта товара. Должна быть ≥ 0.
        attributes (Optional[List[ProductOptionAttributeUpdateSchema]]):
            Список обновляемых атрибутов варианта товара.
            Каждый элемент списка описывается схемой ProductOptionAttributeUpdateSchema.

    Валидаторы:
        check_unique_attribute_names:
            Проверяет, что в списке attributes нет дубликатов по имени атрибута.

    Ограничения:
        - Лишние пробелы в строковых полях будут удалены (str_strip_whitespace=True).
        - Нельзя передавать поля, которых нет в схеме (extra='forbid').
    """

    article: Optional[str] = Field(
        None, max_length=LengthConstants.ARTICLE_LENGTH, title=TitleConstants.ARTICLE_TITLE
    )
    amount: Optional[int] = Field(None, ge=0, title=TitleConstants.AMOUNT_TITLE)
    price: Optional[Decimal] = Field(None, ge=0, title=TitleConstants.PRICE_TITLE)
    attributes: Optional[List[ProductOptionAttributeUpdateSchema]] = None

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

    @field_validator('attributes')
    def check_unique_attribute_names(cls, attributes):
        if attributes is None:
            return attributes
        names = [attr.name for attr in attributes]
        if len(names) != len(set(names)):
            raise ValueError('Атрибуты содержат дубликаты по имени')
        return attributes


class ProductUpdateSchema(BaseModel):
    """
    Схема обновления основного товара.

    Назначение:
        Используется при частичном или полном обновлении общей информации о товаре
        (название, описание, категория, бренд, модель, сезон).
        Не предназначена для изменения вариантов товара или их характеристик.

    Поля:
        title (Optional[str]): Название товара.
        description (Optional[str]): Описание товара.
        category_id (Optional[int]): Идентификатор категории, к которой относится товар.
        brand_name (Optional[str]): Название бренда товара.
        model (Optional[str]): Модель товара.
        season (Optional[int]): Сезон использования (год).

    Ограничения:
        - Лишние пробелы в строковых полях будут удалены (str_strip_whitespace=True).
        - Нельзя передавать поля, которых нет в схеме (extra='forbid').
    """

    title: Optional[str] = Field(
        None, max_length=LengthConstants.TITLE_LENGTH, title=TitleConstants.PRODUCT_TITLE
    )
    description: Optional[str] = Field(
        None,
        max_length=LengthConstants.DESCRIPTION_LENGTH,
        title=TitleConstants.PRODUCT_DESCRIPTION,
    )
    category_id: Optional[int] = Field(None, title=TitleConstants.PRODUCT_CATEGORY)
    brand_name: Optional[str] = Field(
        None, max_length=LengthConstants.BRAND_LENGTH, title=TitleConstants.PRODUCT_BRAND
    )
    model: Optional[str] = Field(
        None, max_length=LengthConstants.MODEL_LENGTH, title=TitleConstants.PRODUCT_MODEL
    )
    season: Optional[int] = Field(None, title=TitleConstants.PRODUCT_SEASON)

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class ProductOptionReadSchema(BaseModel):
    """
    Схема для отображения варианта товара.

    Поля:
        article: Артикул варианта товара.
        amount: Количество на складе.
        price: Цена.
        attributes: Список характеристик варианта товара.
    """

    id: int
    article: str
    amount: int
    price: Decimal
    attributes: List[AttributeReadSchema]


class ProductReadSchema(ProductBaseReadSchema):
    """
    Схема для подробного отображения основного товара и его вариантами.

    Назначение:
        Используется как ответная модель после создания товара или при запросе информации о нем.

    Поля:
        category_name: Название категории, к которой относится товар.
        options: Список всех доступных вариантов (опций) товара.

    Примечание:
        Поля id, name, description, brand_name, season наследуются от ProductBaseReadSchems.
    """

    category_name: str
    options: List[ProductOptionReadSchema]


class ProductDetailReadSchema(ProductOptionReadSchema, ProductBaseReadSchema):
    """
    Схема для отображения детальной информации о товаре.

    Наследует:
        - ProductOptionReadSchema: включает данные о вариантах товара и их атрибутах.
        - ProductBaseReadSchems: включает базовую информацию о товаре.

    Дополнительно:
        - category_name (str): Название категории, к которой относится товар.
    """

    category_name: str
