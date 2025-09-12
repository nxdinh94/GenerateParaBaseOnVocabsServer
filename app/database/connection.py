"""
MongoDB connection setup using Motor (async MongoDB driver)
"""
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

# Global MongoDB instance
mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.database = mongodb.client[settings.MONGODB_DATABASE]
    
    # Test connection
    try:
        await mongodb.client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB: {settings.MONGODB_DATABASE}")
        
        # Auto-sync schema if enabled
        if settings.AUTO_SYNC_SCHEMA:
            from app.database.migrations import auto_sync_schema
            
            logger.info("Starting automatic schema synchronization...")
            sync_results = await auto_sync_schema(
                mongodb.database,
                auto_create=settings.AUTO_CREATE_COLLECTIONS,
                update_indexes=settings.AUTO_UPDATE_INDEXES,
                update_validation=settings.AUTO_UPDATE_VALIDATION
            )
            
            success_count = sum(1 for result in sync_results.values() if result)
            total_count = len(sync_results)
            
            if success_count == total_count:
                logger.info(f"✅ Schema sync completed successfully ({success_count}/{total_count} collections)")
            else:
                logger.warning(f"⚠️ Schema sync partially completed ({success_count}/{total_count} collections)")
                for collection, success in sync_results.items():
                    if not success:
                        logger.warning(f"   Failed: {collection}")
        else:
            logger.info("Automatic schema synchronization is disabled")
            
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return mongodb.database

def get_collection(collection_name: str):
    """Get collection by name"""
    return mongodb.database[collection_name]
