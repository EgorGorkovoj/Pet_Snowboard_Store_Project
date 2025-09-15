from datetime import date
from typing import Optional
from uuid import UUID

from fastapi_users import schemas
from pydantic import EmailStr, Field, PositiveInt
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserRead(schemas.BaseUser[UUID]):
    """
    Схема для чтения информации о пользователе.

    Наследует базовую схему пользователя FastAPI Users с UUID в качестве ID.

    Поля:
        email (Optional[EmailStr]):
            Почта пользователя. Может отсутствовать (например, при регистрации через Telegram).
        name (str):
            Имя пользователя. Обязательное поле.
        surname (Optional[str]):
            Фамилия пользователя.
        nickname (Optional[str]):
            Уникальный никнейм (может использоваться вместо имени).
        birth_date (Optional[date]):
            Дата рождения.
        phone_number (Optional[PhoneNumber]):
            Номер телефона пользователя.
        is_admin (bool):
            Является ли пользователь администратором.
        is_active (bool):
            Активен ли пользователь.
        is_superuser (bool):
            Имеет ли суперправа.
        is_verified (bool):
            Подтверждён ли пользователь (например, по email или иным способом).
    """

    email: Optional[EmailStr] = Field(None, title='Почта пользователя')
    name: str
    surname: Optional[str] = None
    nickname: Optional[str] = None
    birth_date: Optional[date] = None
    phone_number: Optional[PhoneNumber] = None
    is_admin: bool
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(schemas.BaseUserCreate):
    """
    Схема для создания нового пользователя (используется при регистрации).

    Поля:
        email (Optional[EmailStr]):
            Адрес электронной почты. Необязателен, если пользователь создаётся через Telegram.
        telegram_id (Optional[PositiveInt]):
            Уникальный идентификатор пользователя в Telegram.
        password (Optional[str]):
            Пароль пользователя. Необязателен при создании через Telegram.
        name (str):
            Имя пользователя. Обязательное поле.
        surname (Optional[str]):
            Фамилия пользователя.
        nickname (Optional[str]):
            Уникальный никнейм.
        birth_date (Optional[date]):
            Дата рождения.
        phone_number (Optional[PhoneNumber]):
            Номер телефона.
    """

    email: Optional[EmailStr] = None
    telegram_id: Optional[PositiveInt] = None
    password: Optional[str] = None
    name: str
    surname: Optional[str] = None
    nickname: Optional[str] = None
    birth_date: Optional[date] = None
    phone_number: Optional[PhoneNumber] = None


class UserUpdate(schemas.BaseUserUpdate):
    """
    Схема для обновления данных пользователя.

    Все поля являются необязательными, что позволяет частично обновлять данные.

    Поля:
        email (Optional[EmailStr]):
            Новый email (если нужно изменить).
        name (Optional[str]):
            Новое имя.
        surname (Optional[str]):
            Новая фамилия.
        nickname (Optional[str]):
            Новый никнейм.
        birth_date (Optional[date]):
            Новая дата рождения.
        phone_number (Optional[PhoneNumber]):
            Новый номер телефона.
    """

    email: Optional[EmailStr] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    nickname: Optional[str] = None
    birth_date: Optional[date] = None
    phone_number: Optional[PhoneNumber] = None


class TelegramUserUpdate(UserUpdate):
    """
    Схема для обновления данных Telegram-пользователя.

    Наследует все поля 'UserUpdate', но добавляет обязательный 'telegram_id'.

    Поля:
        telegram_id (int):
            Уникальный идентификатор пользователя в Telegram.
    """

    telegram_id: int
