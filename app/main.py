from fastapi import FastAPI

from app.endpoints import router
from app.database import Base, engine


def get_application() -> FastAPI:
    application = FastAPI()
    application.include_router(router)
    return application


Base.metadata.create_all(bind=engine)
app = get_application()

