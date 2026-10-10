from contextlib import asynccontextmanager

from fastapi import FastAPI

from nasd.api.router import api_router
from nasd.database import init_db
from nasd.errors import Problem, problem_exception_handler
from nasd.seed import load_seed_from_files
from nasd.database import get_session_factory


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    db = get_session_factory()()
    try:
        load_seed_from_files(db)
    finally:
        db.close()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="OpenNAS-Lite nasd",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_exception_handler(Problem, problem_exception_handler)
    app.include_router(api_router)

    @app.get("/healthz")
    def healthz() -> dict:
        return {"status": "ok"}

    return app
