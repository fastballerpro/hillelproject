from fastapi import APIRouter, Request, Form, status, Depends
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

@router.get("/")
async def index(requests: Request, user: dict = Depends(get_user)):
    context = {
        "user": user,
        'request': requests
    }
    response = templates.TemplateResponse('pages/index.html', context=context)


    return response


@router.get("/sign-up")
@router.post("/sign-up")
async def user_register(requests: Request, username: str = Form(""), email: str = Form(""), password: str = Form("")):
    context = {
        'request': requests
    }
    if requests.method == "GET":
        response = templates.TemplateResponse('pages/sign-up.html', context=context)
        return response

    async with httpx.AsyncClient() as client:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        json_data = {
            'password': password,
            'email': email,
            'name': username,
        }
        response = await client.post('http://backend:8000/users/create', json=json_data, headers=headers)

        if response.status_code == status.HTTP_201_CREATED:
            redirect_response = RedirectResponse(requests.url_for("index"), status_code=status.HTTP_303_SEE_OTHER)

            async with httpx.AsyncClient() as client_login:
                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded',
                }

                json_data = {
                    'password': password,
                    'username': email,
                }
                response_login = await client_login.post('http://backend:8000/users/login', data=json_data,
                                                         headers=headers)
            redirect_response.set_cookie('access_token', response_login.json()['access_token'], max_age=15 * 60)

            return redirect_response
        elif response.status_code == status.HTTP_409_CONFLICT:
            context['username'] = username
            context['email'] = email
            context['error'] = "Користувач з таким email вже існує"
            response = templates.TemplateResponse('pages/sign-up.html', context=context)
            return response

@router.get("/logout")
async def logout(requests: Request):
    redirect_response = RedirectResponse(requests.url_for("index"), status_code=status.HTTP_303_SEE_OTHER)
    redirect_response.delete_cookie('access_token')
    return redirect_response

@router.get("/login")
@router.post("/login")
async def login(requests: Request, username: str = Form(""), email: str = Form(""), password: str = Form("")):
    context = {
        'request': requests
    }

    if requests.method == "GET":
        response = templates.TemplateResponse('pages/login.html', context=context)
        return response