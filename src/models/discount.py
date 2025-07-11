from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ARRAY, TIMESTAMP, Boolean, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import DiscountPriceConstants, LengthConstants
from src.models.base import Base, BoardShopBase
from src.models.enum import DiscountType  # noqa

if TYPE_CHECKING:
    from src.models.enum import DiscountType  # noqa
    from src.models.product import Brand, Category, Product


class Discount(BoardShopBase):
    """
    Модель скидки.

    Назначение:
        Описывает скидку, которая может быть применена к товарам, брендам, категориям
        или сезонам. Поддерживает диапазон дат действия.

    Поля:
        name: Название скидки.
        discount_type: Тип скидки (процент или фиксированная сумма).
        value: Значение скидки (в процентах или в валюте, в зависимости от типа).
        active: Активна ли скидка.
        start_date: Дата начала действия скидки.
        end_date: Дата окончания действия скидки.
        seasons: Список сезонов (годов), к которым применяется скидка.

    Связи:
        products — товары, на которые распространяется скидка;
        brands — бренды, к которым применяется скидка;
        categories — категории, на которые действует скидка.
    """

    name: Mapped[str] = mapped_column(String(LengthConstants.TITLE_LENGTH), nullable=False)
    discount_type: Mapped['DiscountType'] = mapped_column(
        Enum(DiscountType, name='discount_type_enum'), nullable=False
    )
    value: Mapped[Decimal] = mapped_column(
        Numeric(
            DiscountPriceConstants.DISCOUNT_PRICE_NUMBER_OF_DIGITS,
            DiscountPriceConstants.DISCOUNT_PRICE_FRACTIONAL_PART,
        ),
        nullable=False,
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(
        type_=TIMESTAMP(timezone=True), nullable=True
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(
        type_=TIMESTAMP(timezone=True), nullable=True
    )
    seasons: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)

    products: Mapped[list['Product']] = relationship(
        secondary='discount_product', back_populates='discounts'
    )
    brands: Mapped[list['Brand']] = relationship(
        secondary='discount_brand', back_populates='discounts'
    )
    categories: Mapped[list['Category']] = relationship(
        secondary='discountcategory', back_populates='discounts'
    )

    def __repr__(self) -> str:
        return f'<Discount(id={self.id}, name="{self.name}", percentage={self.value})>'


class DiscountProduct(Base):
    """
    Промежуточная таблица для связи скидок и продуктов.

    Назначение:
        Обеспечивает many-to-many связь между Discount и Product.

    Поля:
        discount_id: Внешний ключ к Discount.
        product_id: Внешний ключ к Product.
    """

    __tablename__ = 'discount_product'

    discount_id: Mapped[int] = mapped_column(
        ForeignKey('discount.id', ondelete='CASCADE'), primary_key=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey('product.id', ondelete='CASCADE'), primary_key=True
    )


class DiscountBrand(Base):
    """
    Промежуточная таблица для связи скидок и брендов.

    Назначение:
        Обеспечивает many-to-many связь между Discount и Brand.

    Поля:
        discount_id: Внешний ключ к Discount.
        brand_id: Внешний ключ к Brand.
    """

    __tablename__ = 'discount_brand'

    discount_id: Mapped[int] = mapped_column(
        ForeignKey('discount.id', ondelete='CASCADE'), primary_key=True
    )
    brand_id: Mapped[int] = mapped_column(
        ForeignKey('brand.id', ondelete='CASCADE'), primary_key=True
    )


class DiscountCategory(Base):
    """
    Промежуточная таблица для связи скидок и категорий.

    Назначение:
        Обеспечивает many-to-many связь между Discount и Category.

    Поля:
        discount_id: Внешний ключ к Discount.
        category_id: Внешний ключ к Category.
    """

    __tablename__ = 'discount_category'

    discount_id: Mapped[int] = mapped_column(
        ForeignKey('discount.id', ondelete='CASCADE'), primary_key=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey('category.id', ondelete='CASCADE'), primary_key=True
    )
