from enum import StrEnum


class OrderStatus(StrEnum):
    """Варианты значения поля стату в заказах."""

    PROCESSING = 'В обработке'
    PAID = 'Оплачено'
    SHIPPED = 'Отправлене'
    DELIVERED = 'Доставлено'
    CANCELED = 'Отменено'
