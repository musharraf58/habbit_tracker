from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Date, UniqueConstraint,DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    habits = relationship("Habit", back_populates="owner")


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    frequency = Column(String, nullable=False, default="daily")

    owner = relationship("User", back_populates="habits")
    completions = relationship(
        "HabitCompletion",
        back_populates="habit",
        cascade="all, delete-orphan"
    )

class HabitCompletion(Base):
    __tablename__ = "habit_completions"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    date = Column(Date, nullable=False)

    habit = relationship("Habit", back_populates="completions")

    __table_args__ = (
        UniqueConstraint(
            "habit_id",
            "date",
            name="uq_habit_completion_date"
        ),
    )