from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, JSONResponse
from app.core.config import get_settings, get_logger
from app.db.session import init_db, drop_db, Add_Ibotix_Admin
from app.db.models import *
from app.routes.auth import router as auth_router
from app.routes.refresh import router as refresh_router
from app.routes.services import router as services_router
from app.utility.CustomException import CustomHttpException
from starlette.status import HTTP_301_MOVED_PERMANENTLY
from fastapi.requests import Request
from contextlib import asynccontextmanager

# Import Logger and Environment Variables
logger = get_logger()
settings = get_settings()  

# Origin
origins = [
    'http://localhost',
    'http://localhost:8000',
    'http://localhost:3000',
    'http://localhost:8080'
]

# Lifespan manager to handle startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    """
    Asynchronous context manager to handle the lifespan of a FastAPI application.
    
    This function initializes the database on startup, yields control to let the application run, 
    and performs cleanup tasks on shutdown.

    Parameters:
        app (FastAPI): The FastAPI application instance.

    Returns:
        None
    """
    
    # Startup event: Initialize database
    logger.info("Starting up: Initializing the database")
    await init_db()
    await Add_Ibotix_Admin()

    # Yield to let the application run
    yield

    # Shutdown event: Perform any cleanup tasks
    logger.info("Shutting down: Cleaning up resources & Dropping DB")
    await drop_db()

# Initialize FastAPI with the lifespan manager
app = FastAPI(lifespan=lifespan)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Include auth routes
# Include auth routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(refresh_router, prefix="/auth", tags=["auth"])
app.include_router(services_router, prefix="/api/services", tags=["Services"])

# Custom Exception Handler
@app.exception_handler(CustomHttpException)
async def custom_exception_handler(request: Request, exc: CustomHttpException):
    
    """
    Handles CustomHttpException instances by logging the error and returning a JSON response 
    with the exception details.

    Parameters:
        request (Request): The incoming request that triggered the exception.
        exc (CustomHttpException): The CustomHttpException instance containing the error details.

    Returns:
        JSONResponse: A JSON response with the exception status code, detail, message, and headers.
    """
    
    logger.error(f"Exception occurred: {exc}")
    return JSONResponse(
        content={"status_code": exc.status_code,
                 "detail": exc.detail,
                 "message": exc.message},
        status_code=exc.status_code,
        headers=exc.headers
    )

# Root test route
@app.get("/", tags=['Documentation'])
async def root():
  
    """
    Handles HTTP GET requests to the root endpoint.

    Returns a RedirectResponse with a status code of 301, redirecting the client to the /docs endpoint.
    """
  
    return RedirectResponse(url='/docs', status_code=HTTP_301_MOVED_PERMANENTLY)