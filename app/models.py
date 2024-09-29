from sqlalchemy import Column, Integer, String

from .database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    task_detail = Column(String)
    numerator = Column(Integer)
    denominator = Column(Integer)
    order = Column(Integer, unique=True, index=True)
    rank = Column(String, unique=True, index=True)
