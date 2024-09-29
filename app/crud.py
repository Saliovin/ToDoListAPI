import math
from sqlalchemy.orm import Session

from app.utils import get_mid_fraction, get_mid_rank

from . import models, schemas


def get_tasks_by_order(db: Session):
    return db.query(models.Task).order_by(models.Task.order).all()


def get_tasks_by_rank(db: Session):
    return db.query(models.Task).order_by(models.Task.rank).all()


def create_task(db: Session, task: schemas.TaskCreate):
    # Both fractional and lexorank are calculated to demonstrate their capability
    # You can remove one for the other

    last_task = db.query(models.Task).order_by(models.Task.order.desc()).first()
    if last_task:
        numerator = math.floor(last_task.order + 1)
        rank = get_mid_rank(last_task.rank)
    else:
        numerator = 1
        rank = "i"
    db_task = models.Task(
        task_detail=task.task_detail,
        numerator=numerator,
        denominator=1,
        order=numerator,
        rank=rank,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task: schemas.TaskUpdate):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return None
    for key, value in task:
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()


def move_task(db: Session, task_id: int, prev_task_id: int, next_task_id: int):
    # Both fractional and lexorank are calculated to demonstrate their capability
    # You can remove one for the other

    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if prev_task_id:
        db_prev_task = (
            db.query(models.Task)
            .filter(models.Task.id == prev_task_id)
            .first()
            .__dict__
        )
    else:
        db_prev_task = {"numerator": 0, "denominator": 1, "rank": "0"}
    if next_task_id:
        db_next_task = (
            db.query(models.Task)
            .filter(models.Task.id == next_task_id)
            .first()
            .__dict__
        )
    else:
        db_next_task = {"numerator": 1, "denominator": 0, "rank": "z"}
    if not db_task or not db_prev_task or not db_next_task:
        return None

    numerator, denominator = get_mid_fraction(
        prev_fraction=db_prev_task, next_fraction=db_next_task
    )
    rank = get_mid_rank(prev_rank=db_prev_task["rank"], next_rank=db_next_task["rank"])

    db_task.numerator = numerator
    db_task.denominator = denominator
    db_task.order = numerator / denominator
    db_task.rank = rank
    db.commit()
    db.refresh(db_task)
    return db_task
