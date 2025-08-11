from typing import List

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.validators import (
    check_on_duplicate_attributes_for_one_option_product,
    check_on_not_found_attributes_for_one_option_product,
    check_product_category_inclusion,
    validate_unique_article_product,
    validate_unique_category_title,
)
from src.core.database.db_depends import get_async_session
from src.crud.crud_attribute import attribute_crud, attribute_option_crud
from src.crud.crud_brand import brand_crud
from src.crud.crud_product import category_crud, product_crud, product_option_crud
from src.schemas.category import CategoryCreateSchema, CategoryReadSchema
from src.schemas.product import (
    AttributeReadSchema,
    ProductBaseReadSchema,
    ProductCreateSchema,
    ProductDetailReadSchema,
    ProductOptionReadSchema,
    ProductOptionUpdateSchema,
    ProductReadSchema,
    ProductUpdateSchema,
)
from src.schemas.query_param import PaginationDep

router = APIRouter()

# TODO: подключить пользователей!


@router.post('/categories', status_code=status.HTTP_201_CREATED, response_model=CategoryReadSchema)
async def create_categories(
    object_in: CategoryCreateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> CategoryReadSchema:
    """
    Создание новой категории товаров.

    Доступно только админам!

    Назначение:
        Обрабатывает запрос на создание новой категории. Проверяет уникальность
        названия и slug перед сохранением. Может создавать как основную категорию,
        так и подкатегорию, если указан ID родительской категории.

    Параметры:
        object_in (CategoryCreateSchema): Данные категории, переданные в теле запроса.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        CategoryReadSchema: Созданная категория с её ID, названием,
                            slug и ID родительской категории (если есть).
    """
    await validate_unique_category_title(
        session=session, title_category=object_in.title, slug_category=object_in.slug
    )
    db_obj = await category_crud.create(session=session, obj_in=object_in)

    return db_obj


@router.get('/categories', status_code=status.HTTP_200_OK, response_model=List[str])
async def get_the_main_categories(
    session: AsyncSession = Depends(get_async_session),
) -> List[str]:
    """
    Получает список всех главных категорий.

    Назначение:
        Используется для отображения основных (корневых) категорий товаров.

    Аргументы:
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с БД.

    Возвращает:
        List[str]: Список названий всех главных категорий.

    Исключения:
        HTTPException: 404, если в базе не найдено ни одной главной категории.
    """
    db_objects = await category_crud.get_all_main_categories(session=session)
    return db_objects


@router.get(
    '/categories/{parent_title}/subcategories',
    status_code=status.HTTP_200_OK,
    response_model=List[str],
)
async def get_subcategories_by_parent(
    parent_title: str, session: AsyncSession = Depends(get_async_session)
) -> List[str]:
    """
    Получает список подкатегорий по названию родительской категории.

    Аргументы:
        parent_title (str): Название родительской категории.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        List[str]: Названия подкатегорий.
    """
    return await category_crud.get_subcategories_by_parent_title(
        session=session, parent_title=parent_title
    )


@router.post('/product', status_code=status.HTTP_201_CREATED, response_model=ProductReadSchema)
async def create_product(
    product: ProductCreateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> ProductReadSchema:
    """
    Создаёт новый товар с вариантами и характеристиками.

    Только для администраторов!
    Категория должна быть создана заранее в базе данных.

    Поведение:
    - Если бренд не существует, создаётся автоматически.
    - Если товар с таким названием и сезоном уже есть — используется существующий.
    - Создаются варианты товара (артикулы).
    - Каждая характеристика (атрибут) создаётся при необходимости.
    - Автоматически привязывает найденные или озданные атрибуты к категории товара
      через модель "CategoryAttribute", если они ещё не привязаны.

    Параметры:
        product (ProductCreateSchema): Схема с данными о товаре, вариантах и атрибутах.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Возвращает:
        ProductReadSchema: Сериализованный объект товара с вариантами и атрибутами.
    """
    category = await category_crud.get_or_404(session=session, obj_id=product.category_id)
    brand = await brand_crud.get_brand_by_name(session=session, brand_name=product.brand_name)
    if not brand:
        brand = await brand_crud.create_brand_by_name_from_product(
            session=session, brand_name=product.brand_name, auto_commit=True
        )
    product_in_bd = await product_crud.get_product_by_name_and_season(
        session=session, title_product=product.title, season=product.season
    )
    if not product_in_bd:
        product_in_bd = await product_crud.create_product(
            session=session, product_schema=product, brand_id=brand.id
        )

    optional_read_list: List[ProductOptionReadSchema] = []

    for product_option in product.product_options:
        await validate_unique_article_product(session=session, article=product_option.article)
        prod_create = await product_option_crud.create_product_option(
            session=session,
            product_id=product_in_bd.id,
            product_option_in_bd=product_option,
            auto_commit=False,
        )
        await session.flush()
        attribute_read_list: List[AttributeReadSchema] = []
        for attribute in product_option.additional_attributes:
            attribute_in_bd = await attribute_crud.get_attr_by_name(
                session=session, attr_name=attribute.name
            )
            if not attribute_in_bd:
                attribute_in_bd = await attribute_crud.create_attr_by_name(
                    session=session, attr_name=attribute.name, auto_commit=False
                )
                await session.flush()
            await category_crud.attach_attribute_if_not_exists(
                session=session,
                category_id=category.id,
                attribute_id=attribute_in_bd.id,
                auto_commit=False,
            )
            await check_on_duplicate_attributes_for_one_option_product(
                session=session, prod_option_id=prod_create.id, attr_id=attribute_in_bd.id
            )
            attr_val_in_bd = await attribute_option_crud.create_attr_and_value_for_option_product(
                session=session,
                prod_option_id=prod_create.id,
                attr_id=attribute_in_bd.id,
                value=attribute.value,
                auto_commit=False,
            )
            attribute_read_list.append(
                AttributeReadSchema(name=attribute_in_bd.name, value=attr_val_in_bd.value)
            )
        optional_read_list.append(
            ProductOptionReadSchema(
                id=prod_create.id,
                article=prod_create.article,
                amount=prod_create.amount,
                price=prod_create.price,
                attributes=attribute_read_list,
            )
        )
    await session.commit()

    product_read = ProductReadSchema(
        id=product_in_bd.id,
        title=product_in_bd.title,
        description=product_in_bd.description,
        category_name=category.title,
        brand_name=brand.name,
        season=product_in_bd.season,
        options=optional_read_list,
    )
    return product_read


@router.get(
    '/categories/{category_slug}/{product_id}',
    status_code=status.HTTP_200_OK,
    response_model=ProductReadSchema,
)
async def get_product_by_category(
    category_slug: str, product_id: int, session: AsyncSession = Depends(get_async_session)
) -> ProductReadSchema:
    """
    Получить продукт, относящийся к определённой категории.

    Проверяет, что продукт с указанным ID принадлежит категории с заданным slug.
    Если категория или продукт не найдены, возвращает ошибку 404.
    Загружает бренд, варианты продукта и их атрибуты.

    Параметры:
        category_slug (str): Слаг категории.
        product_id (int): Идентификатор продукта.
        session (AsyncSession): Асинхронная сессия базы данных.

    Возвращает:
        ProductReadSchema: Сериализованные данные продукта с вариантами и атрибутами.
    """

    category = await category_crud.get_by_slug(session=session, slug=category_slug, raise_404=True)
    product = await product_crud.get_or_404(session=session, obj_id=product_id)
    check_product_category_inclusion(
        product_category_id=product.category_id,
        category_id=category.id,  # type: ignore
    )

    brand = await brand_crud.get_or_404(session=session, obj_id=product.brand_id)

    options_in_db = await product_option_crud.get_products_options_with_attributes(
        session=session, product_id=product.id
    )

    option_read_list = []
    for option in options_in_db:
        attributes_in_db = await attribute_option_crud.get_attributes_by_variant_id(
            session=session, variant_id=option.id
        )
        print(attributes_in_db[0].attribute.name)
        attr_read = [
            AttributeReadSchema(name=attr.attribute.name, value=attr.value)
            for attr in attributes_in_db
        ]

        option_read_list.append(
            ProductOptionReadSchema(
                id=option.id,
                article=option.article,
                amount=option.amount,
                price=option.price,
                attributes=attr_read,
            )
        )

    return ProductReadSchema(
        id=product.id,
        title=product.title,
        description=product.description,
        category_name=category.title,  # type: ignore
        brand_name=brand.name,
        season=product.season,
        options=option_read_list,
    )


# TODO: Досктринг поправить
@router.get(
    '/categories/{category_slug}',
    status_code=status.HTTP_200_OK,
    response_model=List[ProductBaseReadSchema],
)
async def get_all_product_by_category(
    category_slug: str,
    paginations: PaginationDep,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> List[ProductBaseReadSchema]:
    """
    Получить список продуктов по заданной категории со встроенной пагинацией.

    Параметры:
        category_slug (str): Уникальный slug категории, по которому производится поиск.
        paginations (PaginationDep): Зависимость с параметрами пагинации (limit и offset).
        session (AsyncSession): Асинхронная сессия базы данных.

    Возвращает:
        List[ProductBaseReadSchems]: Список сериализованных продуктов,
        содержащих ID, название, описание, бренд и сезон.

    Исключения:
        HTTPException 404: Если категория по slug не найдена.
    """

    category = await category_crud.get_by_slug(session=session, slug=category_slug, raise_404=True)
    query_params = dict(request.query_params)
    query_params.pop('limit', None)
    query_params.pop('offset', None)
    products = await product_crud.get_all_products_by_category(
        session=session,
        category_id=category.id,  # type: ignore
        filters=query_params,
        limit=paginations.limit,
        offset=paginations.offset,
    )
    products_list: List[ProductBaseReadSchema] = [
        ProductBaseReadSchema(
            id=product.id,
            title=product.title,
            category_name=category.title,  # type: ignore
            description=product.description,
            brand_name=product.brand.name,
            season=product.season,
        )
        for product in products
    ]
    return products_list


@router.get(
    '/categories/{category_slug}/{product_id}/products',
    status_code=status.HTTP_200_OK,
    response_model=List[ProductDetailReadSchema],
)
async def get_all_product_optional_with_attributes(
    category_slug: str, product_id: int, session: AsyncSession = Depends(get_async_session)
) -> List[ProductDetailReadSchema]:
    """
    Возвращает все доступные варианты конкретного товара с его характеристиками.

    Параметры:
        category_slug (str): Слаг категории, к которой должен принадлежать товар.
        product_id (int): Идентификатор основного товара.
        session (AsyncSession): Асинхронная сессия БД.

    Возвращает:
        List[ProductDetailReadSchema]: Список вариантов товара с атрибутами,
        включая информацию о товаре, его бренде, категории и сезонности.

    Исключения:
        HTTPException 404: Если категория не найдена.
        HTTPException 400/403: Если товар не принадлежит переданной категории.

    Примечание:
        Выполняется проверка принадлежности товара к указанной категории.
        Каждая вариация (ProductOption) содержит свои уникальные характеристики.
    """
    category = await category_crud.get_by_slug(session=session, slug=category_slug, raise_404=True)
    product = await product_crud.get_or_404(session=session, obj_id=product_id)
    variant_products = await product_option_crud.get_products_options_with_attributes(
        session=session, product_id=product.id
    )
    all_product_optional: List[ProductDetailReadSchema] = []
    for variant_product in variant_products:
        attr_var: List[AttributeReadSchema] = []
        check_product_category_inclusion(
            product_category_id=variant_product.product.category_id,
            category_id=category.id,  # type: ignore
        )
        for attr in variant_product.attributes:
            attr_var.append(AttributeReadSchema(name=attr.attribute.name, value=attr.value))
            attr.attribute.name
        all_product_optional.append(
            ProductDetailReadSchema(
                id=variant_product.id,
                name=variant_product.product.title,
                category_name=category.title,  # type: ignore
                description=variant_product.product.description,
                brand_name=variant_product.product.brand.name,
                season=variant_product.product.season,
                article=variant_product.article,
                amount=variant_product.amount,
                price=variant_product.price,
                attributes=attr_var,
            )
        )
    return all_product_optional


@router.patch('/products/{product_id}/', status_code=status.HTTP_200_OK)
async def update_main_product(
    product_id: int,
    update_data: ProductUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> ProductBaseReadSchema:
    """
    Обновляет основной продукт с возможностью изменения связанных полей, включая бренд.

    Параметры:
        product_id (int): Идентификатор обновляемого основного продукта.
        update_data (ProductUpdateSchema): Данные для обновления продукта.
        session (AsyncSession): Асинхронная сессия базы данных.

    Возвращает:
        ProductBaseReadSchema: Обновленная информация о продукте, включая категорию и бренд.

    Исключения:
        HTTPException 404: Если продукт с указанным ID не найден.

    Примечание:
        Если передано новое название бренда, оно создаётся в базе, если отсутствует.
        Все изменения коммитятся одной транзакцией.
    """
    product = await product_crud.get_or_404(session=session, obj_id=product_id)
    data = update_data.model_dump(exclude_unset=True)
    if brand_name := data.pop('brand_name', None):
        brand = await brand_crud.get_brand_by_name(session=session, brand_name=brand_name)
        if not brand:
            brand = await brand_crud.create(
                session=session, obj_in={'name': brand_name}, auto_commit=False
            )
            await session.flush()
        data['brand_id'] = brand.id  # type: ignore

    updated_product = await product_crud.update(
        session=session,
        db_obj=product,
        obj_in=data,
        auto_commit=False,
    )
    await session.commit()

    return ProductBaseReadSchema(
        id=updated_product.id,
        title=updated_product.title,
        description=updated_product.description,
        category_name=updated_product.category.title,
        brand_name=updated_product.brand.name,
        season=updated_product.season,
    )


@router.patch('/products/{product_id}/{variant_id}', status_code=status.HTTP_200_OK)
async def update_variant_product(
    product_id: int,
    variant_id: int,
    update_data: ProductOptionUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> ProductOptionReadSchema:
    """
    Обновляет вариант продукта, включая его основные поля и связанные атрибуты.

    Параметры:
        product_id (int): Идентификатор основного товара, к которому относится вариант.
        variant_id (int): Идентификатор варианта продукта.
        update_data (ProductOptionUpdateSchema): Схема для обновления варианта и его атрибутов.
        session (AsyncSession): Асинхронная сессия базы данных.

    Возвращает:
        ProductOptionReadSchema: Обновленный вариант продукта с актуальными атрибутами.

    Исключения:
        HTTPException 404: Если вариант продукта или запрашиваемые атрибуты не найдены.
        HTTPException 400: Если артикул не уникален или имеются другие ошибки валидации.
    """
    variant_product = await product_option_crud.get_product_option_by_id(
        session=session, product_id=product_id, product_option_id=variant_id
    )
    data_without_attr = update_data.model_dump(exclude_unset=True, exclude={'attributes'})
    if update_data.article:
        await validate_unique_article_product(session=session, article=update_data.article)
    update_variant_product = await product_option_crud.update(
        session=session, db_obj=variant_product, obj_in=data_without_attr, auto_commit=False
    )
    await session.flush()
    update_data_attr = update_data.attributes
    attr_list: List[AttributeReadSchema] = []
    if update_data_attr:
        for data_attr in update_data_attr:
            if data_attr.name:
                attr = await attribute_crud.get_attr_by_name(
                    session=session, attr_name=data_attr.name
                )
                if attr:
                    await check_on_not_found_attributes_for_one_option_product(
                        session=session, prod_option_id=update_variant_product.id, attr_id=attr.id
                    )
                    value_db = await attribute_option_crud.get_attr_by_option_product(
                        session=session, prod_option_id=update_variant_product.id, attr_id=attr.id
                    )
                    update_value = await attribute_option_crud.update(
                        session=session,
                        db_obj=value_db,
                        obj_in={'value': data_attr.value},
                        auto_commit=False,
                    )
                    await session.flush()
                    attr_list.append(AttributeReadSchema(name=attr.name, value=update_value.value))
    await session.commit()
    return ProductOptionReadSchema(
        id=update_variant_product.id,
        article=update_variant_product.article,
        amount=update_variant_product.amount,
        price=update_variant_product.price,
        attributes=attr_list,
    )


@router.delete('/products/{product_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int, session: AsyncSession = Depends(get_async_session)
) -> None:
    """
    Удаляет продукт и все связанные с ним данные.

    Параметры:
    - product_id (int): Идентификатор продукта.
    - session (AsyncSession):  Асинхронная сессия БД.

    Возвращает:
    - None: Возвращает HTTP 204 (No Content) при успешном удалении.

    Примечание:
    Удаление происходит каскадно — вместе с продуктом удаляются
    все его варианты и связанные записи.
    """
    product = await product_crud.get_or_404(session=session, obj_id=product_id)
    await product_crud.remove(session=session, db_object=product)


@router.delete('/products/{product_id}/{variant_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_variant_product(
    product_id: int, variant_id: int, session: AsyncSession = Depends(get_async_session)
) -> None:
    """
    Удаляет вариант продукта.

    Параметры:
    - product_id (int): Идентификатор продукта.
    - variant_id (int): Идентификатор варианта продукта.
    - session (AsyncSession):  Асинхронная сессия БД.

    Возвращает:
    - None: Возвращает HTTP 204 (No Content) при успешном удалении.

    Примечание:
    Удаление происходит каскадно — вместе с продуктом удаляются
    все его варианты и связанные записи.
    """
    product_option = await product_option_crud.get_product_option_by_id(
        session=session, product_id=product_id, product_option_id=variant_id
    )
    await product_option_crud.remove(session=session, db_object=product_option)
