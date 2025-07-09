import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import LengthConstants
from src.models.base import BoardShopBase

if TYPE_CHECKING:
    from src.models.cart import Cart


class User(BoardShopBase):
    """"""

    cart: Mapped['Cart'] = relationship(
        'Cart', back_populates='user', uselist=False, cascade='all, delete-orphan'
    )
    addresses: Mapped[List['UserAddress']] = relationship(
        'UserAddress',
        back_populates='user',
        cascade='all, delete-orphan',
    )


class UserAddress(BoardShopBase):
    """
    Модель адресов пользователя.

    Назначение:
        Хранит адреса доставки, которые пользователь может выбирать при оформлении заказа.

    Поля:
        id: Уникальный идентификатор адреса.
        user_id: Внешний ключ к пользователю.
        address: Текстовое представление адреса доставки.
    """

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
    )
    address: Mapped[str] = mapped_column(
        String(LengthConstants.DELIVERY_ADDRESS_LENGTH), nullable=False
    )

    user: Mapped['User'] = relationship('User', back_populates='addresses')
