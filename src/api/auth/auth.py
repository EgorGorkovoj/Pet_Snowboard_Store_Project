from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend

from src.api.auth.manager import get_user_manager
from src.api.auth.strategy import get_redis_strategy
from src.api.auth.transport import bearer_transport
from src.models.user import User

auth_backend = AuthenticationBackend(
    name='admin_redis',
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
