from fastapi import FastAPI
from app.middleware import add_middlewares
from app.database import create_tables, test_connection
from app.logger import get_logger
from app.routes.restaurants import router as restaurants_router
from app.routes.search import router as search_router
from app.routes.auth_routes import router as auth_router

logger = get_logger(__name__)

app = FastAPI(title="Food Finder API", version="0.1.0")

add_middlewares(app)

@app.on_event("startup")
async def on_startup():
    logger.info("Starting up API")
    test_connection()
    create_tables()

app.include_router(restaurants_router, prefix="/restaurants", tags=["restaurants"])
app.include_router(search_router, prefix="/search", tags=["search"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"status": "ok", "service": "food-finder"}

