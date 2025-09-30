from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from src.modules.db.engine import get_session
from src.routes.example import example_router
from src.settings import settings

@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield

app = FastAPI(
    title="KUS Backend",
    version="1.0.0",
    lifespan=lifespan,
    debug=(settings.environment == "develop"),
    dependencies=[Depends(get_session)],
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
)

app.include_router(example_router.router)