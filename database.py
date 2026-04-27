from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends

SQLALCHEMY_DB_URL = "sqlite:///todos.db"

engine = create_engine(SQLALCHEMY_DB_URL, connect_args={"check_same_thread":False})

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

