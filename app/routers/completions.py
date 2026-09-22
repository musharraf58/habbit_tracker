from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models import HabitCompletion, Habit
from app.schemas import CompletionCreate, CompletionResponse, CompletionListResponse
from app.security import get_current_user_id
from datetime import date, timedelta


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
    return new_completion

@router.get("/{habit_id}", response_model=CompletionListResponse)
def get_completions(
    habit_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
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

    query = (
        db.query(HabitCompletion)
        .filter(HabitCompletion.habit_id == habit_id)
    )

    total = query.count()

    completions = (
        query
        .order_by(HabitCompletion.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "items": completions,
        "total": total,
        "skip": skip,
        "limit": limit
    }



@router.get("/{habit_id}/streak")
def get_current_streak(
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

    completions = (
        db.query(HabitCompletion.date)
        .filter(HabitCompletion.habit_id == habit_id)
        .order_by(HabitCompletion.date.desc())
        .all()
    )

    if not completions:
        return {"current_streak": 0}

    completion_dates = {completion.date for completion in completions}

    today = date.today()

    if today not in completion_dates:
        return {"current_streak": 0}

    streak = 0
    current_date = today

    while current_date in completion_dates:
        streak += 1
        current_date -= timedelta(days=1)

    return {"current_streak": streak}


@router.get("/{habit_id}/longest-streak")
def get_longest_streak(
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

    completions = (
        db.query(HabitCompletion.date)
        .filter(HabitCompletion.habit_id == habit_id)
        .order_by(HabitCompletion.date)
        .all()
    )

    if not completions:
        return {"longest_streak": 0}

    completion_dates = sorted(
        {completion.date for completion in completions}
    )

    longest_streak = 1
    current_streak = 1

    for i in range(1, len(completion_dates)):
        if completion_dates[i] == completion_dates[i - 1] + timedelta(days=1):
            current_streak += 1
        else:
            current_streak = 1

        longest_streak = max(longest_streak, current_streak)

    return {"longest_streak": longest_streak}



@router.get("/{habit_id}/stats")
def get_habit_stats(
    habit_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
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

    query = (
    db.query(HabitCompletion)
    .filter(HabitCompletion.habit_id == habit_id)
)

    if start_date and end_date:
         days_in_period = (end_date - start_date).days + 1
    elif start_date:
         days_in_period = (date.today() - start_date).days + 1
    elif end_date:
         days_in_period = (end_date - habit.created_at.date()).days + 1
    else:
         days_in_period = (date.today() - habit.created_at.date()).days + 1

    total_completions = query.count()

    days_since_creation = (date.today() - habit.created_at.date()).days + 1

    completion_percentage = (
    total_completions / days_in_period
    ) * 100

    

    return {
     "habit_id": habit_id,
     "total_completions": total_completions,
     "days_in_period": days_in_period,
     "completion_percentage": round(completion_percentage, 2)
}


@router.delete("/{habit_id}/{completion_date}")
def delete_completion(
    habit_id: int,
    completion_date: date,
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

    completion = (
        db.query(HabitCompletion)
        .filter(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.date == completion_date
        )
        .first()
    )

    if not completion:
        raise HTTPException(
            status_code=404,
            detail="Completion not found"
        )

    db.delete(completion)
    db.commit()

    return {
        "message": "Habit completion deleted successfully"
    }