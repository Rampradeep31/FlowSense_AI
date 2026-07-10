from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.api.router import api_router
from app.database import init_db, engine
from app.scheduler import start_scheduler, shutdown_scheduler
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up FlowSense AI Application...")
    await init_db()
    start_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down FlowSense AI Application...")
    shutdown_scheduler()
    await engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FlowSense AI: Intelligent Cold Chain Monitoring & Decision Support",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Register endpoints router
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
