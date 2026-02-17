from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory='templates')


@router.get("/")
async def index(requests: Request):
    context = {
        'request': requests
    }
    response = templates.TemplateResponse('pages/index.html', context=context)


    return response