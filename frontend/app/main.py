from fastapi import FastAPI

from routers import router

def get_application() -> FastAPI:
    _app = FastAPI(
        debug=True
    )
    _app.include_router(router)
    return _app

app = get_application()