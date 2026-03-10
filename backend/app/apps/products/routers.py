from fastapi import APIRouter, status, Depends, Form, UploadFile, File, HTTPException
from apps.core.dependencies import get_session, get_current_user
from apps.products.crud import product_manager
from apps.products.s3 import s3_service
from typing import List
import uuid

product_router = APIRouter()


@product_router.post('/create', status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_product(
    title: str = Form(),
    price: int = Form(gt=0),
    description: str = Form(default=""),
    main_image: UploadFile = File(),
        image1: UploadFile = File(default=None),
        image2: UploadFile = File(default=None),
    session=Depends(get_session)
):
    product_uuid = uuid.uuid4()
    main_image_url = s3_service.upload_file(main_image, product_uuid=product_uuid)
    images = [s3_service.upload_file(i, product_uuid=product_uuid) for i in (image1, image2) if i]
    product = await product_manager.create_product(
        session=session,
        title=title, price=price, description=description, uuid_id=product_uuid, main_image=main_image_url, images=images
    )
    return product

@product_router.get('/{product_uuid}')
async def get_product(
    product_uuid: uuid.UUID,
    session=Depends(get_session)
):

    product = await product_manager.get_product(
        session=session,
        product_uuid=product_uuid,
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='product not found')
    return product


@product_router.get('/')
async def get_products(
    q: str = '',
    session=Depends(get_session)
):

    products: list = await product_manager.get_products(
        session=session,
        q=q,
    )
    return products