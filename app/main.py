from fastapi import FastAPI, HTTPException
from starlette.staticfiles import StaticFiles
import os
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request
from app.middleware import add_middlewares
from app.database import create_tables, test_connection, migrate_schema
from app.logger import get_logger
from app.routes.restaurants import router as restaurants_router
from app.routes.search import router as search_router
from app.routes.auth_routes import router as auth_router
from app.routes.user import router as user_router
from app.routes.owner import router as owner_router

logger = get_logger(__name__)

app = FastAPI(
    title="Food Finder API", 
    version="0.1.0",
    description="API for food delivery and restaurant management",
    docs_url="/docs",
    redoc_url="/redoc"
)

add_middlewares(app)

@app.on_event("startup")
async def on_startup():
    logger.info("Starting up API")
    test_connection()
    create_tables()
    migrate_schema()

# Mount static uploads directory
uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(restaurants_router, prefix="/restaurants", tags=["restaurants"])
app.include_router(search_router, prefix="/search", tags=["search"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(owner_router, prefix="/owner", tags=["owner"])

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"success": False, "error": exc.errors()})


@app.get("/")
async def root():
    return {"success": True, "data": {"service": "food-finder"}}

