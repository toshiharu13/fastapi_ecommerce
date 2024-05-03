from fastapi import APIRouter

router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products():
    ...


@router.post('/create')
async def create_product():
    ...


@router.get('/{category_slug}')
async def product_by_category(category_slug):
    ...


@router.get('/detail/{product_slug}')
async def product_detail(product_slug: str):
    ...


@router.put('/detail/{product_slug}')
async def update_product(product_slug: str):
    ...


@router.delete('/delete')
async def delete_product(product_id: int):
    ...

