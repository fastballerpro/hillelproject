from fastapi import APIRouter, Request, Form, status, Depends, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import httpx

router = APIRouter()

templates = Jinja2Templates(directory='templates')


async def get_user(requests: Request) -> dict:
    access_token = requests.cookies.get('access_token')
    if not access_token:
        return {}
    async with httpx.AsyncClient() as client_login:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {access_token}"
        }

        response_login = await client_login.get('http://backend:8000/users/my-info', headers=headers)
        if response_login.status_code == 200:
            return response_login.json()
        return {}


@router.get('/')
async def index(requests: Request, user: dict = Depends(get_user)):
    context = {
        'user': user,
        'request': requests,
        'notes': []
    }

    if not user:
        return templates.TemplateResponse('pages/index.html', context=context)

    async with httpx.AsyncClient() as client:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {requests.cookies.get('access_token')}"
        }
        response = await client.get('http://backend:8000/notes/', headers=headers)
        if response.status_code == status.HTTP_200_OK:
            context['notes'] = response.json()

    return templates.TemplateResponse('pages/index.html', context=context)


@router.get('/notes/create')
@router.post('/notes/create')
async def create_note(
    requests: Request,
    user: dict = Depends(get_user),
    name: str = Form(''),
    content: str = Form(''),
    image: UploadFile | None = File(None),
):
    if not user:
        return RedirectResponse(requests.url_for('login'), status_code=status.HTTP_303_SEE_OTHER)

    context = {
        'request': requests,
        'user': user,
        'name': name,
        'content': content,
    }

    if requests.method == 'GET':
        return templates.TemplateResponse('pages/create_note.html', context=context)

    async with httpx.AsyncClient() as client:
        headers = {
            'accept': 'application/json',
            'Authorization': f"Bearer {requests.cookies.get('access_token')}"
        }

        data = {
            'name': name,
            'content': content,
        }
        files = {}
        if image and image.filename:
            files['image'] = (image.filename, await image.read(), image.content_type)

        response = await client.post('http://backend:8000/notes/', data=data, files=files, headers=headers)

    if response.status_code == status.HTTP_201_CREATED:
        return RedirectResponse(requests.url_for('index'), status_code=status.HTTP_303_SEE_OTHER)

    context['error'] = response.json().get('detail', 'Something went wrong')
    return templates.TemplateResponse('pages/create_note.html', context=context)


@router.get('/notes/{note_id}')
async def note_detail(requests: Request, note_id: int, user: dict = Depends(get_user)):
    if not user:
        return RedirectResponse(requests.url_for('login'), status_code=status.HTTP_303_SEE_OTHER)

    context = {
        'request': requests,
        'user': user,
        'note': None,
    }

    async with httpx.AsyncClient() as client:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {requests.cookies.get('access_token')}"
        }
        response = await client.get(f'http://backend:8000/notes/{note_id}', headers=headers)

    if response.status_code == status.HTTP_200_OK:
        context['note'] = response.json()
    else:
        context['error'] = response.json().get('detail', 'Note not found')

    return templates.TemplateResponse('pages/note.html', context=context)


@router.get('/sign-up')
@router.post('/sign-up')
async def user_register(requests: Request, user: dict = Depends(get_user), username: str = Form(''), email: str = Form(''), password: str = Form('')):
    if user:
        return RedirectResponse(requests.url_for('index'), status_code=status.HTTP_303_SEE_OTHER)
    context = {'request': requests}
    if requests.method == 'GET':
        return templates.TemplateResponse('pages/sign-up.html', context=context)

    async with httpx.AsyncClient() as client:
        headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
        json_data = {'password': password, 'email': email, 'name': username}
        response = await client.post('http://backend:8000/users/create', json=json_data, headers=headers)

    if response.status_code == status.HTTP_201_CREATED:
        redirect_response = RedirectResponse(requests.url_for('index'), status_code=status.HTTP_303_SEE_OTHER)
        async with httpx.AsyncClient() as client_login:
            headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
            json_data = {'password': password, 'username': email}
            response_login = await client_login.post('http://backend:8000/users/login', data=json_data, headers=headers)
        redirect_response.set_cookie('access_token', response_login.json()['access_token'], max_age=15 * 60)
        return redirect_response

    if response.status_code == status.HTTP_409_CONFLICT:
        context['username'] = username
        context['email'] = email
        context['error'] = "Користувач з таким email вже існує"
        return templates.TemplateResponse('pages/sign-up.html', context=context)


@router.get('/logout')
async def logout(requests: Request):
    redirect_response = RedirectResponse(requests.url_for('index'), status_code=status.HTTP_303_SEE_OTHER)
    redirect_response.delete_cookie('access_token')
    return redirect_response


@router.get('/login')
@router.post('/login')
async def login(requests: Request, user: dict = Depends(get_user), email: str = Form(''), password: str = Form('')):
    redirect_response = RedirectResponse(requests.url_for('index'), status_code=status.HTTP_303_SEE_OTHER)
    if user:
        return redirect_response
    context = {'request': requests, 'email': email}
    if requests.method == 'GET':
        return templates.TemplateResponse('pages/login.html', context=context)

    async with httpx.AsyncClient() as client_login:
        headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
        json_data = {'password': password, 'username': email}
        response_login = await client_login.post('http://backend:8000/users/login', data=json_data, headers=headers)

    if response_login.status_code == status.HTTP_404_NOT_FOUND:
        context['error'] = "Користувач з таким email не знайдений"
        return templates.TemplateResponse('pages/login.html', context=context)
    if response_login.status_code == status.HTTP_400_BAD_REQUEST:
        context['error'] = "перевірте введення паролю"
        return templates.TemplateResponse('pages/login.html', context=context)

    redirect_response.set_cookie('access_token', response_login.json()['access_token'], max_age=15 * 60)
    return redirect_response
