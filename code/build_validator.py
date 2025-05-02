from pydantic import BaseModel, field_validator, model_validator
from typing import List
from datetime import time, date

class RoutineItem(BaseModel):
    activity_name: str
    category: str
    days: List[str]
    start_time: time
    end_time: time

    @field_validator("days")
    def check_valid_days(cls, v):
        valid = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
        if not all(d in valid for d in v):
            raise ValueError("Invalid weekday")
        return v
    
    @model_validator(mode="after")  
    def check_time_order(self):
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        return self

class TaskItem(BaseModel):
    task_name: str
    duration: float
    deadline: date
    priority: str

    @field_validator("priority")
    def check_priority(cls, v):
        if v not in {"Low", "Medium", "High"}:
            raise ValueError("Invalid priority level")
        return v

    @model_validator(mode="after")
    def check_deadline_not_past(self):
        if self.deadline < date.today():
            raise ValueError("Deadline cannot be in the past")
        return self

