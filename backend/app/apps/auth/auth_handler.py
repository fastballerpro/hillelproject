from apps.users.models import User
from settings import settings
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import jwt


class AuthHandler:
    def __init__(self):
        self.secret = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM

    async def get_access_token(self, user: User) -> dict:
        now = datetime.now()
        payload = {
            "iat": now,
            "exp": now + timedelta(minutes=15),
            "sub": user.email
        }
        access_token = jwt.encode(
            payload,
            self.secret,
            algorithm=self.algorithm
        )
        return {
            "access_token": access_token
        }

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(detail='token expired', status_code=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            raise HTTPException(detail='token issuer not known', status_code=status.HTTP_401_UNAUTHORIZED)


auth_handler = AuthHandler()