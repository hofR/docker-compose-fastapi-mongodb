from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from pydantic.types import UUID4

class ItemBase(BaseModel):
    name: str
    description: str
    price: float

class Item(ItemBase):
    id: str