from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.auth import get_current_user
from app.backend.db_depends import get_db
from app.models import *
from app.sсhemas import CreateProduct

router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(
        select(Product).where(Product.is_active == True, Product.stock > 0))
    return products.all()


@router.post('/create')
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], new_product: CreateProduct, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('admin') or get_user.get('is_supplier'):
        await db.execute(insert(Product).values(
            name=new_product.name,
            slug=slugify(new_product.name),
            description=new_product.description,
            price=new_product.price,
            image_url=new_product.image_url,
            stock=new_product.stock,
            category_id=new_product.category,
            supplier_id=get_user.get('id')
        ))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to use this method")


@router.get('/{category_slug}')
async def product_by_category(db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    main_category = await db.scalar(select(Category).where(Category.slug == category_slug))
    if main_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found')
    requested_categories = await db.scalars(select(Category.id).where(Category.parent_id == main_category.id))
    requested_categories = requested_categories.all()
    requested_categories.append(main_category.id)
    #print(f'requested_categories {requested_categories}')
    requestetd_products = await db.scalars(
        select(Product).where(Product.is_active == True, Product.stock > 0, Product.category_id.in_(requested_categories)))
    requestetd_products = requestetd_products.all()
    #print(f'requestetd_products {requestetd_products}')
    return {
        'requestetd_products': requestetd_products
    }


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    requested_product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if requested_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    return {
        'requested_product': requested_product
    }


@router.put('/detail/{product_slug}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         update_product_model: CreateProduct, get_user: Annotated[dict, Depends(get_current_user)]):
    product_update = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    if get_user.get('is_supplier') or get_user.get('is_admin'):
        if get_user.get('id') == product_update.supplier_id or get_user.get('is_admin'):
            await db.execute(
                update(Product).where(Product.slug == product_slug)
                .values(name=update_product_model.name,
                        description=update_product_model.description,
                        price=update_product_model.price,
                        image_url=update_product_model.image_url,
                        stock=update_product_model.stock,
                        category_id=update_product_model.category,
                        slug=slugify(update_product_model.name)))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product update is successful'
            }
        else:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to use this method'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )


@router.delete('/delete')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)],  product_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
    requested_product = await db.scalar(select(Product).where(Product.id == product_id))
    if get_user.get('admin') or (get_user.get('is_supplier') and get_user.get('id') == requested_product.supplier_id):
        if requested_product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There are no product'
            )
        await db.execute(update(Product).where(Product.id == requested_product.id).values(is_active=False))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Product delete is successful'
        }

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to use this method")