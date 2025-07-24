"""
Базовый модуль констант проекта.

Содержит фундаментальные константы, используемые во всех компонентах системы.
Организован по принципу "контейнеров констант" - классов, группирующих
константы по функциональному назначению.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MiscBaseConstants:
    """
    Базовый класс разных общесистемных констант.

    Класс реализован, как неизменяемый (frozen=True).

    Атрибуты:
    - BASE_DIR (Path): Корневая директория проекта.
    """

    BASE_DIR: Path = Path(__file__).resolve().parents[2]


class DirectoryBaseConstants:
    """
    Базовый класс констант путей к директориям.

    Атрибуты:
    - MEDIA (str): Название директории для медиафайлов.
    """

    MEDIA: str = 'media'


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
    - DESCRIPTION_LENGTH (int): Максимальная длина текста описания товара.
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
    DESCRIPTION_LENGTH: int = 2000


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
    - FOUND_CATEGORY_BY_ID_OR_SLUG (str): Текст ошибки при получении уже существующего объекта
                                              со slug или категорией.
    - MAIN_CATEGORY_NOT_FOUND (str): Текст ошибки при отсутствии основых категорий.
    - PARENT_CATEGORY_NOT_FOUND (str): Текст ошибки при отсутствии родительской категорий.
    - FOUND_BRAND_BY_NAME (str): Текст ошибки, что такой брэнд уже сущетсвует.
    - FOUND_ATTR_FOR_OPTION_PRODUCT (str): Текст ошибки, что такая характеристика
                                           для варианта товара уже сущетсвует.
    """

    NOT_FOUND_BY_ID: str = 'Не найден объект {obj} по данному id: {id}'
    NOT_FOUND_BY_SLUG: str = 'Не найден объект {obj} по данному slug: {slug}'
    CREATE_SERVER_LOG: str = 'Ошибка при создании'
    UPDATE_SERVER_LOG: str = 'Ошибка при обновлении'
    DELETE_SERVER_LOG: str = 'Ошибка при удалении'
    FOUND_CATEGORY_BY_ID_OR_SLUG: str = 'Объект с такой категорией и slug уже существует.'
    MAIN_CATEGORY_NOT_FOUND: str = 'Главные категории не найдены.'
    PARENT_CATEGORY_NOT_FOUND: str = 'Родительская категория "{parent_title}" не найдена.'
    FOUND_BRAND_BY_NAME: str = 'Брэнд "{brand_title}" уже существует.'
    FOUND_ARTICLE: str = 'Артикул "{article}" уже существует.'
    FOUND_ATTR_FOR_OPTION_PRODUCT: str = 'Для данного товара такая характеристика уже существуют'


class TitleConstants:
    """
    Класс констант для хранения заголовков полей.

    Атрибуты:
    - CATEGORY_NAME (str): Загаловок для категории.
    - CATEGORY_SLUG (str): Загаловок для slug категории.
    - PARENT_CATEGORY_NAME (str): Заголовок для родительской категории.
    - PRODUCT_TITLE (str): Загаловок для товара.
    - PRODUCT_DESCRIPTION (str): Загаловок для описания товара.
    - PRODUCT_CATEGORY (str): Заголовок для Id категории к которой принадлежит товар.
    - PRODUCT_BRAND (str): Загаловок для брэнда товара.
    - PRODUCT_MODEL (str): Загаловок модели товара.
    - PRODUCT_SEASON (str): Заголовок сезона товара.
    - ATTRIBUTE_NAME (str): Заголовок для названия характеристики товара (используется в схеме).
    - ATTRIBUTE_VALUE (str): Заголовок для значения характеристики товара (используется в схеме).
    - ARTICLE_TITLE (str): Заголовок артикула товара (используется в схеме).
    - AMOUNT_TITLE (str): Заголовок количества товара (используется в схеме).
    - PRICE_TITLE (str): Заголовок цены товара (используется в схеме).
    """

    CATEGORY_NAME: str = 'Название категории'
    CATEGORY_SLUG: str = 'Slug категории'
    PARENT_CATEGORY_NAME: str = 'ID родительской категории'
    PRODUCT_TITLE: str = 'Название товара'
    PRODUCT_DESCRIPTION: str = 'Описание товара'
    PRODUCT_CATEGORY: str = 'ID категории товара'
    PRODUCT_BRAND: str = 'Брэнд товара'
    PRODUCT_MODEL: str = 'Модель товара'
    PRODUCT_SEASON: str = 'Сезон'
    ATTRIBUTE_NAME: str = 'Название атрибута (характеристики) '
    ATTRIBUTE_VALUE: str = 'Значение атрибута (характеристики)'
    ARTICLE_TITLE: str = 'Артикул товара'
    AMOUNT_TITLE: str = 'Количество товара'
    PRICE_TITLE: str = 'Цена товара'
