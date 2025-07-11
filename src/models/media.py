from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import LengthConstants
from src.models.base import BoardShopBase
from src.models.enum import MediaTypeEnum

if TYPE_CHECKING:
    from src.models.enum import MediaTypeEnum  # noqa
    from src.models.product import Product


class Media(BoardShopBase):
    """
    Модель медиа-файлов, связанных с товарами.

    Назначение:
        Хранит ссылки на изображения, видео и другие медиафайлы,
        относящиеся к конкретному товару.

    Поля:
        id: Уникальный идентификатор записи.
        file_url: Ссылка на файл, хранящийся на сервере или внешнем хранилище.
        media_type: Тип медиафайла (например: 'image', 'video').
        is_primary: Флаг, указывающий, является ли данное медиа основным для отображения товара.
        product_id: Внешний ключ на модель товара.

    Связи (атрибут - Модель):
        product - Product.
    """

    file_url: Mapped[str] = mapped_column(
        String(LengthConstants.FILE_LINK_MAX_LENGTH), nullable=False
    )
    media_type: Mapped['MediaTypeEnum'] = mapped_column(
        Enum(MediaTypeEnum, name='media_type_enum'), nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    product_id: Mapped[int] = mapped_column(
        ForeignKey('product.id', ondelete='CASCADE'), nullable=False
    )

    product: Mapped['Product'] = relationship('Product', back_populates='media', lazy='selectin')

    def __repr__(self) -> str:
        return (
            f'<Media(id={self.id}, type="{self.media_type}", '
            f'is_primary={self.is_primary}, product_id={self.product_id})>'
        )
