from typing import List, Optional

from sqlalchemy import ForeignKey, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import LengthConstants
from src.models.base import BoardShopBase


class Category(BoardShopBase):
    """sd"""

    products: Mapped[List['Product']] = relationship(back_populates='category')


class Brand(BoardShopBase):
    """pass"""

    products: Mapped[List['Product']] = relationship(back_populates='brand')


class Product(BoardShopBase):
    """
    Модель всех товаров унаследованная от базового класса 'BoardShopBase'.

    Назначение:
        Хранит сведения о всех товарах магазина и их общих характеристиках.

    Поля:
        id: Идентификационный номер.
        title: Название товара.
        description: Описание товара.
        category_id: Категория товара (внешний ключ к таблице категории).
        brand_id: Торговая марка товара (брэнд).
        model: Модель товара (например: Hardwork 2.0).
        season: К какому сезону относится товар (например: 2023).
        image_url: Ссылка на изображение товара.

    Связи (атрибут - Модель):
        categorys - Category;
        brands - Brand;
        product_variants - ProductVariant.
    """

    title: Mapped[str] = mapped_column(String(LengthConstants.TITLE_LENGTH), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey('category.id', ondelete='SET NULL'), nullable=False
    )
    brand_id: Mapped[str] = mapped_column(ForeignKey('brand.id'), nullable=False)
    model: Mapped[Optional[str]] = mapped_column(
        String(LengthConstants.MODEL_LENGTH), nullable=True
    )
    season: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(
        String(LengthConstants.FILE_LINK_MAX_LENGTH), nullable=True
    )
    category: Mapped['Category'] = relationship(
        'Category', back_populates='products', lazy='selectin'
    )
    brand: Mapped['Brand'] = relationship('Brand', back_populates='products', lazy='selectin')

    def __repr__(self) -> str:
        return self.title
