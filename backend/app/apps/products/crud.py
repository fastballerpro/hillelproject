from apps.auth.password_handler import PasswordHandler
from apps.products.models import Product
from apps.users.schemas import RegisterUserSchema
from sqlalchemy import  select, or_, and_
from fastapi import HTTPException, status


class ProductManager:
    async def create_product(self, session, title, price, description, uuid_id, main_image, images):
        query = select(Product).filter(Product.title == title)
        result = await session.execute(query)
        maybe_product = result.scalar_one_or_none()
        if maybe_product:
            raise HTTPException(
                detail=f'Product with title {title} already exists',
                status_code=status.HTTP_409_CONFLICT
            )

        product = Product(
            title=title,
            price=price,
            description=description,
            uuid_id=uuid_id,
            main_image=main_image,
            images=images
        )
        session.add(product)
        await session.commit()
        return product

    async def get_product(self, session, product_uuid: str) -> Product | None:
        query = select(Product).filter(Product.uuid_id == product_uuid)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_products(self, session, q: str) -> list[Product]:
        query = select(Product)
        if q := q.strip():
            words = [word for word in q.replace(',', ' ').split() if len(word) > 1]
            search_fields_condition = or_(
                and_(*(search_field.icontains(word) for word in words))
                for search_field in (Product.title, Product.description)
            )
            query = query.filter(search_fields_condition)
        query = query.limit(8)
        result = await session.execute(query)
        return list(result.scalars())


product_manager = ProductManager()