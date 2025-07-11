from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Numeric, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import DefaultValueConstants, PriceConstants
from src.models.base import BoardShopBase
from src.models.enum import OrderStatus, PaymentMethod  # noqa

if TYPE_CHECKING:
    from src.models.enum import OrderStatus, PaymentMethod  # noqa
    from src.models.product import ProductOption
    from src.models.user import User, UserAddress

# TODO Продумать как связать поле с адресом пользователя, логика автозаполнения!


class Order(BoardShopBase):
    """
    Модель заказа пользователя.

    Назначение:
        Хранит информацию о заказе: кому принадлежит, когда был оформлен,
        текущий статус, сумма, способ оплаты и доставки.

    Поля:
        id: Уникальный идентификатор заказа.
        user_id: Внешний ключ к пользователю.
        status: Статус заказа (например, "в обработке", "отправлен").
        total_price: Общая стоимость заказа.
        payment_method: Способ оплаты.
        delivery_address: Адрес доставки.

    Связи:
        user — User;
        items — список OrderItem.
    """

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id', ondelete='SET NULL'), nullable=True
    )
    status: Mapped['OrderStatus'] = mapped_column(
        Enum(OrderStatus, name='orderstatus'), default=OrderStatus.PROCESSING, nullable=False
    )
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(
            PriceConstants.BOARDSHOP_PRICE_NUMBER_OF_DIGITS,
            PriceConstants.BOARDSHOP_PRICE_FRACTIONAL_PART,
        ),
        nullable=False,
    )
    payment_method: Mapped['PaymentMethod'] = mapped_column(
        Enum(PaymentMethod, name='orderstatus'), nullable=True
    )
    delivery_address_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('useraddress.id', ondelete='SET NULL'), nullable=True
    )

    user: Mapped[Optional['User']] = relationship('User', back_populates='orders', lazy='selectin')
    items: Mapped[List['OrderItem']] = relationship(
        'OrderItem', back_populates='order', cascade='all, delete-orphan', lazy='selectin'
    )
    delivery_address: Mapped[Optional['UserAddress']] = relationship('UserAddress', lazy='joined')

    def __repr__(self) -> str:
        return (
            f'<Order(id={self.id}, user_id={self.user_id}, '
            f'status={self.status.name}, total_price={self.total_price})>'
        )


class OrderItem(BoardShopBase):
    """
    Модель товара в заказе.

    Назначение:
        Хранит информацию о каждой товарной позиции, которая входит в заказ,
        включая количество и цену на момент оформления.

    Поля:
        id: Уникальный идентификатор позиции.
        order_id: Внешний ключ к заказу.
        product_option_id: Внешний ключ к конкретному варианту товара.
        quantity: Количество единиц.
        price: Цена за единицу на момент оформления заказа.

    Связи:
        order — Order;
        product_option — ProductOption.
    """

    order_id: Mapped[int] = mapped_column(
        ForeignKey('order.id', ondelete='CASCADE'), nullable=False
    )
    product_option_id: Mapped[int] = mapped_column(
        ForeignKey('productoption.id', ondelete='SET NULL'), nullable=True
    )
    quantity: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=DefaultValueConstants
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(
            PriceConstants.BOARDSHOP_PRICE_NUMBER_OF_DIGITS,
            PriceConstants.BOARDSHOP_PRICE_FRACTIONAL_PART,
        ),
        nullable=False,
    )

    order: Mapped['Order'] = relationship('Order', back_populates='items', lazy='selectin')
    product_option: Mapped[Optional['ProductOption']] = relationship(
        'ProductOption', back_populates='order_items', lazy='selectin'
    )

    def __repr__(self) -> str:
        return (
            f'<OrderItem(id={self.id}, order_id={self.order_id}, '
            f'product_option_id={self.product_option_id}, '
            f'quantity={self.quantity}, price={self.price})>'
        )
