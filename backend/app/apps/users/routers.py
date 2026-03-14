from typing import List
import uuid

from fastapi import APIRouter, status, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm

from apps.auth.auth_handler import auth_handler
from apps.users.schemas import (
    RegisterUserSchema,
    UserResponseSchema,
    NoteResponseSchema,
    NoteCreateSchema,
    UserBaseFieldsSchemas,
)
from apps.users.crud import user_manager, note_manager, User
from apps.auth.password_handler import PasswordHandler
from apps.core.dependencies import get_session, get_current_user
from apps.products.s3 import s3_service

users_router = APIRouter()
note_router = APIRouter()

@users_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_user(user_register_data: RegisterUserSchema, session=Depends(get_session)) -> UserResponseSchema:
    user = await user_manager.create_user(user_register_data=user_register_data, session=session)
    return user

@users_router.post('/login')
async def user_login(
    data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(    get_session   )
):
    user: User = await user_manager.get(session, data.username)
    if not user:
        raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

    is_password_valid = await PasswordHandler.verify_password(data.password, user.hashed_password)
    if not is_password_valid:
        raise HTTPException(detail="incorrect password", status_code=status.HTTP_400_BAD_REQUEST)

    return await auth_handler.get_access_token(user)

@users_router.get('/my-info')
async def get_my_info(user: User = Depends(get_current_user)) -> UserBaseFieldsSchemas:
    return user


@note_router.get('/', response_model=List[NoteResponseSchema])
async def list_notes(user: User = Depends(get_current_user), session=Depends(get_session)):
    return await note_manager.get_user_notes(session, user.id)


@note_router.post('/', response_model=NoteResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_note(
    name: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None),
    user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    image_url = None
    if image and image.filename:
        note_uuid = uuid.uuid4()
        image_url = s3_service.upload_file(image, product_uuid=note_uuid)

    note_data = NoteCreateSchema(name=name, content=content)
    return await note_manager.create_note(session, note_data, user.id, image_url=image_url)


@note_router.get('/{note_id}', response_model=NoteResponseSchema)
async def get_note(note_id: int, user: User = Depends(get_current_user), session=Depends(get_session)):
    note = await note_manager.get_note(session, note_id, user.id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='note not found')
    return note