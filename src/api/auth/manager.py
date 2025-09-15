import re
import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin, schemas

from src.api.auth.constants import AuthManagerValidateConstants
from src.api.auth.user_db import get_user_db
from src.core.config.app import settings
from src.models.user import User
from src.schemas.user import TelegramUserUpdate, UserCreate


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):  # type: ignore
    """
    Менеджер пользователей для интернет-магазина.

    Назначение:
        - Расширяет базовый класс FastAPI Users 'BaseUserManager'.
        - Добавляет кастомную валидацию пароля.
        - Поддерживает создание и обновление пользователей без пароля
          (например, Telegram-пользователей).
        - Содержит хуки (события) для действий после регистрации,
          восстановления пароля и верификации.

    Атрибуты:
        reset_password_token_secret (str):
            Секрет для генерации токенов восстановления пароля.
        verification_token_secret (str):
            Секрет для генерации токенов подтверждения e-mail.
    """

    reset_password_token_secret = settings.secret
    verification_token_secret = settings.secret

    async def validate_password(
        self,
        password: str,
        user: schemas.UC | User,
    ) -> None:
        """
        Проверяет корректность пароля при регистрации/обновлении пользователя.

        Логика валидации:
            - Пароль не должен содержать e-mail пользователя.
            - Пароль не должен быть палиндромом.
            - Пароль должен содержать:
                * хотя бы одну заглавную букву,
                * хотя бы одну цифру,
                * хотя бы один спецсимвол (_, #, %),
                * длину не менее 8 символов.

        Аргументы:
            password (str): Пароль для проверки.
            user (schemas.UC | User): Объект пользователя (или схема создания).

        Исключения:
            InvalidPasswordException: если пароль не соответствует требованиям.
        """
        if user.email and user.email in password:
            raise InvalidPasswordException(
                reason=AuthManagerValidateConstants.ERROR_EMAIL_IN_PASSWORD
            )
        reverse_pass = password[::-1].lower()
        if password.lower() == reverse_pass:
            raise InvalidPasswordException(reason=AuthManagerValidateConstants.ERROR_PALINDROM)
        if not re.match(AuthManagerValidateConstants.REGULAR_EXPR_PASSWORD, password):
            raise InvalidPasswordException(reason=AuthManagerValidateConstants.ERROR_TEXT_PASSWORD)

    async def create(
        self, user_create: schemas.UC, safe: bool = False, request: Optional[Request] = None
    ) -> User:
        """
        Создаёт нового пользователя.

        Логика:
            - Если создаётся Telegram-пользователь и пароль не указан —
              в БД сохраняется 'hashed_password=None'.
            - Если пароль отсутствует у обычного пользователя —
              также сохраняется 'hashed_password=None'.
            - В остальных случаях используется стандартная логика FastAPI Users.

        Аргументы:
            user_create (schemas.UC):
                Схема создания пользователя ('UserCreate' или другая совместимая).
            safe (bool, по умолчанию=False):
                Флаг безопасного создания (ограничивает доступные для записи поля).
            request (Optional[Request], по умолчанию=None):
                Объект запроса FastAPI.

        Возвращает:
            User: Созданный пользователь.
        """
        if isinstance(user_create, UserCreate):
            if user_create.telegram_id and not user_create.password:
                user_dict = user_create.model_dump(exclude_unset=True)
                user_dict['hashed_password'] = None
                return await self.user_db.create(user_dict)
            if user_create.password is None:
                user_dict = user_create.model_dump(exclude_unset=True)
                user_dict['hashed_password'] = None
                return await self.user_db.create(user_dict)

        return await super().create(user_create, safe, request)

    async def update(
        self,
        user_update: schemas.UU,
        user: User,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        """
        Обновляет данные пользователя с поддержкой кастомной логики для Telegram-пользователей.

        Назначение:
            - Позволяет обновлять пользователей как через стандартные схемы FastAPI Users
              ('UserUpdate'), так и через кастомную ('TelegramUserUpdate').
            - Обеспечивает корректную обработку случаев, когда у пользователя отсутствует пароль
              (например, регистрация только через Telegram).
            - Если в обновлении передан 'password=None' или пароль отсутствует —
              вместо 'password' в БД будет записан 'hashed_password=None'.

        Аргументы:
            user_update (schemas.UU):
                Объект схемы обновления пользователя (например, 'UserUpdate'
                или 'TelegramUserUpdate').
            user (User):
                Экземпляр модели пользователя, который требуется обновить.
            safe (bool, по умолчанию = False):
               Флаг безопасного обновления (определяет, какие поля можно изменять).
            request (Optional[Request], по умолчанию = None):
                Объект запроса FastAPI. Может использоваться для контекста
                (например, логирование, зависимости).

        Возвращает:
            User:
               Обновлённый объект пользователя.

        Исключения:
            Может пробросить ошибки валидации Pydantic или
            исключения из базового класса 'BaseUserManager'.
        """
        update_data = user_update.model_dump(exclude_unset=True)

        if isinstance(user_update, TelegramUserUpdate):
            if 'password' not in update_data or update_data['password'] is None:
                update_data['hashed_password'] = None

        if 'password' in update_data and update_data['password'] is None:
            update_data['hashed_password'] = None
            update_data.pop('password', None)

        user_update_new = type(user_update)(**update_data)
        return await super().update(user_update_new, user, safe, request)

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Хук, вызываемый после успешной регистрации пользователя.

        Аргументы:
            user (User): Зарегистрированный пользователь.
            request (Optional[Request]): Объект запроса FastAPI.
        """
        print(f'Пользователь {user.id} успешно зарегистрирован.')

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Хук, вызываемый после запроса на восстановление пароля.

        Аргументы:
            user (User): Пользователь, запросивший восстановление пароля.
            token (str): Токен восстановления.
            request (Optional[Request]): Объект запроса FastAPI.
        """
        print(f'Пользователь {user.id} запросил восстановление пароля. Токен для сброса: {token}')

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Хук, вызываемый после запроса на подтверждение e-mail.

        Аргументы:
            user (User): Пользователь, запросивший подтверждение.
            token (str): Токен подтверждения.
            request (Optional[Request]): Объект запроса FastAPI.
        """
        print(
            f'Пользователь {user.id} запросил подтверждение e-mail. Токен подтверждения: {token}'
        )


async def get_user_manager(user_db=Depends(get_user_db)):
    """
    Провайдер менеджера пользователей для зависимостей FastAPI.

    Назначение:
        Используется как dependency injection при работе с роутами FastAPI Users.

    Аргументы:
        user_db: Объект доступа к базе данных пользователей.

    Возвращает:
        UserManager: Экземпляр менеджера пользователей.
    """
    yield UserManager(user_db)
