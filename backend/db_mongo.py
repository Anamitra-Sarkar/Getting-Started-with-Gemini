"""MongoDB database initialization using Motor and Beanie for async operations."""
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import List

logger = logging.getLogger("backend.db_mongo")

# Global MongoDB client
_mongo_client: AsyncIOMotorClient = None


async def init_db(document_models: List):
    """
    Initialize MongoDB connection using Motor and Beanie.
    
    Args:
        document_models: List of Beanie Document classes to initialize
    
    Raises:
        Exception: If MONGODB_URI is not set or connection fails
    """
    global _mongo_client
    
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        raise ValueError("MONGODB_URI environment variable is required")
    
    try:
        # Create Motor client with connection timeout
        _mongo_client = AsyncIOMotorClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000,  # 5 second timeout for initial connection
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
        )
        
        # Get database - use get_default_database() for URI-specified database
        try:
            database = _mongo_client.get_default_database()
            db_name = database.name
        except Exception:
            # Fallback to explicit database name if not in URI
            db_name = "vaelis"
            database = _mongo_client[db_name]
        
        # Test connection with ping
        await database.command("ping")
        logger.info(f"MongoDB connection established to database: {db_name}")
        
        # Initialize Beanie with document models
        await init_beanie(database=database, document_models=document_models)
        logger.info("MongoDB / Beanie initialized successfully")
        
    except Exception as e:
        logger.exception(f"Failed to initialize MongoDB: {e}")
        raise


async def close_db():
    """Close MongoDB connection gracefully."""
    global _mongo_client
    
    if _mongo_client:
        _mongo_client.close()
        logger.info("MongoDB connection closed")


async def health_check() -> bool:
    """
    Check if MongoDB connection is healthy.
    
    Returns:
        bool: True if connection is healthy, False otherwise
    """
    global _mongo_client
    
    if not _mongo_client:
        return False
    
    try:
        # Ping the database to check connection
        await _mongo_client.admin.command("ping")
        return True
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        return False
