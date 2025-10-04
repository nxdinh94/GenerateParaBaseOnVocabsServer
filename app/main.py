from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.api.v1.routes import router as v1_router
from app.database.connection import connect_to_mongo, close_mongo_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting English Learning API server...")
    await connect_to_mongo()
    logger.info("Server startup completed")
    yield
    # Shutdown  
    logger.info("Shutting down server...")
    await close_mongo_connection()
    logger.info("Server shutdown completed")

app = FastAPI(
    title="English Learning API",
    description="API for generating learning content with Gemini",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Include API v1 routes
app.include_router(v1_router)
