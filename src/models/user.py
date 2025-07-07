from typing import TYPE_CHECKING

# from sqlalchemy import ForeignKey, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, relationship

# from src.core.constants import LengthConstants
from src.models.base import BoardShopBase

if TYPE_CHECKING:
    from src.models.cart import Cart


class User(BoardShopBase):
    """"""

    cart: Mapped['Cart'] = relationship(
        'Cart', back_populates='user', uselist=False, cascade='all, delete-orphan'
    )


class UserAddress(BoardShopBase):
    """"""

    pass
