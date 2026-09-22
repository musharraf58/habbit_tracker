from fastapi import FastAPI, HTTPException
from app.routers import auth, completions, habits
from app.exceptions import http_exception_handler

app = FastAPI()

app.include_router(auth.router)
app.include_router(habits.router)
app.include_router(completions.router)
app.add_exception_handler(
    HTTPException,
    http_exception_handler
)

@app.get("/")
def root():
    return {"message": "Habit Tracker API"}