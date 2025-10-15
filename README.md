# Food Finder Backend (FastAPI)

FastAPI backend to find nearby and best food outlets. Supports mobile-number login with role selection (customer or restaurant_owner), restaurant management, and public search.

## Features
- Mobile number login with desired user_type at signin
- Multi-role users; a user can be both customer and restaurant_owner
- Restaurant CRUD (basic)
- Search: nearby, popular, new, by unique code
- SQLAlchemy 2.x ORM, pooled engine, auto table creation
- Pydantic v2 schemas, CORS, basic request logging

## Requirements
- Python 3.11+
- PostgreSQL (recommended) or SQLite

## Environment
Create `.env` in project root:

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/food_db
SECRET_KEY=replace_with_strong_secret
```

SQLite quick start:
```
DATABASE_URL=sqlite:///./food.db
SECRET_KEY=dev_secret_key
```

## Install & Run
```
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\uvicorn app.main:app --reload
```
Docs: http://127.0.0.1:8000/docs

## Key Endpoints
- POST `/auth/login`
  - Body: `{ "phone_number": "9999999999", "user_type": "customer" | "restaurant_owner" }`
  - Returns: `access_token`, `refresh_token`, `active_role`, `roles`
- Restaurants
  - POST `/restaurants`
  - GET `/restaurants`
  - GET `/restaurants/{id}`
  - PATCH `/restaurants/{id}`
  - DELETE `/restaurants/{id}`
- Search
  - GET `/search/nearby?lat=&lng=&radius_km=5`
  - GET `/search/popular`
  - GET `/search/new`
  - GET `/search/code/{unique_code}`

## Structure
```
app/
  main.py
  database.py
  models.py
  schemas.py
  auth.py
  routes/
    auth_routes.py
    restaurants.py
    search.py
  middleware.py
  logger.py
config.py
requirements.txt
```

## Notes
- Tables auto-create on startup; for teams, use Alembic migrations.
- SQLAlchemy 2.x: wrap raw SQL with `text("...")`.
- Pydantic v2: use `Field(pattern=...)` not `regex`.

## Alembic (optional)
```
venv\Scripts\alembic init alembic
# configure alembic.ini and env.py
venv\Scripts\alembic revision -m "init"
venv\Scripts\alembic upgrade head
```

## Troubleshooting
- Import error `app.mian:app` → use `app.main:app`
- DB ping error on startup → check `DATABASE_URL` and DB status
- Windows shell chaining → run commands separately
