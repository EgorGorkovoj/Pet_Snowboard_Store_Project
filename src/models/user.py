import uuid
from datetime import date
from typing import TYPE_CHECKING, List

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import LengthConstants
from src.models.base import BoardShopBase

if TYPE_CHECKING:
    from src.models.cart import Cart
    from src.models.newsletter import Newsletter
    from src.models.order import Order


class User(BoardShopBase, SQLAlchemyBaseUserTableUUID):  # type: ignore[misc]
    """
    Модель пользователя интернет-магазина сноубордов.

    Наследование:
        - BoardShopBase: базовый класс моделей проекта.
        - SQLAlchemyBaseUserTableUUID: базовая модель пользователя с UUID в качестве PK.

    Назначение:
        Хранит учётные данные, личную информацию и связи пользователя с другими сущностями
        (корзина, заказы, адреса и т.д.).

    Атрибуты:
        telegram_id (int | None):
            Уникальный идентификатор пользователя в Telegram.
            Хранится как BigInteger.
            Не допускает NULL.
        email (str | None):
            Адрес электронной почты пользователя.
            Уникален, может быть NULL.
        hashed_password (str | None):
            Хэшированный пароль пользователя.
            Может быть NULL (например, если авторизация только через Telegram).
        name (str):
            Полное имя пользователя.
            Не допускает NULL.
        surname(str | None):
            Фамилия пользователя.
        nickname (str | None):
            Уникальный никнейм пользователя.
            Может быть NULL.
        birth_date (date | None):
            Дата рождения пользователя.
            Может быть NULL.
        phone_number (str | None):
            Уникальный номер телефона.
            Может быть NULL.
        is_admin (bool):
            Флаг, обозначающий права администратора.
            По умолчанию False.
        is_verified (bool):
            Флаг, подтверждающий верификацию пользователя.
            По умолчанию True, не допускает NULL.

    Связи:
        cart (Cart):
            Связь один-к-одному с корзиной пользователя.
            Автоматически удаляется при удалении пользователя.
        orders (List[Order]):
            Список заказов пользователя.
        addresses (List[UserAddress]):
            Список адресов пользователя.
            Автоматически удаляются при удалении пользователя.
        newsletters (List[Newsletter]):
            Список подписок пользователя на рассылки.

    __table_args__:
        extend_existing=True — разрешает переопределение уже существующей таблицы
        (например, при миграциях или автогенерации).
    """

    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)  # type: ignore
    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)  # type: ignore
    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[str | None] = mapped_column(String, nullable=True)
    nickname: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # type: ignore

    cart: Mapped['Cart'] = relationship(
        'Cart', back_populates='user', uselist=False, cascade='all, delete-orphan'
    )
    orders: Mapped[List['Order']] = relationship('Order', back_populates='user')
    addresses: Mapped[List['UserAddress']] = relationship(
        'UserAddress',
        back_populates='user',
        cascade='all, delete-orphan',
    )
    newsletters: Mapped[List['Newsletter']] = relationship('Newsletter', back_populates='user')

    __table_args__ = {'extend_existing': True}


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

    def __repr__(self) -> str:
        return f'<UserAddress(id={self.id}, user_id={self.user_id}, address="{self.address}")>'
