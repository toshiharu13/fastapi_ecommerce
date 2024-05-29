from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from statistics import mean

from app.routers.auth import get_current_user
from app.backend.db_depends import get_db
from app.models import ratings_reviews, products
from app.sсhemas import CreateReview

router = APIRouter(prefix='/rewiews', tags=['rewiews'])


@router.get('/all_reviews')
# TODO
async def get_all_reviews(db: Annotated[AsyncSession, Depends(get_db)],):
    rewiews = await db.scalars(select(ratings_reviews.Review).where(ratings_reviews.Review.is_active == True))
    return rewiews.all()


@router.get('/products_reviews')
async def get_product_review(db: Annotated[AsyncSession, Depends(get_db)], product_id: int):
    request_products_rewiews = await db.scalar(select(ratings_reviews.Review).where(
        ratings_reviews.Review.product_id == product_id,
        ratings_reviews.Review.is_active == True))
    if request_products_rewiews is not None:
        return request_products_rewiews
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no reviews found')


@router.post('/add_review')
async def add_review(db: Annotated[AsyncSession, Depends(get_db)], create_review_model: CreateReview, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_customer'):
        requested_product = await db.scalar(select(products.Product).where(products.Product.id == create_review_model.product_id))
        result = await db.execute(insert(ratings_reviews.Rating).values(
            grade=create_review_model.grade,
            user_id=get_user.get('id'),
            product_id=create_review_model.product_id
        ))
        inserted_rate_id = result.inserted_primary_key[0]
        product_review = await db.execute(insert(ratings_reviews.Review).values(
            user_id=get_user.get('id'),
            product_id=create_review_model.product_id,
            rating_id=inserted_rate_id,
            comment=create_review_model.comment
        ))
        all_evaluates = await db.scalars(select(ratings_reviews.Rating.grade).where(ratings_reviews.Rating.product_id == create_review_model.product_id))
        all_evaluates = all_evaluates.all()
        product_rate = mean(all_evaluates)
        requested_product.rating = product_rate
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'}
    else:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to use this method")


@router.delete('/delete_reviews')
async def delete_reviews(db: Annotated[AsyncSession, Depends(get_db)], review_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        review_object = await db.scalar(select(ratings_reviews.Review).where(ratings_reviews.Review.id == review_id))
        if review_object is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no reviews found')
        rate_object = await db.scalar(select(ratings_reviews.Rating).where(ratings_reviews.Rating.id == review_object.rating_id))
        if rate_object is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no rate found')
        review_object.is_active = False
        rate_object.is_active = False
        await db.commit()

        requested_product = await db.scalar(select(products.Product).where(
            products.Product.id == review_object.product_id))
        all_evaluates = await db.scalars(
            select(ratings_reviews.Rating.grade).where(
                ratings_reviews.Rating.product_id == requested_product.id,
                ratings_reviews.Rating.is_active == True))
        all_evaluates = all_evaluates.all()
        product_rate = mean(all_evaluates)
        requested_product.rating = product_rate
        await db.commit()

        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Product delete is successful'
        }
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorized to use this method")
