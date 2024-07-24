from fastapi import FastAPI

from app.api.main import api_router
from app.core.database import engine

app = FastAPI()
app.include_router(api_router)

from sqlmodel import SQLModel
SQLModel.metadata.create_all(engine)