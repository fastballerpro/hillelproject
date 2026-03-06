from fastapi import APIRouter, status, Depends, Form, UploadFile, File
from apps.core.dependencies import get_session, get_current_user
from apps.products.crud import product_manager
from apps.products.s3 import s3_service
import uuid

product_router = APIRouter()


@product_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(
    title: str = Form(),
    price: int = Form(gt=0),
    description: str = Form(default=""),
    main_image: UploadFile = File(),
    # images: list[UploadFile] = File(default=None, max_length=3),
    session=Depends(get_session)
):
    product_uuid = uuid.uuid4()
    main_image_url = s3_service.upload_file(main_image, product_uuid=product_uuid)
    product = await product_manager.create_product(
        session=session,
        title=title, price=price, description=description, uuid_id=product_uuid, main_image=main_image_url
    )
    return product