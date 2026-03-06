from apps.auth.password_handler import PasswordHandler
from apps.products.models import Product
from apps.users.schemas import RegisterUserSchema
from sqlalchemy import  select
from fastapi import HTTPException, status


class ProductManager:
    async def create_product(self, session, title, price, description, uuid_id, main_image):
        # maybe_user = await self.get(session=session, user_email=user_register_data.email)
        # if maybe_user:
        #     raise HTTPException(
        #         detail=f'User with email {user_register_data.email} already exists',
        #         status_code=status.HTTP_409_CONFLICT
        #     )


        product = Product(
            title=title,
            price=price,
            description=description,
            uuid_id=uuid_id,
            main_image=main_image,
            images=[main_image, main_image]
        )
        session.add(product)
        await session.commit()
        return product

    # async def get(self, session, user_email: str) -> User | None:
    #     query = select(User).filter(User.email == user_email)
    #     result = await session.execute(query)
    #     return result.scalar_one_or_none()


product_manager = ProductManager()