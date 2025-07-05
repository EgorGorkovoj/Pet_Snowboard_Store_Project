from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Boolean, ForeignKey, Numeric, SmallInteger, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import LengthConstants, PriceConstants
from src.models.base import BoardShopBase


class Category(BoardShopBase):
    """
    Модель категорий товаров.

    Поля:
        id: Идентификационный номер.
        title: Название товара.
        slug: Короткая строка для пути к эндпоинту.
        subcategory: Подкатегория товаров (внешний ключ к родительской категории).

    Связи (атрибут - Модель):
        parent_category - Category;
        categories - Category;
        products - Product.
    """

    title: Mapped[str] = mapped_column(
        String(LengthConstants.TITLE_LENGTH), nullable=False, unique=True
    )
    slug: Mapped[str] = mapped_column(String(LengthConstants.SLUG), nullable=False, unique=True)
    subcategory: Mapped[Optional[int]] = mapped_column(ForeignKey('category.id'), nullable=True)

    parent_category: Mapped[Optional['Category']] = relationship(
        'Category', back_populates='categories', remote_side=[id]
    )
    categories: Mapped[List['Category']] = relationship(
        'Category', back_populates='parent_category', cascade='all, delete-orphan'
    )
    products: Mapped[List['Product']] = relationship(back_populates='category')


class Brand(BoardShopBase):
    """
    Модель брэнда товара.

    Поля:
        id: Идентификационный номер.
        name: Название брэнда.

    Связи (атрибут - Модель):
        parent_category - Category;
        categories - Category;
        products - Product.
    """

    name: Mapped[str] = mapped_column(
        String(LengthConstants.BRAND_LENGTH), nullable=False, unique=True
    )

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
    brand_id: Mapped[str] = mapped_column(
        ForeignKey('brand.id', ondelete='SET NULL'), nullable=False
    )
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


# TODO: available в докстринге удалить


class ProductOption(BoardShopBase):
    """
    Модель вариантов одного товара.

    Назначение:
        Каждый товар имеет свои характеристики. И в зависимости например от размера и цвета,
        один и тот же товар может иметь свою цену и количество на складе.

    Поля:
        id: Идентификационный номер.
        product_id: Товар (внешний ключ к таблице товаров).
        article: Артикул товара.
        amount: Количество товара.
        available: Доступность товара (если amount > 0 True).
        is_active: Активен ли товар (если False то недоступен на сайте).
        price: Цена товара.

    Связи (атрибут - Модель):
        products - Product;
        atributes - ProductOptionAttribute;
        cart_item - CartItem;
        order_item - OrderItem
    """

    product_id: Mapped['Product'] = mapped_column(
        ForeignKey('product.id', ondelete='CASCADE'), nullable=False
    )
    article: Mapped[str] = mapped_column(
        String(LengthConstants.ARTICLE_LENGTH), unique=True, nullable=False
    )
    amount: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    price: Mapped[Decimal] = mapped_column(
        Numeric(
            PriceConstants.BOARDSHOP_PRICE_NUMBER_OF_DIGITS,
            PriceConstants.BOARDSHOP_PRICE_FRACTIONAL_PART,
        ),
        nullable=False,
    )

    @hybrid_property
    def available(self) -> bool:
        return self.amount > 0

    @available.expression
    def available(cls) -> bool:
        return cls.amount > 0
