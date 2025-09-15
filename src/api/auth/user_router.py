from fastapi import APIRouter, Depends, HTTPException

from src.api.auth.auth import auth_backend, fastapi_users
from src.api.auth.manager import get_user_manager
from src.schemas.user import TelegramUserUpdate, UserCreate, UserRead, UserUpdate

router = APIRouter()


router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/admin/jwt',
    tags=['auth'],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix='/auth',
    tags=['auth'],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix='/users',
    tags=['users'],
)


@router.patch('/telegram/user/', response_model=UserRead)
async def update_telegram_user(
    user_update: TelegramUserUpdate,
    user_manager=Depends(get_user_manager),
):
    """
    Обновляет данные пользователя по его Telegram ID.

    Аргументы:
        user_update (TelegramUserUpdate): Данные для обновления пользователя.
                                         Содержит telegram_id и новые значения полей.
        user_manager: Зависимость FastAPI, предоставляет доступ к менеджеру пользователей.

    Процесс:
        1. Находит пользователя по telegram_id.
        2. Если пользователь не найден, возвращает 404.
        3. Обновляет данные пользователя с учетом переданных полей.

    Возвращает:
        UserRead: Обновленный пользователь.

    Исключения:
        HTTPException 404: Если пользователь с указанным telegram_id не найден.
    """
    user = await user_manager.user_db.get_by_telegram_id(user_update.telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден.')

    updated_user = await user_manager.user_db.update(
        user, user_update.model_dump(exclude_unset=True)
    )
    return updated_user
