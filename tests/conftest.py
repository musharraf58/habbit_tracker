from dotenv import load_dotenv

load_dotenv(".env.test", override=True)

from app.database import Base, engine, SessionLocal
from app import models
import pytest


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield