"""
Test script to verify automatic schema synchronization
"""
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.database.migrations import SchemaMigration, auto_sync_schema

# Configure logging for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_schema_sync():
    """Test the schema synchronization functionality"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.MONGODB_DATABASE]
    
    try:
        # Test connection
        await client.admin.command('ping')
        logger.info(f"✓ Connected to MongoDB: {settings.MONGODB_DATABASE}")
        
        # Create schema migration instance
        migration = SchemaMigration(database)
        
        # Get initial collection info
        logger.info("\n=== BEFORE SYNC ===")
        before_info = await migration.validate_all_collections()
        for collection_name, info in before_info.items():
            if info.get("exists"):
                logger.info(f"{collection_name}: {info['document_count']} docs, {len(info['indexes'])} indexes")
            else:
                logger.info(f"{collection_name}: Does not exist")
        
        # Run schema synchronization
        logger.info("\n=== RUNNING SYNC ===")
        sync_results = await auto_sync_schema(
            database,
            auto_create=True,
            update_indexes=True,
            update_validation=True
        )
        
        # Get post-sync collection info
        logger.info("\n=== AFTER SYNC ===")
        after_info = await migration.validate_all_collections()
        for collection_name, info in after_info.items():
            if info.get("exists"):
                indexes_info = ", ".join([f"{idx['name']}" for idx in info['indexes']])
                validation_status = "✓" if info.get('validation') else "✗"
                logger.info(f"{collection_name}: {info['document_count']} docs, {len(info['indexes'])} indexes ({indexes_info}), validation: {validation_status}")
            else:
                logger.info(f"{collection_name}: Creation failed")
        
        # Summary
        logger.info("\n=== SYNC SUMMARY ===")
        success_count = sum(1 for result in sync_results.values() if result)
        total_count = len(sync_results)
        
        if success_count == total_count:
            logger.info(f"🎉 All collections synced successfully ({success_count}/{total_count})")
        else:
            logger.warning(f"⚠️  Partial sync completed ({success_count}/{total_count})")
            for collection, success in sync_results.items():
                status = "✓" if success else "✗"
                logger.info(f"   {status} {collection}")
        
        # Test validation by inserting test data
        logger.info("\n=== TESTING VALIDATION ===")
        await test_validation(database)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise
    finally:
        client.close()
        logger.info("Disconnected from MongoDB")

async def test_validation(database):
    """Test validation rules are working"""
    users_collection = database.users
    
    try:
        # Test valid document
        valid_user = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "created_at": "invalid_date_type"  # This should fail validation
        }
        
        try:
            await users_collection.insert_one(valid_user)
            logger.warning("⚠️  Validation may not be working - invalid date accepted")
        except Exception as e:
            logger.info("✓ Validation working - rejected invalid date format")
        
        # Test invalid email
        invalid_user = {
            "name": "Test User 2", 
            "email": "invalid-email",
            "password": "password123"
        }
        
        try:
            await users_collection.insert_one(invalid_user)
            logger.warning("⚠️  Email validation may not be working")
        except Exception as e:
            logger.info("✓ Email validation working - rejected invalid email")
            
        # Clean up any test documents
        await users_collection.delete_many({"name": {"$regex": "^Test User"}})
        
    except Exception as e:
        logger.error(f"Validation test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_schema_sync())