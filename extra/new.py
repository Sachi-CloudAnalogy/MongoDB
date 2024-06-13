from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List

app = FastAPI()

client = AsyncIOMotorClient('mongodb://localhost:27017')
database = client.my_database
collection = database.my_collection

class Item(BaseModel):
    name: str
    description: str

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    document = item.dict()
    result = await collection.insert_one(document)
    return document

@app.get("/items/", response_model=List[Item])
async def read_items():
    items = await collection.find().to_list(100)
    return items

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


#-------------------------------
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List
import os
from pymongo import MongoClient

app = FastAPI()

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class ItemModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
client = MongoClient(DATABASE_URL)
database = client.my_database
collection = database.my_collection

def get_collection():
    return collection

@app.post("/items/", response_model=ItemModel)
def create_item(item: ItemModel, collection = Depends(get_collection)):
    document = item.dict(by_alias=True)
    result = collection.insert_one(document)
    if result.inserted_id:
        document["_id"] = result.inserted_id
        return document
    raise HTTPException(status_code=400, detail="Item could not be created")

@app.get("/items/", response_model=List[ItemModel])
def read_items(collection = Depends(get_collection)):
    items = list(collection.find())
    return items

@app.get("/items/{item_id}", response_model=ItemModel)
def read_item(item_id: str, collection = Depends(get_collection)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId")
    item = collection.find_one({"_id": ObjectId(item_id)})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}", response_model=ItemModel)
def update_item(item_id: str, item: ItemModel, collection = Depends(get_collection)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId")
    result = collection.replace_one({"_id": ObjectId(item_id)}, item.dict(by_alias=True))
    if result.modified_count == 1:
        return read_item(item_id, collection)
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_id}", response_model=dict)
def delete_item(item_id: str, collection = Depends(get_collection)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId")
    result = collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 1:
        return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
