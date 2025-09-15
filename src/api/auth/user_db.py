import uuid

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.db_depends import get_async_session
from src.models.user import User


class CustomUserDatabase(SQLAlchemyUserDatabase[User, uuid.UUID]):  # type: ignore
    """
    Кастомный менеджер пользователей для работы с базой данных через SQLAlchemy.

    Назначение:
        - Расширяет стандартный SQLAlchemyUserDatabase из FastAPI Users.
        - Добавляет возможность поиска пользователя по Telegram ID.
        - Позволяет использовать любую модель пользователя (User) с UUID в качестве идентификатора.

    Атрибуты:
        user_model (type[User]):
            Модель пользователя, используемая для запросов к базе данных.
    """

    user_model: type[User]

    def __init__(self, session: AsyncSession, user_model: type[User]):
        """
        Инициализация кастомного менеджера пользователей.

        Аргументы:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            user_model (type[User]): Модель пользователя для работы с базой данных.
        """
        super().__init__(session=session, user_table=user_model)
        self.user_model = user_model

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """
        Получить пользователя по его Telegram ID.

        Аргументы:
            telegram_id (int): Идентификатор пользователя в Telegram.

        Возвращает:
            User | None: Экземпляр пользователя, если найден, иначе None.
        """
        query = select(self.user_model).where(self.user_model.telegram_id == telegram_id)
        result = await self.session.execute(query)
        return result.scalars().first()


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """
    Функция-зависимость FastAPI для получения экземпляра CustomUserDatabase.

    Аргументы:
        session (AsyncSession, optional): Асинхронная сессия SQLAlchemy.
                                         Получается через Depends(get_async_session).

    Возвращает:
        CustomUserDatabase: Экземпляр кастомного менеджера пользователей.
    """
    yield CustomUserDatabase(session, User)
