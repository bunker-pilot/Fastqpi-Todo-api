from fastapi import  APIRouter,HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from passlib.context import CryptContext
from starlette import status
import models
from database import db_dependency

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRequest(BaseModel):
    username: str = Field(min_length=4 , max_length=100)
    email:EmailStr
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=72)

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




def hash_password(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(password:str, hashed_pass:str) -> bool:
    return pwd_context.verify(password, hashed_pass)






@router.post("/api/register/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register_user(db: db_dependency, data:UserRequest):
    user = db.query(models.User).filter(
        (models.User.username == data.username) | (models.User.email == data.email)
    ).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username or email already exists")
    print(len(data.password.encode('utf-8')))
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
    db.refresh(new_user)
    return new_user
    

