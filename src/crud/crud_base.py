from decimal import Decimal
from typing import Any, Dict, Generic, Optional, Type, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import Select, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.core.config.logging import logger
from src.core.constants import TextErrorConstants
from src.models.base import BoardShopBase

ModelType = TypeVar('ModelType', bound=BoardShopBase)
CreateShemaType = TypeVar('CreateShemaType', bound=BaseModel)
UpdateShemaType = TypeVar('UpdateShemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateShemaType, UpdateShemaType]):
    """Универсальный базовый класс для CRUD операций."""

    def __init__(self, model: Type[ModelType]):
        """
        Инициализирует CRUD-класс с указанной моделью.

        Параметры:
            model: SQLAlchemy-модель (класс), связанный с таблицей в БД.
        """
        self.model = model

    async def get(self, session: AsyncSession, obj_id: str | int | UUID) -> Optional[ModelType]:
        """
        Получает объект из базы данных по ID.

        Параметры:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            obj_id (str | int | UUID): Уникальный идентификатор объекта.

        Возвращает:
            Optional[ModelType]: Экземпляр модели или None, если объект не найден.
        """
        result = await session.execute(select(self.model).where(self.model.id == obj_id))
        return result.scalars().first()

    async def get_or_404(
        self, session: AsyncSession, obj_id: int | UUID, message: str | None = None
    ) -> ModelType:
        """
        Получает объект из БД по id или выбрасывает 404-ошибку.

        Параметры:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            obj_id (int | UUID): Идентификатор объекта.
            message (str): сообщение, которое вернется с ошибкой 404.

        Возвращает:
            ModelType: Экземпляр модели.

        Исключения:
            HTTPException со статусом 404, если не найдет объект по id в БД.
        """

        result = await self.get(session=session, obj_id=obj_id)

        if not result:
            if message is None:
                message = TextErrorConstants.NOT_FOUND_BY_ID.format(
                    obj=self.model.__name__, id=obj_id
                )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        return result

    async def get_by_slug(
        self, session: AsyncSession, slug: str, raise_404: bool = False, message: str | None = None
    ) -> Optional[ModelType]:
        """
        Получает объект модели по значению поля 'slug'.

        Параметры:
            session : AsyncSession
            Активная асинхронная сессия SQLAlchemy.
            slug (str): Значение поля 'slug', по которому производится поиск.
            raise_404 : bool, по умолчанию False.
                        Если True и объект не найден — выбрасывается HTTPException с кодом 404.
            message (str | None): По умолчанию None. Пользовательское сообщение для исключения 404.
                                  Если не передано — будет сгенерировано автоматически.

        Возвращает:
            Optional[ModelType]: Объект модели, если найден.
                                 Иначе — None (или исключение, если raise_404=True).

        Исключения:
            HTTPException: Если объект не найден и raise_404=True.

        Примечание:
            Атрибут 'slug' должен существовать в модели.
            Если модель его не содержит — может возникнуть ошибка.
        """
        result = await session.execute(
            select(self.model).where(self.model.slug == slug)  # type: ignore
        )
        obj = result.scalars().first()

        if not obj and raise_404:
            if message is None:
                message = TextErrorConstants.NOT_FOUND_BY_SLUG.format(
                    obj=self.model.__name__, slug=slug
                )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        return obj

    async def create(
        self, session: AsyncSession, obj_in: CreateShemaType | dict, auto_commit: bool = True
    ) -> ModelType:
        """
        Создаёт новый объект в базе данных.

        Назначение:
            Добавляет запись на основе входной схемы 'obj_in' в текущую сессию.
            Если 'auto_commit=True', коммит происходит сразу после добавления
            и объект cохраняется и обновляется.

        Параметры:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            obj_in (CreateSchemaType): Входная Pydantic-схема с данными для создания объекта.
            auto_commit (bool, по умолчанию True):
                Флаг автоматического коммита.
                Если False, объект добавляется в сессию, но коммит не выполняется —
                это удобно при создании нескольких объектов в рамках одной транзакции.

        Возвращает:
            ModelType: Сохранённый экземпляр модели.

        Исключения:
            HTTPException или любая другая ошибка, возникшая при добавлении объекта.
            В случае ошибки происходит откат транзакции ('rollback').

        Примечание:
            При массовом создании объектов рекомендуется устанавливать 'auto_commit=False'
            и выполнять общий 'session.commit()' один раз после добавления всех объектов.
        """
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.model_dump()

        db_obj = self.model(**obj_data)
        try:
            session.add(db_obj)
            if auto_commit:
                await session.commit()
                await session.refresh(db_obj)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateShemaType | dict[str, Any],
        auto_commit: bool = True,
    ) -> ModelType:
        """
        Обновляет существующий объект в базе данных.

        Назначение:
            Обновляет поля переданного объекта на основе входных данных (Pydantic-схемы),
            исключая поля, которые не были явно заданы (exclude_unset=True).
            По умолчанию изменения коммитятся автоматически.

        Параметры:
            session (AsyncSession): Активная асинхронная сессия SQLAlchemy.
            db_obj (ModelType): Объект модели, который необходимо обновить.
            obj_in (UpdateShemaType): Входная схема Pydantic с новыми значениями полей.
            auto_commit (bool): Если True (по умолчанию), изменения будут закоммичены
                                и объект обновится в сессии. Иначе коммит нужно выполнить вручную.

        Возвращает:
            ModelType: Обновлённый объект модели.

        Исключения:
            Exception: В случае ошибки обновления.
                       Изменения будут откатаны, ошибка залогирована.

        Примечание:
            При обновлении группы объектов (bulk update) рекомендуется устанавливать
            auto_commit=False, чтобы закоммитить все изменения одной операцией.
        """

        relationships = {rel.key for rel in inspect(self.model).relationships}
        db_obj_update = jsonable_encoder(db_obj, exclude=relationships)
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.model_dump(exclude_unset=True)
        for field in db_obj_update:
            if field in obj_data:
                setattr(db_obj, field, obj_data[field])

        try:
            session.add(db_obj)
            if auto_commit:
                await session.commit()
                await session.refresh(db_obj)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.UPDATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return db_obj

    async def remove(
        self,
        session: AsyncSession,
        db_object: ModelType,
        auto_commit: bool = True,
    ) -> Any:
        """
        Удаляет объект из базы данных.

        Назначение:
            Удаляет переданный экземпляр модели из базы данных.
            По умолчанию изменения коммитятся автоматически (auto_commit = True).

        Параметры:
            session (AsyncSession): Активная асинхронная сессия SQLAlchemy.
            db_object (ModelType): Объект, который требуется удалить из базы данных.
            auto_commit (bool): Если True (по умолчанию), изменения коммитятся сразу.
                                Если False — необходимо выполнить коммит вручную после удаления.

        Возвращает:
            Any: Обычно None.

        Исключения:
            Exception: В случае ошибки удаления.
                       Изменения будут откатаны, ошибка залогирована.

        Примечание:
            При удалении нескольких объектов (bulk delete) рекомендуется использовать
            'auto_commit=False', чтобы коммитить всё одной операцией.
        """
        try:
            await session.delete(db_object)
            if auto_commit:
                await session.commit()
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.DELETE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error

    def _apply_limit_offset(self, query: Select, limit: int, offset: int) -> Select:
        """
        Применяет пагинацию к SQL-запросу.

        Параметры:
            query (Select): SQLAlchemy запрос.
            limit (int): Количество записей.
            offset (int): Смещение.

        Возвращает:
            Select: Обновлённый запрос с пагинацией.
        """
        query_pagination = query.limit(limit).offset(offset)
        return query_pagination

    def _apply_filters_by_attribute(self, query: Select, filters: Dict[str, Any]) -> Select:
        """
        Применяет фильтры по атрибутам. Исользуеются модели Attribute,
        ProductOptionAttribute поэтому импортируем только внути.
        """
        from src.models.attribute import Attribute, ProductOptionAttribute
        from src.models.product import Product, ProductOption

        query = query.join(ProductOption, Product.id == ProductOption.product_id)

        min_price = filters.pop('min_price', None)
        max_price = filters.pop('max_price', None)

        if min_price is not None and max_price is not None:
            query = query.where(
                ProductOption.price.between(Decimal(min_price), Decimal(max_price))
            )
        elif min_price is not None:
            query = query.where(ProductOption.price >= Decimal(min_price))
        elif max_price is not None:
            query = query.where(ProductOption.price <= Decimal(max_price))

        for i, (name_attr, value_attr) in enumerate(filters.items()):
            poa_alias = aliased(ProductOptionAttribute, name=f'poa_{i}')
            attr_alias = aliased(Attribute, name=f'attr_{i}')

            query = (
                query.join(poa_alias, poa_alias.variant_id == ProductOption.id)
                .join(attr_alias, attr_alias.id == poa_alias.attribute_id)
                .where(attr_alias.name == name_attr)
                .where(poa_alias.value == value_attr)
            )
        return query
