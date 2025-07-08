from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Numeric, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import DefaultValueConstants, PriceConstants
from src.models.base import BoardShopBase

if TYPE_CHECKING:
    from src.models.product import ProductOption
    from src.models.user import User


class Cart(BoardShopBase):
    """
    Модель корзины пользователя.

    Назначение:
        Представляет текущую корзину покупок, связанную с конкретным пользователем.

    Поля:
        id: Идентификатор корзины.
        user_id: Внешний ключ на пользователя (у каждого пользователя только одна корзина).

    Связи (атрибут - Модель):
        user — User;
        cart_items — CartItem (список товаров в корзине).
    """

    user_id: Mapped[int] = mapped_column(ForeignKey('user.uuid', ondelete='CASCADE'), unique=True)

    user: Mapped['User'] = relationship('User', back_populates='cart', lazy='joined')
    cart_items: Mapped[List['CartItem']] = relationship(
        'CartItem', back_populates='cart', cascade='all, delete-orphan', lazy='selectin'
    )

    @property
    def total_price(self) -> Decimal:
        """
        Вычисляет общую стоимость всех товаров в корзине.
        Возвращает сумму произведений цены и количества каждого элемента корзины.
        Использует зафиксированную цену из CartItem, чтобы избежать рассинхронизации
        при изменении цен в товаре после добавления в корзину.

        Возвращаемое значение:
            Decimal: Общая сумма корзины с учётом количества каждого товара.
        """
        return sum((item.price * item.quantity for item in self.cart_items), Decimal('0'))


class CartItem(BoardShopBase):
    """
    Модель позиции товара в корзине.

    Назначение:
        Хранит информацию о конкретном товаре, добавленном пользователем в корзину,
        включая количество и цену на момент добавления.

    Поля:
        id: Идентификатор.
        cart_id: ID корзины.
        product_option_id: ID варианта товара.
        quantity: Количество товара в корзине.
        price: Цена на момент добавления в корзину.

    Связи:
        cart — Cart;
        product_option — ProductOption.
    """

    cart_id: Mapped[int] = mapped_column(ForeignKey('cart.id', ondelete='CASCADE'), nullable=False)
    product_option_id: Mapped[int] = mapped_column(
        ForeignKey('productoption.id', ondelete='CASCADE'), nullable=False
    )
    quantity: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=DefaultValueConstants.CART_ITEM_AMOUNT
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(
            PriceConstants.BOARDSHOP_PRICE_NUMBER_OF_DIGITS,
            PriceConstants.BOARDSHOP_PRICE_FRACTIONAL_PART,
        ),
        nullable=False,
    )

    cart: Mapped['Cart'] = relationship('Cart', back_populates='cart_items', lazy='selectin')
    product_option: Mapped['ProductOption'] = relationship(
        'ProductOption', back_populates='cart_items', lazy='selectin'
    )
