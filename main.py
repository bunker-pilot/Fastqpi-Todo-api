from fastapi import FastAPI, Depends
from fastapi_swagger import patch_fastapi
from starlette import status
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal



app = FastAPI(docs_url=None,swagger_ui_oauth2_redirect_url=None)
patch_fastapi(app,docs_url="/api/docs")

models.Base.metadata.create_all(bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length= 10)
    description:str = Field(max_length=400)
    priority : int = Field(gt=0 , le=5)
    complete : bool = Field()


class TodoResponse(TodoRequest):
    id: int

    class Config:
        from_attributes = True 



@app.get("/api/todos/", status_code=status.HTTP_200_OK, response_model=List[TodoResponse])
def get_todos(db:db_dependency):
    return db.query(models.Todo).all()

@app.post("/api/todos/" , status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
def create_todo(db:db_dependency, todo: TodoRequest):
    new_todo = models.Todo(**todo.model_dump())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo