from fastapi import APIRouter, Depends,HTTPException
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

@router.get("/", response_model=list[HabitResponse])
def get_habits(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    habits = db.query(Habit).filter(Habit.owner_id == user_id).all()

    return habits


@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    habit: HabitCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    existing_habit = (
        db.query(Habit)
        .filter(
            Habit.id == habit_id,
            Habit.owner_id == user_id
        )
        .first()
    )

    if not existing_habit:
        raise HTTPException(
            status_code=404,
            detail="Habit not found"
        )

    existing_habit.name = habit.name

    db.commit()
    db.refresh(existing_habit)

    return existing_habit