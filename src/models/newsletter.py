import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import LengthConstants
from src.models.base import BoardShopBase
from src.models.enum import NotificationChannel

if TYPE_CHECKING:
    from src.models.enum import NotificationChannel  # noqa
    from src.models.user import User

# TODO Нужно в будущем реализовать логику проверки заказов у пользователя


class Newsletter(BoardShopBase):
    """
    Модель подписки пользователя на рассылки (newsletter).

    Назначение:
        Содержит настройки для получения новостей, акций и других рассылок.
        Поддерживает разные каналы доставки (Telegram, email и др.).

    Поля:
        id: Уникальный идентификатор рассылки.
        user_id: Внешний ключ к пользователю.
        is_active: Флаг, включена ли подписка.
        cancel_newslatter: Флаг отключения рассылок пользователем.
        min_orders: Минимальное количество заказов, после которого рассылка активируется.
        media_url: Ссылка на баннер или изображение для рассылки.
        message_text: Текст сообщения рассылки.
        channel: Канал доставки (например, telegram, email).
    """

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cancel_newslatter: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    min_orders: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    media_url: Mapped[Optional[str]] = mapped_column(
        String(LengthConstants.FILE_LINK_MAX_LENGTH), nullable=True
    )
    message_text: Mapped[str] = mapped_column(
        String(LengthConstants.NEWSLETTER_MESSAGE_LENGTH), nullable=False
    )
    channel: Mapped['NotificationChannel'] = mapped_column(
        Enum(NotificationChannel), nullable=False
    )

    user: Mapped['User'] = relationship('User', back_populates='newsletters')

    def __repr__(self) -> str:
        return (
            f'<Newsletter(user_id={self.user_id}, '
            f'active={self.is_active}, channel="{self.channel}")>'
        )
