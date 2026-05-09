# Fleet Control System

Live ship control system for the Strait of Hormuz scenario. Built with Django and real-time services.

## Quick Start (Docker)

1. Create your environment file:
   - `cp .env.example .env`
2. Set your Postgres URL(s) in `.env`.
3. Run:
   - `docker compose up --build`
4. In a new terminal, run migrations and seed data:
   - `docker compose exec web python manage.py migrate`
   - `docker compose exec web python manage.py load_fleet`
5. Start the simulator (new terminal):
   - `docker compose exec web python manage.py run_simulation`

App URL: http://localhost:8000

## Local Development (without Docker)

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Run migrations:
   - `python manage.py migrate`
3. Load initial data:
   - `python manage.py load_fleet`
4. Start server:
   - `python manage.py runserver`
5. Start the simulator:
   - `python manage.py run_simulation`

## Environment Variables

- `Fleet212_POSTGRES_URL` or `Fleet212_PRISMA_DATABASE_URL` (recommended)
- `DATABASE_URL` (alternative name)
- `REDIS_URL` (required for WebSocket broadcasts across processes)

If no database URL is set, Django falls back to SQLite for local use.
