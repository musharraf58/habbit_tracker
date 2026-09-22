from pydantic import BaseModel, EmailStr,Field,model_validator
from datetime import date,datetime
from typing import Literal


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

    model_config = {
        "str_strip_whitespace": True
    }

class HabitCreate(BaseModel):
    name: str=Field( min_length=1, max_length=100)
    frequency: Literal["daily", "weekly"] = "daily"


class HabitResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    frequency: str


class CompletionCreate(BaseModel):
    date: date


class CompletionResponse(BaseModel):
    id: int
    habit_id: int
    date: date

class HabitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    frequency: Literal["daily", "weekly"] | None = None

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        if self.name is None and self.frequency is None:
            raise ValueError("At least one field must be provided")
        return self


class HabitListResponse(BaseModel):
    items: list[HabitResponse]
    total: int
    skip: int
    limit: int

class CompletionListResponse(BaseModel):
    items: list[CompletionResponse]
    total: int
    skip: int
    limit: int