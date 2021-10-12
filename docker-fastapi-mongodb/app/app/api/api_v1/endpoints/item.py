from os import stat
from typing import List
from fastapi import APIRouter, Depends, Response, status
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.status import HTTP_204_NO_CONTENT, HTTP_304_NOT_MODIFIED, HTTP_404_NOT_FOUND

from app.db.mongodb import get_database
from app.schema.item import Item, ItemBase
from app.crud import item as crud_item

router = APIRouter()


@router.get("/{item_id}", response_model=Item,  status_code=status.HTTP_200_OK)
async def get_item(item_id: str,  db: AsyncIOMotorClient = Depends(get_database)):
    item = await crud_item.read_item(item_id, db)

    if item is None:
        return Response(status_code=HTTP_404_NOT_FOUND)
    else:
        return item

@router.get("/", response_model=List[Item], status_code=status.HTTP_200_OK)
async def get_all_items(skip: int = 0, limit: int = 100,  db: AsyncIOMotorClient = Depends(get_database)):
    items = await crud_item.get_all_items(skip, limit, db)
    return items

@router.post("",  response_model=Item, status_code=status.HTTP_201_CREATED)
async def post_item(item: ItemBase, db: AsyncIOMotorClient = Depends(get_database)):
    item = await crud_item.create_item(item, db)
    return item


@router.put("/{item_id}", response_model=Item, status_code=status.HTTP_200_OK)
async def update_item(item_id: str, item: ItemBase, db: AsyncIOMotorClient = Depends(get_database)):
    db_item= await crud_item.read_item(item_id, db)
    if db_item is None:
        return Response(status_code=HTTP_404_NOT_FOUND)


    item = await crud_item.update_item(item_id, item, db)
    if item is None:
        return Response(status_code=HTTP_304_NOT_MODIFIED)
    else:
        return item


@router.delete("/{item_id}")
async def delete_item(item_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    delete_count = await crud_item.delete_item(item_id, db)

    if delete_count == 0:
        return Response(status_code=HTTP_404_NOT_FOUND)
    else:
        return Response(status_code=HTTP_204_NO_CONTENT)
