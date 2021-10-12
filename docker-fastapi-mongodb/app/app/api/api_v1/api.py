from fastapi import APIRouter


from app.api.api_v1.endpoints import item

api_router = APIRouter()
api_router.include_router(item.router, prefix="/items", tags=["Items"])
