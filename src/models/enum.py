from enum import StrEnum


class OrderStatus(StrEnum):
    """Варианты значения поля статуc в заказах."""

    PROCESSING = 'В обработке'
    PAID = 'Оплачено'
    SHIPPED = 'Отправлене'
    DELIVERED = 'Доставлено'
    CANCELED = 'Отменено'


class DiscountType(StrEnum):
    """Варианты значения поля discount_type в модели скидок."""

    PERCENT = 'Процент'
    FIXED = 'Фиксированная цена'


class PaymentMethod(StrEnum):
    """Варианты значения поля способа оплаты в модели заказов."""

    CARD = 'Картой онлайн'
    SBP = 'По СБП'
    CASH_ON_DELIVERY = 'Наличными при получении'
    CARD_ON_DELIVERY = 'Картой при получении'
