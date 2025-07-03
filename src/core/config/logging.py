import sys
import time

from fastapi import Request
from loguru import logger

from src.core.config.app import settings
from src.core.constants import LoggingBaseConstants

logger.remove(0)
logger.add(sys.stderr, level=settings.log_level)
logger.add(
    LoggingBaseConstants.LOG_FILE,
    rotation=LoggingBaseConstants.LOG_ROTATION,
    retention=LoggingBaseConstants.LOG_RETENTION,
    level=settings.log_level,
)


class LoggingMidleware:
    """
    Middleware-класс для логирования всех входящих HTTP-запросов и исходящих ответов.

    Что делает:
    - Логирует HTTP-метод, URL и статус ответа.
    - Измеряет длительность обработки запроса (в секундах).
    - Выводит лог в консоль и/или файл (настраивается через loguru).

    Аргументы метода __call__:
    - request (Request): Объект запроса FastAPI.
    - call_next: Функция, которая вызывает следующий обработчик (роутер/эндпоинт).

    Пример использования:
        app = FastAPI()
        app.middleware("http")(LoggingMiddleware())

    Пример лога:
        Запрос: GET http://localhost:8000/api/items - 0.057 sec; Ответ: 200
    """

    async def __call__(self, request: Request, call_next, *args, **kwargs):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(
            f'Запрос: {request.method} {request.url} - {duration:.3f} sec; '
            f'Ответ: {response.status_code}'
        )
        return response
