import logging
from typing import List, Union

from app.api.api_v1.endpoints import item
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from uuid import uuid4

from app.core.config import settings
from app.schema.item import Item, ItemBase

ID = "_id"

log = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)


async def create_item(item: ItemBase, db: AsyncIOMotorClient) -> Item:
    collection = _get_collection(db)
    document = vars(item)
    document[ID] = str(uuid4())

    result = await collection.insert_one(document)
    return Item(id=result.inserted_id, **document)

async def get_all_items(skip: int, limit: int, db: AsyncIOMotorClient) -> List[Item]:
    collection = _get_collection(db)
    items = []
    for result in (await collection.find().skip(skip).to_list(length=limit)):
        item = Item(**result, id=result[ID])
        items.append(item)

    return items

async def read_item(id: str, db: AsyncIOMotorClient) -> Union[Item, None]:
    collection = _get_collection(db)
    item = await collection.find_one({ID: id})

    return None if item is None else Item(id=item[ID], **item)

async def update_item(id: str, item: ItemBase, db: AsyncIOMotorClient) -> Union[Item, None]:
    collection = _get_collection(db)
    document = vars(item)
    result = await collection.update_one({ID: id}, {'$set': document})
    
    if result.modified_count == 0:
        return None
    else:
        return Item(id=id, **document)

async def delete_item(id: str, db: AsyncIOMotorClient) -> int:
    collection = _get_collection(db)
    result = await collection.delete_many({ID: id})
    return result.deleted_count

def _get_collection(db: AsyncIOMotorClient) -> AsyncIOMotorCollection:
    return db[settings.MONGODB_DATABASE][settings.MONGODB_COLLECTION]