from datetime import datetime, timedelta, timezone
from fastapi import  APIRouter,HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field, field_validator
from passlib.context import CryptContext
from starlette import status
from jose import jwt, JWTError
from typing import Annotated
import models
from database import db_dependency

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)
SECRET_KEY= "dGhpcy1pcy1hLXNlY3JldC1rZXktZm9yLWp3dC1zdGF5LXNhZmUtaXQtaXMtbG9uZy1lbm91Z2gK"
ALGORITHM = "HS256"




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/auth/token")



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

class Token(BaseModel):
    access_token : str
    token_type: str




def hash_password(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(password:str, hashed_pass:str) -> bool:
    return pwd_context.verify(password, hashed_pass)


def authenticate_user(username:str, password:str, db):
    user = db.query(models.User).filter((models.User.username == username)).first()
    if user is not None: 
        if verify_password(password, user.hashed_password):
            return user
    return None

def create_access_token(username: str, user_id:int,  expires_delta: timedelta):
    encode = {"sub" : username, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try: 
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="could not validate credentials")
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="could not validate credentials")



@router.post("/register/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
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
    

@router.post("/token/", status_code=status.HTTP_200_OK, response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                           db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password , db)
    if user is not None :
        token = create_access_token(user.username, user.id,timedelta(minutes=20) )
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="wrong username or password ")