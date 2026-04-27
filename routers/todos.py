from fastapi import APIRouter,  Path, HTTPException
from starlette import status
from typing import List, Optional
from pydantic import BaseModel, Field
import models
from database import db_dependency


router = APIRouter(
    prefix="/api",
    tags=["todo"]
)




class TodoRequest(BaseModel):
    title: str = Field(min_length= 1)
    description:str | None = Field(max_length=400 , default=None)
    priority : int = Field(gt=0 , le=5)
    complete : bool


class TodoResponse(TodoRequest):
    id: int

    class Config:
        from_attributes = True 

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] =Field(None, max_length=400)
    priority: Optional[int] = Field(None, gt=0, le=5)
    complete: Optional[bool] = None



@router.get("/todos/", status_code=status.HTTP_200_OK, response_model=List[TodoResponse])
def get_todos(db:db_dependency):
    return db.query(models.Todo).all()

@router.post("/todos/" , status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
def create_todo(db:db_dependency, todo: TodoRequest):
    new_todo = models.Todo(**todo.model_dump())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoResponse)
def get_todo_by_id(db: db_dependency ,todo_id:int = Path(gt=0)):
    todo = db.get(models.Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
    return todo

@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_todo_by_id(db: db_dependency, todo_id:int = Path(gt=0)):
    todo = db.get(models.Todo , todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
    db.delete(todo)
    db.commit()

@router.put("/todos/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoResponse)
def update_todo(db: db_dependency,data: TodoRequest ,todo_id:int = Path(gt=0)):
    todo = db.get(models.Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
    
    todo.title = data.title
    todo.description = data.description
    todo.priority = data.priority
    todo.complete = data.complete

    db.commit()
    db.refresh(todo)
    return todo

@router.patch("/todos/{todo_id}" , status_code=status.HTTP_200_OK, response_model=TodoResponse)
def todo_partial_update(db:db_dependency, data:TodoUpdate, todo_id:int = Path(gt=0)):
    todo = db.get(models.Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
    
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(todo, field, value)

    db.commit()
    db.refresh(todo)
    return todo