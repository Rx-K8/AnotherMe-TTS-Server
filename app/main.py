import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.main import api_router
from app.dependencies import TTSDependencies

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """アプリケーション起動時の初期化処理"""
    logger.info("依存関係の初期化を開始します...")
    TTSDependencies.initialize()
    logger.info("依存関係の初期化が完了しました")

    yield

    logger.info("依存関係をリセットします...")
    TTSDependencies.reset()
    logger.info("依存関係のリセットが完了しました。")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AnotherMe TTS Server",
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app


app = create_app()
