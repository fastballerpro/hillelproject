from fastapi import Request, Depends, HTTPException, status

from apps.auth.auth_handler import auth_handler
from apps.core.base_model import async_session_maker
from apps.users.crud import user_manager
from apps.users.models import User
from fastapi.security import OAuth2PasswordBearer

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/users/login')

async def get_data_first():
    return 30


async def get_data(request: Request, first=Depends(get_data_first)):
    print(request)
    return 444+first

async def get_session():
   async with async_session_maker() as session:
        yield session

async def get_current_user(
        token: str = Depends(oauth2_schema),
        session = Depends(get_session)
) -> User:
    payload = await auth_handler.decode_token(token)

    user = await user_manager.get(session, payload['sub'])
    if not user:
        raise HTTPException(detail="User not authorized", status_code=status.HTTP_401_UNAUTHORIZED)
    return user