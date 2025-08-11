from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """
    Параметры пагинации для запросов с ограничением и смещением.

    Поля:
        limit (int): Количество элементов на странице. Минимум — 1. По умолчанию — 10.
        offset (int): Смещение (количество пропущенных записей). Минимум — 0. По умолчанию — 0.
    """

    limit: int = Field(
        10, ge=1, le=100, title='Лимит', description='Количество элементов на странице'
    )
    offset: int = Field(0, ge=0, title='Пропуск записей', description='Смещение для пагинации')


# Зависимость для пагинации.
PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]
