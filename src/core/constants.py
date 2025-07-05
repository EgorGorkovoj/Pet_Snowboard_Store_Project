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
    - TITLE_LENGTH (int): Максимальная длина названия товара.
    - MODEL_LENGTH (int): Максимальная длина модели (разновидность внутри бренда) товара.
    - FILE_LINK_MAX_LENGTH (int): Максимальная длина ссылки на изображение товара.
    - SLUG (int): Максимальная длина slug товара.
    - BRAND_LENGTH (int): Максимальная длина названия бренда товара.
    - ARTICLE_LENGTH (int): Максимальная длина артикула.
    """

    TITLE_LENGTH: int = 100
    MODEL_LENGTH: int = 50
    FILE_LINK_MAX_LENGTH: int = 2048
    SLUG: int = 110
    BRAND_LENGTH = 100
    ARTICLE_LENGTH = 64


# class DefaultValueConstants:
#     """
#     Базовый класс констант для значений по умолчанию в БД.

#     Атрибуты:
#     - PRODUCT_AMOUNT (int): Количество определенного товара (по умолчанию).
#     """

#     PRODUCT_AMOUNT: int = 0


class PriceConstants:
    """
    Базовый класс констант для цен товара.

    Атрибуты:
    - BOARDSHOP_PRICE_NUMBER_OF_DIGITS (int): целая часть цены товара.
    - BOARDSHOP_PRICE_FRACTIONAL_PART (int): сколько знаков после запятой у цены товара.
    """

    BOARDSHOP_PRICE_NUMBER_OF_DIGITS: int = 10
    BOARDSHOP_PRICE_FRACTIONAL_PART: int = 2


class LoggingBaseConstants:
    """
    Базовый класс констант для хранения параметров логирования приложения.

    Атрибуты:
    - LOG_FILE (str): Путь к основному файлу логов.
    - LOG_RETENTION (str): Срок хранения логов (например '7 days').
    - LOG_ROTATION (str): Периодичность ротации логов (например, '1 day').
    """

    LOG_FILE: str = 'logs/tabit.log'
    LOG_RETENTION: str = '7 days'
    LOG_ROTATION: str = '1 day'
