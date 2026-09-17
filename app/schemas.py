from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class HabitCreate(BaseModel):
    name: str


class HabitResponse(BaseModel):
    id: int
    name: str