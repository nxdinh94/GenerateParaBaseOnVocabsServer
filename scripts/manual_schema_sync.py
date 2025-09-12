"""
Manual schema synchronization script
Use this to manually sync schemas without starting the full server
"""
import asyncio
import logging
import argparse
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.database.migrations import SchemaMigration, auto_sync_schema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def manual_sync(
    auto_create: bool = True,
    update_indexes: bool = True,
    update_validation: bool = True,
    show_info: bool = False
):
    """Manually run schema synchronization"""
    
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.MONGODB_DATABASE]
    
    try:
        # Test connection
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.MONGODB_DATABASE}")
        
        # Show collection info before sync if requested
        if show_info:
            migration = SchemaMigration(database)
            logger.info("\n=== COLLECTION INFO BEFORE SYNC ===")
            info = await migration.validate_all_collections()
            for collection_name, details in info.items():
                if details.get("exists"):
                    logger.info(f"{collection_name}: ✓ exists ({details['document_count']} docs, {len(details['indexes'])} indexes)")
                else:
                    logger.info(f"{collection_name}: ✗ does not exist")
        
        # Run synchronization
        logger.info(f"\n=== RUNNING SYNC ===")
        logger.info(f"Options: create={auto_create}, indexes={update_indexes}, validation={update_validation}")
        
        sync_results = await auto_sync_schema(
            database,
            auto_create=auto_create,
            update_indexes=update_indexes,
            update_validation=update_validation
        )
        
        # Show results
        logger.info("\n=== SYNC RESULTS ===")
        success_count = sum(1 for result in sync_results.values() if result)
        total_count = len(sync_results)
        
        for collection, success in sync_results.items():
            status = "✓" if success else "✗"
            logger.info(f"{status} {collection}")
        
        if success_count == total_count:
            logger.info(f"\n🎉 Schema sync completed successfully ({success_count}/{total_count} collections)")
        else:
            logger.warning(f"\n⚠️ Schema sync partially completed ({success_count}/{total_count} collections)")
        
        # Show collection info after sync if requested
        if show_info:
            migration = SchemaMigration(database)
            logger.info("\n=== COLLECTION INFO AFTER SYNC ===")
            info = await migration.validate_all_collections()
            for collection_name, details in info.items():
                if details.get("exists"):
                    validation_status = "✓" if details.get('validation') else "✗"
                    logger.info(f"{collection_name}: ✓ exists ({details['document_count']} docs, {len(details['indexes'])} indexes, validation: {validation_status})")
                else:
                    logger.info(f"{collection_name}: ✗ does not exist")
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        raise
    finally:
        client.close()
        logger.info("Disconnected from MongoDB")

def main():
    parser = argparse.ArgumentParser(description="Manual MongoDB schema synchronization")
    parser.add_argument("--no-create", action="store_true", help="Don't auto-create collections")
    parser.add_argument("--no-indexes", action="store_true", help="Don't update indexes")
    parser.add_argument("--no-validation", action="store_true", help="Don't update validation rules")
    parser.add_argument("--info", action="store_true", help="Show detailed collection info before and after")
    
    args = parser.parse_args()
    
    asyncio.run(manual_sync(
        auto_create=not args.no_create,
        update_indexes=not args.no_indexes,
        update_validation=not args.no_validation,
        show_info=args.info
    ))

if __name__ == "__main__":
    main()