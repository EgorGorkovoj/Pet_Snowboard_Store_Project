from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import LengthConstants
from src.models.base import BoardShopBase

if TYPE_CHECKING:
    from src.models.product import Category, ProductOption


class Attribute(BoardShopBase):
    """
    Модель характеристик(атрибутов) товара.

    Назначение:
        Содержит только название характеристики, без значений, для возможности расширения.

    Поля:
        id: Идентификационный номер.
        name: Название характеристики (атрибута).

    Связи (атрибут - Модель):
        product_option_attr - ProductOptionAttribute;
        category_attributes - CategoryAttribute.
    """

    name: Mapped[str] = mapped_column(
        String(LengthConstants.ATTRIBUTE_LENGTH), nullable=False, unique=True
    )

    product_option_attr: Mapped[List['ProductOptionAttribute']] = relationship(
        'ProductOptionAttribute', back_populates='attribute', lazy='selectin'
    )
    category_attributes: Mapped[List['CategoryAttribute']] = relationship(
        'CategoryAttribute', back_populates='attribute', lazy='selectin'
    )


class ProductOptionAttribute(BoardShopBase):
    """
    Модель характеристик определенного товара.

    Назначение:
        Это промежуточная модель (Many-To-Many) для связи различных
        характеристик(атрибутов) с разными товарами одной модели.

    Поля:
        id: Идентификационный номер.
        variant_id: Вариант товара (Внешний ключ).
        attribute_id: Характеристика товара (Внешний ключ).

    Связи (атрибут - Модель):
        product_option - ProductOption;
        attribute - Attribute.
    """

    variant_id: Mapped[int] = mapped_column(
        ForeignKey('productoption.id', ondelete='CASCADE'), nullable=False
    )
    attribute_id: Mapped[int] = mapped_column(
        ForeignKey('attribute.id', ondelete='CASCADE'), nullable=False
    )
    value: Mapped[str] = mapped_column(String(LengthConstants.ATTRIBUTE_LENGTH), nullable=False)

    product_option: Mapped['ProductOption'] = relationship(
        'ProductOption', back_populates='attributes', lazy='selectin'
    )
    attribute: Mapped['Attribute'] = relationship(
        'Attribute', back_populates='product_option_attr', lazy='selectin'
    )


class CategoryAttribute(BoardShopBase):
    """
    Модель характеристик привязанных к категории товара.

    Назначение:
        Это промежуточная модель (Many-To-Many) для связи различных
        характеристик(атрибутов) с категориями товаров. Служит для
        упрощения получения всех характеристик.

    Поля:
        id: Идентификационный номер.
        category_id: Категория товара (Внешний ключ).
        attribute_id: Характеристика товара (Внешний ключ).

    Связи (атрибут - Модель):
        category - Category;
        attributes - Attribute.
    """

    category_id: Mapped[int] = mapped_column(
        ForeignKey('category.id', ondelete='CASCADE'), nullable=False
    )
    attribute_id: Mapped[int] = mapped_column(
        ForeignKey('attribute.id', ondelete='SETNULL'), nullable=False
    )

    category: Mapped['Category'] = relationship(
        'Category', back_populates='category_attributes', lazy='selectin'
    )
    attribute: Mapped['Attribute'] = relationship(
        'Attribute', back_populates='category_attributes', lazy='selectin'
    )
