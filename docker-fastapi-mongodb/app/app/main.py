import logging

from fastapi import FastAPI

from app.api.api_v1.api import api_router
from app.db.mongodb_utils import connect_to_mongo, close_mongo_connection
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()


app.include_router(api_router, prefix=settings.API_V1_STR)