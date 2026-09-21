from fastapi import FastAPI
from app.routers import auth, completions, habits

app = FastAPI()

app.include_router(auth.router)
app.include_router(habits.router)
app.include_router(completions.router)

@app.get("/")
def root():
    return {"message": "Habit Tracker API"}