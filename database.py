from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


SQLALCHEMY_DB_URL = "sqlite:///todos.db"

engine = create_engine(SQLALCHEMY_DB_URL, connect_args={"check_same_thread":False})

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()



