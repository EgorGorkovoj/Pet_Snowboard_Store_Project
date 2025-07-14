"""
Базовый модуль констант проекта.

Содержит фундаментальные константы, используемые во всех компонентах системы.
Организован по принципу "контейнеров констант" - классов, группирующих
константы по функциональному назначению.
"""


class LengthConstants:
    """
    Базовый класс констант для ограничения длины символов полей.

    Атрибуты:
    - TITLE_LENGTH (int): Максимальная длина названия товара или категории.
    - MODEL_LENGTH (int): Максимальная длина модели (разновидность внутри бренда) товара.
    - FILE_LINK_MAX_LENGTH (int): Максимальная длина ссылки на изображение товара.
    - MEDIA_TYPE_CONSTANTS (int): Максимальная длина типа медифайла.
    - SLUG (int): Максимальная длина slug категории товара.
    - BRAND_LENGTH (int): Максимальная длина названия бренда товара.
    - ARTICLE_LENGTH (int): Максимальная длина артикула.
    - ATTRIBUTE_LENGTH (int): Максимальная длина названия и значения характеристики товара.
    - DELIVERY_ADDRESS_LENGTH (int): Максимальная длина адреса доставки.
    - NEWSLETTER_MESSAGE_LENGTH (int): Максимальная длина текста сообщения рассылки.
    """

    TITLE_LENGTH: int = 100
    MODEL_LENGTH: int = 50
    FILE_LINK_MAX_LENGTH: int = 2048
    MEDIA_TYPE_CONSTANTS: int = 50
    SLUG: int = 110
    BRAND_LENGTH: int = 100
    ARTICLE_LENGTH: int = 64
    ATTRIBUTE_LENGTH: int = 50
    DELIVERY_ADDRESS_LENGTH: int = 256
    NEWSLETTER_MESSAGE_LENGTH: int = 2000


class DefaultValueConstants:
    """
    Базовый класс констант для значений по умолчанию в БД.

    Атрибуты:
    - CART_ITEM_AMOUNT (int): Количество товара в корзине.
    """

    CART_ITEM_AMOUNT: int = 1


class PriceConstants:
    """
    Базовый класс констант для цен товара.

    Атрибуты:
    - BOARDSHOP_PRICE_NUMBER_OF_DIGITS (int): целая часть цены товара.
    - BOARDSHOP_PRICE_FRACTIONAL_PART (int): сколько знаков после запятой у цены товара.
    """

    BOARDSHOP_PRICE_NUMBER_OF_DIGITS: int = 10
    BOARDSHOP_PRICE_FRACTIONAL_PART: int = 2


class DiscountPriceConstants:
    """
    Базовый класс констант для cкидок на товар.

    Атрибуты:
    - DISCOUNT_PRICE_NUMBER_OF_DIGITS (int): целая часть скидк.
    - DISCOUNT_PRICE_FRACTIONAL_PART (int): сколько знаков после запятой у cкидки.
    """

    DISCOUNT_PRICE_NUMBER_OF_DIGITS: int = 5
    DISCOUNT_PRICE_FRACTIONAL_PART: int = 2


class LoggingBaseConstants:
    """
    Базовый класс констант для хранения параметров логирования приложения.

    Атрибуты:
    - LOG_FILE (str): Путь к основному файлу логов.
    - LOG_RETENTION (str): Срок хранения логов (например '7 days').
    - LOG_ROTATION (str): Периодичность ротации логов (например, '1 day').
    """

    LOG_FILE: str = 'logs/boardshop.log'
    LOG_RETENTION: str = '7 days'
    LOG_ROTATION: str = '1 day'


class TextErrorConstants:
    """
    Базовый класс констант стандартных текстов ошибок.

    Атрибуты:
    - NOT_FOUND_BY_ID (str): Шаблон сообщения об отсутствии объекта по переданному ID.
    - NOT_FOUND_BY_SLUG (str): Шаблон сообщения об отсутствии объекта по переданному slug.
    - CREATE_SERVER_LOG (str): Текст лога ошибки при создании объекта.
    - UPDATE_SERVER_LOG (str): Текст лога ошибки при обновлении объекта.
    - DELETE_SERVER_LOG (str): Текст лога ошибки ошибки при удалении.
    - NOT_FOUND_CATEGORY_BY_ID_OR_SLUG (str): Текст ошибки при получении уже существующего объекта
                                              со slug или категорией.
    """

    NOT_FOUND_BY_ID: str = 'Не найден объект {obj} по данному id: {id}'
    NOT_FOUND_BY_SLUG: str = 'Не найден объект {obj} по данному slug: {slug}'
    CREATE_SERVER_LOG: str = 'Ошибка при создании'
    UPDATE_SERVER_LOG: str = 'Ошибка при обновлении'
    DELETE_SERVER_LOG: str = 'Ошибка при удалении'
    FOUND_CATEGORY_BY_ID_OR_SLUG: str = 'Объект с такой категорией и slug уже существует.'


class TitleConstants:
    """
    Класс констант для хранения заголовков полей.

    Атрибуты:
    - CATEGORY_NAME (str): Загаловок для категории.
    - CATEGORY_SLUG (str): Загаловок для slug категории.
    - PARENT_CATEGORY_NAME (str): Заголовок для родительской категории.

    """

    CATEGORY_NAME: str = 'Название категории'
    CATEGORY_SLUG: str = 'Slug категории'
    PARENT_CATEGORY_NAME: str = 'ID родительской категории'
