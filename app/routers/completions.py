from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models import HabitCompletion, Habit
from app.schemas import CompletionCreate, CompletionResponse
from app.security import get_current_user_id


router = APIRouter(
    prefix="/completions",
    tags=["Completions"]
)

@router.post("/{habit_id}", response_model=CompletionResponse)
def complete_habit(
    habit_id: int,
    completion: CompletionCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    habit = (
        db.query(Habit)
        .filter(
            Habit.id == habit_id,
            Habit.owner_id == user_id
        )
        .first()
    )

    if not habit:
        raise HTTPException(
            status_code=404,
            detail="Habit not found"
        )

    new_completion = HabitCompletion(
        habit_id=habit_id,
        date=completion.date
    )

    db.add(new_completion)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Habit already completed for this date"
        )

    db.refresh(new_completion)