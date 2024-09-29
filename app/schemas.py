from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, model_validator


class TaskBase(BaseModel):
    task_detail: str


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskMove(BaseModel):
    prev_task_id: Optional[int] = None
    next_task_id: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def check_xor(cls, data: Any) -> Any:
        if isinstance(data, dict):
            assert (
                "prev_task_id" in data or "next_task_id" in data
            ), "prev_task_id or next_task_id must be present in the body"
        return data


class Task(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order: float
    numerator: int
    denominator: int
    rank: str
