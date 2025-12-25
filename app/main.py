import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.dependencies import TTSDependencies

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = create_app()
