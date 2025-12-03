from fastapi import FastAPI

from app.api.main import api_router


def create_app() -> FastAPI:
    app = FastAPI(title="AnotherMe TTS Server")
    app.include_router(api_router)
    return app


app = create_app()
