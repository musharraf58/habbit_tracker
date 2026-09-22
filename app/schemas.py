from pydantic import BaseModel, EmailStr,Field
from datetime import date,datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

    model_config = {
        "str_strip_whitespace": True
    }

class HabitCreate(BaseModel):
    name: str=Field( min_length=1, max_length=100)
    fequency: str ="daily"


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