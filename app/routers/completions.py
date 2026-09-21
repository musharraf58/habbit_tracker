from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HabitCompletion
from app.schemas import CompletionCreate, CompletionResponse
from app.security import get_current_user_id


router = APIRouter(
    prefix="/completions",
    tags=["Completions"]
)