from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import Insert
from slugify import slugify

from app.backend.db_depends import get_db
from app.models import *
from app.sсhemas import CreateCategory


router = APIRouter(prefix='/category', tags=['category'])


@router.get('/all_categories')
async def get_all_categories():
    ...


@router.post('/create')
async def create_category(db: Annotated[Session, Depends(get_db)], create_category: CreateCategory):
    ...


@router.put('/update_category')
async def update_category():
    ...


@router.delete('/delete')
async def delete_category():
    ...
