# Fleet Control System

## Quick Start (Docker)

1. Copy the example environment file:
   - `cp .env.example .env`
2. Update `.env` with your Postgres URL.
3. Run:
   - `docker compose up --build`

The app will be available at http://localhost:8000

## Local Development (without Docker)

1. Create a virtual environment and install dependencies:
   - `pip install -r requirements.txt`
2. Run migrations:
   - `python manage.py migrate`
3. Load initial data:
   - `python manage.py load_fleet`
4. Start server:
   - `python manage.py runserver`
