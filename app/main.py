from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import crud, schemas
from .database import get_db

app = FastAPI()


@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)


# Should return the same as rank
@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks_by_order(db: Session = Depends(get_db)):
    tasks = crud.get_tasks_by_order(db)
    return tasks


# Should return the same as order
@app.get("/tasks/rank", response_model=list[schemas.Task])
def read_tasks_by_rank(db: Session = Depends(get_db)):
    tasks = crud.get_tasks_by_rank(db)
    return tasks


@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = crud.update_task(db, task_id=task_id, task=task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    crud.delete_task(db, task_id=task_id)
    return {"message": "Task deleted successfully"}


@app.put("/tasks/move/{task_id}", response_model=schemas.Task)
def move_task(task_id: int, body: schemas.TaskMove, db: Session = Depends(get_db)):
    try:
        db_task = crud.move_task(
            db,
            task_id=task_id,
            prev_task_id=body.prev_task_id,
            next_task_id=body.next_task_id,
        )
    except IntegrityError as e:
        if "UNIQUE constraint failed" in e._message():
            raise HTTPException(
                status_code=500,
                detail="New order value exists. Check for reindexing or invalid input",
            )
        else:
            raise e
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task
