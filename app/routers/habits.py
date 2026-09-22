from fastapi import APIRouter, Depends,HTTPException,Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Habit
from app.schemas import HabitCreate, HabitResponse, HabitUpdate, HabitListResponse
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
    owner_id=user_id,
    frequency=habit.frequency
)

    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)

    return new_habit

@router.get("/", response_model=HabitListResponse)
def get_habits(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    query = db.query(Habit).filter(Habit.owner_id == user_id)

    total = query.count()

    habits = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "items": habits,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    habit: HabitUpdate,
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

    if habit.name is not None:
     existing_habit.name = habit.name

    if habit.frequency is not None:
     existing_habit.frequency = habit.frequency

    db.commit()
    db.refresh(existing_habit)

    return existing_habit


@router.delete("/{habit_id}")
def delete_habit(
    habit_id: int,
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

    db.delete(existing_habit)
    db.commit()

    return {
        "message": "Habit deleted successfully"
    }

@router.get("/{habit_id}", response_model=HabitResponse)
def get_habit(
    habit_id: int,
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

    return habit