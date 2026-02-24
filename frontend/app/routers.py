from fastapi import APIRouter, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import httpx

router = APIRouter()

templates = Jinja2Templates(directory='templates')


@router.get("/")
async def index(requests: Request):
    context = {
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
            return redirect_response
        elif response.status_code == status.HTTP_409_CONFLICT:
            context['username'] = username
            context['email'] = email
            context['error'] = "Користувач з таким email вже існує"
            response = templates.TemplateResponse('pages/sign-up.html', context=context)
            return response