from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, ForeignKey, Numeric, SmallInteger, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import LengthConstants, PriceConstants
from src.models.base import BoardShopBase

if TYPE_CHECKING:
    from src.models.attribute import CategoryAttribute, ProductOptionAttribute
    from src.models.cart import CartItem
    from src.models.discount import Discount
    from src.models.media import Media
    from src.models.order import OrderItem


class Category(BoardShopBase):
    """
    Модель категорий товаров.

    Поля:
        id: Идентификационный номер.
        title: Название категории.
        slug: Короткая строка для пути к эндпоинту.
        subcategory: Подкатегория товаров (внешний ключ к родительской категории).

    Связи (атрибут - Модель):
        parent_category - Category;
        categories - Category;
        products - Product;
        category_attributes - CategoryAttribute;
        discounts - Discount.
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
        'Category', back_populates='parent_category', cascade='all, delete-orphan', lazy='selectin'
    )
    products: Mapped[List['Product']] = relationship(back_populates='category', lazy='selectin')
    category_attributes: Mapped[List['CategoryAttribute']] = relationship(
        'CategoryAttribute', back_populates='category', lazy='selectin'
    )
    discounts: Mapped[list['Discount']] = relationship(
        secondary='discount_category', back_populates='categories'
    )

    def __repr__(self) -> str:
        return f'<Category(id={self.id}, name="{self.title}")>'


class Brand(BoardShopBase):
    """
    Модель брэнда товара.

    Поля:
        id: Идентификационный номер.
        name: Название брэнда.

    Связи (атрибут - Модель):
        products - Product.
        discounts - Discount.
    """

    name: Mapped[str] = mapped_column(
        String(LengthConstants.BRAND_LENGTH), nullable=False, unique=True
    )

    products: Mapped[List['Product']] = relationship(back_populates='brand')

    discounts: Mapped[list['Discount']] = relationship(
        secondary='discount_brand', back_populates='brands'
    )

    def __repr__(self) -> str:
        return f'<Brand(id={self.id}, name="{self.name}")>'


class Product(BoardShopBase):
    """
    Модель товара магазина.

    Назначение:
        Хранит сведения о всех товарах магазина и их общих характеристиках.

    Поля:
        id: Идентификационный номер.
        title: Название товара.
        description: Описание товара.
        category_id: Категория товара (внешний ключ к таблице категории).
        brand_id: Торговая марка товара (брэнд).
        model: Модель товара (например: Magnum 2.0).
        season: К какому сезону относится товар (например: 2023).

    Связи (атрибут - Модель):
        category - Category;
        brand - Brand;
        product_options - ProductOption;
        discounts - Discount;
        media - Media.
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
    category: Mapped['Category'] = relationship(
        'Category', back_populates='products', lazy='selectin'
    )

    brand: Mapped['Brand'] = relationship('Brand', back_populates='products', lazy='selectin')
    product_options: Mapped[List['ProductOption']] = relationship(
        'ProductOption', back_populates='product', cascade='all, delete-orphan'
    )
    discounts: Mapped[list['Discount']] = relationship(
        secondary='discount_product', back_populates='products'
    )
    media: Mapped[List['Media']] = relationship(
        'Media', back_populates='product', cascade='all, delete-orphan', lazy='selectin'
    )

    def __repr__(self) -> str:
        return f'<Product(id={self.id}, title="{self.title}")>'


class ProductOption(BoardShopBase):
    """
    Модель вариантов одного товара.

    Назначение:
        Представляет конкретную модификацию товара (например, сноуборд 158 см, черный).
        У каждого варианта может быть свой артикул, цена и количество на складе.

    Поля:
        id: Идентификационный номер.
        product_id: Товар (внешний ключ к таблице товаров).
        article: Артикул товара.
        amount: Количество товара.
        available: Доступность товара (если amount > 0 True).
        is_active: Активен ли товар (если False то недоступен на сайте).
        price: Цена товара.

    Вычисляемые свойства:
        available: Вычисляется автоматически (если amount > 0). Не сохраняется в БД.

    Связи (атрибут - Модель):
        product - Product;
        attributes - ProductOptionAttribute;
        cart_items - CartItem;
        order_items - OrderItem
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

    product: Mapped['Product'] = relationship(
        'Product', back_populates='product_options', lazy='joined'
    )
    attributes: Mapped[List['ProductOptionAttribute']] = relationship(
        'ProductOptionAttribute',
        back_populates='product_option',
        cascade='all, delete-orphan',
        lazy='selectin',
    )
    cart_items: Mapped[List['CartItem']] = relationship(
        'CartItem', back_populates='product_option', cascade='all, delete-orphan', lazy='selectin'
    )
    order_items: Mapped[List['OrderItem']] = relationship(
        'OrderItem', back_populates='product_option', lazy='selectin'
    )

    @hybrid_property
    def available(self) -> bool:
        return self.amount > 0

    @available.expression
    def available(cls) -> bool:
        return cls.amount > 0

    def __repr__(self) -> str:
        return (
            f'<ProductOption(id={self.id}, product_id={self.product_id}, '
            f'article="{self.article}", amount={self.amount}, price={self.price})>'
        )
