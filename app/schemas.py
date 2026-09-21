from pydantic import BaseModel, EmailStr
from datetime import date


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class HabitCreate(BaseModel):
    name: str


class HabitResponse(BaseModel):
    id: int
    name: str


class CompletionCreate(BaseModel):
    date: date


class CompletionResponse(BaseModel):
    id: int
    habit_id: int
    date: date