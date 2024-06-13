from fastapi import APIRouter
from models import Todo
from database import collection
from schemas import list_serial
from bson import ObjectId

router = APIRouter()

# GET Request Method
@router.get("/")
async def get_todos():
    todos = list_serial(collection.find())
    return todos

# POST Request Method
@router.post("/create")
async def create_todo(todo: Todo):
    collection.insert_one(dict(todo))
    return "Todo added successfully !!"

# PUT Request Method
@router.put("/update/{id}")
async def update_todo(id: str, todo: Todo):
    collection.find_one_and_update({"_id": ObjectId(id)}, {"$set": dict(todo)})
    return "Todo updated Successfully !!"

# DELETE Request Method
@router.delete("/delete/{id}")
async def delete_todo(id: str):
    collection.find_one_and_delete({"_id": ObjectId(id)})
    return "Todo deleted Successfully !!"
