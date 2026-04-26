from fastapi import  APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from passlib.context import CryptContext
from database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
import models
from typing import Annotated

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRequst(BaseModel):
    username: str = Field(min_length=4 , max_length=100)
    email:EmailStr
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=6, max_length=100)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    role: str
    
    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]

def hash_password(password:str) -> str:
    return pwd_context(password)

def verify_password(password:str, hashed_pass:str) -> bool:
    return pwd_context.verify(password, has_password)






@router.get("/api/register/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register_user(db: db_dependency, data:UserRequst):
    user = db.query(models.User).filter(
        (models.User.username == data.username) | (models.User.email == data.email)
    ).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username or email already exists")
    
    hash_pass = hash_password(data.password)

    new_user = models.User(
        username = data.username,
        email = data.email,
        hashed_password = hash_pass,
        first_name = data.first_name,
        last_name = data.last_name,
        role = "user"
    )
    db.add(new_user)
    db.commit()
    return new_user
    



