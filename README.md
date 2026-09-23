# Habit Tracker API

A RESTful Habit Tracker API built with FastAPI and PostgreSQL.

## Features

- User registration and authentication
- JWT-based authentication
- Create, read, update, and delete habits
- Daily and weekly habit frequency
- Track habit completions
- Habit completion history
- Current and longest streaks
- Habit statistics and completion percentage
- Pagination
- Ownership-based access control
- Centralized error handling
- PostgreSQL database
- Alembic database migrations
- Docker and Docker Compose
- Automated tests with pytest
- GitHub Actions CI

## Tech Stack

- Python 3.10
- FastAPI
- PostgreSQL 16
- SQLAlchemy
- Alembic
- Pydantic
- JWT
- bcrypt
- Docker
- pytest
- GitHub Actions

## Run with Docker

Clone the repository and enter the project directory.

Start the application:

```bash
docker compose up -d
