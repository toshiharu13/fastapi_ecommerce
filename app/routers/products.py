from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update
from slugify import slugify

from app.backend.db_depends import get_db
from app.models import *
from app.sсhemas import CreateProduct

router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products(db: Annotated[Session, Depends(get_db)]):
    products = db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0)).all()
    return products


@router.post('/create')
async def create_product(db: Annotated[Session, Depends(get_db)], new_product: CreateProduct):
    db.execute(insert(Product).values(
        name=new_product.name,
        slug=slugify(new_product.name),
        description=new_product.description,
        price=new_product.price,
        image_url=new_product.image_url,
        stock=new_product.stock,
        category_id=new_product.category
    ))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.get('/{category_slug}')
async def product_by_category(db: Annotated[Session, Depends(get_db)], category_slug: str):
    main_category = db.scalar(select(Category).where(Category.slug == category_slug))
    if main_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found')
    requested_categories = db.scalars(select(Category.id).where(Category.parent_id == main_category.id)).all()
    requested_categories.append(main_category.id)
    print(f'requested_categories {requested_categories}')
    requestetd_products = db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0, Product.category_id.in_(requested_categories))).all()
    print(f'requestetd_products {requestetd_products}')
    return {
        'requestetd_products': requestetd_products
    }


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[Session, Depends(get_db)], product_slug: str):
    requested_product = db.scalar(select(Product).where(Product.slug == product_slug))
    if requested_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    return {
        'requested_product': requested_product
    }


@router.put('/detail/{product_slug}')
async def update_product(db: Annotated[Session, Depends(get_db)], product_slug: str, update_product: CreateProduct):
    requested_product = db.scalar(select(Product).where(Product.slug == product_slug))
    if requested_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    db.execute(update(Product).where(Product.id == requested_product.id).values(
        name=update_product.name,
        slug=slugify(update_product.name),
        description=update_product.description,
        price=update_product.price,
        image_url=update_product.image_url,
        stock=update_product.stock,
        category_id=update_product.category
    ))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product update is successful'
    }


@router.delete('/delete')
async def delete_product(db: Annotated[Session, Depends(get_db)],  product_id: int):
    requested_product = db.scalar(select(Product).where(Product.id == product_id))
    if requested_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    db.execute(update(Product).where(Product.id == requested_product.id).values(is_active=False))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product delete is successful'
    }

