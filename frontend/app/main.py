from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import router


def get_application() -> FastAPI:
    _app = FastAPI(
        debug=True
    )
    _app.include_router(router)


    _app.mount("/static", StaticFiles(directory="static"), name="static")

    return _app


app = get_application()