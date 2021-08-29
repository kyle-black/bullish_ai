from fastapi import FastAPI, Path, Query

from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# GET return information
# POSt creating something new creating data
# PUT update something in database
# DELETE delete something in database


class Item(BaseModel):
    name: str
    price: Optional[float] = None


inventory = {}


@app.get("/get-item/{item_id}")
def get_item(item_id: int = Path(None, description="The ID of the item that you need:")):
    return inventory[item_id]


@app.get("/get-by-name/")
def get_item(*, name: str = Query(None, title="Name", description="Name of item.")):
    for item_id in inventory:
        if inventory[item_id].name == name:
            return inventory[item_id]
    return {"Data": "Not Found"}


@app.post("/create-item/{item_id}")
def create_item(item_id: int, item: Item):
    if item_id in inventory:

        return{"Error:": "Item Id already exists"}
    inventory[item_id] = item
    return inventory[item_id]
