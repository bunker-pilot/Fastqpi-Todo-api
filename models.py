from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ ="user"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    role = Column(String)
    todos = relationship("Todo" , back_populates="owner", cascade="all, delete-orphan")

class Todo(Base):
    __tablename__ = "todo"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(String ,nullable=True)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer,ForeignKey("user.id") , index=True)
    owner = relationship("User", back_populates="todos")