from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Habit
from app.schemas import HabitCreate, HabitResponse
from app.security import get_current_user_id


router = APIRouter(
    prefix="/habits",
    tags=["Habits"]
)

@router.post("/", response_model=HabitResponse)
def create_habit(
    habit: HabitCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    new_habit = Habit(
        name=habit.name,
        owner_id=user_id
    )

    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)

    return new_habit