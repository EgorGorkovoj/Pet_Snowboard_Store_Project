from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config.logging import logger
from src.core.constants import TextErrorConstants
from src.crud.crud_base import CRUDBase
from src.models.attribute import Attribute, ProductOptionAttribute


class AttributeCRUD(CRUDBase):
    """
    CRUD-класс для работы с моделью Attribute.

    Назначение:
        Управляет созданием и получением атрибутов (характеристик товара).
    """

    async def get_attr_by_name(self, session: AsyncSession, attr_name: str) -> Optional[Attribute]:
        """
        Получает атрибут по его названию.

        Параметры:
            session (AsyncSession): Сессия SQLAlchemy.
            attr_name (str): Название атрибута.

        Возвращает:
            Optional[Attribute]: Найденный атрибут или None.
        """
        result = await session.execute(select(Attribute).where(Attribute.name == attr_name))
        return result.scalars().first()

    async def create_attr_by_name(
        self, session: AsyncSession, attr_name: str, auto_commit: bool = True
    ) -> Attribute:
        """
        Создает атрибут, если он еще не существует.

        Назначение:
            Используется при создании товара — если атрибута нет, он добавляется в таблицу.

        Параметры:
            session (AsyncSession): Сессия SQLAlchemy.
            attr_name (str): Название нового атрибута.
            auto_commit (bool): Выполнять ли commit автоматически (по умолчанию True).

        Возвращает:
            Attribute: Созданный объект атрибута.
        """

        db_obj = Attribute(name=attr_name)
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


class AttributeOptionProductCRUD(CRUDBase):
    """
    CRUD-класс для работы с моделью ProductOptionAttribute.

    Назначение:
        Управляет связью между вариантом продукта и его атрибутами.
    """

    async def get_attr_by_option_product(
        self, session: AsyncSession, prod_option_id: int, attr_id: int
    ) -> Optional[ProductOptionAttribute]:
        """
        Получает запись атрибута, связанного с конкретным вариантом товара.

        Параметры:
            session (AsyncSession): Сессия SQLAlchemy.
            prod_option_id (int): ID варианта продукта.
            attr_id (int): ID атрибута.

        Возвращает:
            Optional[ProductOptionAttribute]: Найденная запись или None.
        """
        result = await session.execute(
            select(ProductOptionAttribute).where(
                and_(
                    ProductOptionAttribute.variant_id == prod_option_id,
                    ProductOptionAttribute.attribute_id == attr_id,
                )
            )
        )
        return result.scalars().first()

    async def get_attributes_by_variant_id(
        self, session: AsyncSession, variant_id: int
    ) -> List[ProductOptionAttribute]:
        """
        Получает все атрибуты и их значения, привязанные к конкретному варианту продукта.

        Параметры:
            session (AsyncSession): Сессия SQLAlchemy.
            variant_id (int): Идентификатор варианта продукта.

        Возвращает:
            List[ProductOptionAttribute]: Список атрибутов и их значений, связанных с вариантом.
        """

        result = await session.execute(
            select(ProductOptionAttribute)
            .where(ProductOptionAttribute.variant_id == variant_id)
            .options(selectinload(ProductOptionAttribute.attribute))
        )
        return result.scalars().all()  # type: ignore

    async def create_attr_and_value_for_option_product(
        self,
        session: AsyncSession,
        prod_option_id: int,
        attr_id: int,
        value: str,
        auto_commit: bool = True,
    ) -> ProductOptionAttribute:
        """
        Создает значение атрибута и связывает его с вариантом товара.

        Назначение:
            Добавляет запись в промежуточную таблицу ProductOptionAttribute,
            содержащую ID варианта товара, ID атрибута и его значение.

        Параметры:
            session (AsyncSession): Сессия SQLAlchemy.
            prod_option_id (int): ID варианта товара.
            attr_id (int): ID атрибута.
            value (str): Значение атрибута.
            auto_commit (bool): Выполнять ли commit автоматически (по умолчанию True).

        Возвращает:
            ProductOptionAttribute: Созданный объект связи.
        """

        db_obj = ProductOptionAttribute(
            variant_id=prod_option_id, attribute_id=attr_id, value=value
        )
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


attribute_crud = AttributeCRUD(Attribute)
attribute_option_crud = AttributeOptionProductCRUD(ProductOptionAttribute)
