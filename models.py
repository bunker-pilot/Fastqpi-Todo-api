from database import Base
from sqlalchemy import Column, Integer, String, Boolean

class Todo(Base):
    __tablename__ = "todo"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(String ,nullable=True)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
