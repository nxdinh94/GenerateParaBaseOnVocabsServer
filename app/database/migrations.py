"""
MongoDB Schema Migration and Synchronization
Automatically syncs Pydantic models with MongoDB collections
"""
import asyncio
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
from datetime import datetime
import logging

from app.database.models import (
    UserInDB,
    InputHistoryInDB, 
    SavedParagraphInDB
)

logger = logging.getLogger(__name__)

class SchemaMigration:
    """Handles automatic schema synchronization with MongoDB"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collections_config = self._get_collections_config()
    
    def _get_collections_config(self) -> Dict[str, Dict[str, Any]]:
        """Define collection configurations with indexes and validation"""
        return {
            "users": {
                "model": UserInDB,
                "indexes": [
                    IndexModel([("email", ASCENDING)], unique=True, name="email_unique"),
                    IndexModel([("created_at", DESCENDING)], name="created_at_desc"),
                ],
                "validation": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["name", "email", "password", "created_at"],
                        "properties": {
                            "name": {
                                "bsonType": "string",
                                "minLength": 1,
                                "maxLength": 100,
                                "description": "User's full name"
                            },
                            "email": {
                                "bsonType": "string",
                                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                                "description": "User's email address"
                            },
                            "password": {
                                "bsonType": "string",
                                "minLength": 6,
                                "description": "Hashed password"
                            },
                            "created_at": {
                                "bsonType": "date",
                                "description": "Account creation timestamp"
                            }
                        }
                    }
                }
            },
            "input_history": {
                "model": InputHistoryInDB,
                "indexes": [
                    IndexModel([("user_id", ASCENDING)], name="user_id_asc"),
                    IndexModel([("created_at", DESCENDING)], name="created_at_desc"),
                    IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)], name="user_created_compound"),
                ],
                "validation": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["user_id", "words", "created_at"],
                        "properties": {
                            "user_id": {
                                "bsonType": "objectId",
                                "description": "Reference to user document"
                            },
                            "words": {
                                "bsonType": "array",
                                "minItems": 1,
                                "items": {
                                    "bsonType": "string"
                                },
                                "description": "List of input words"
                            },
                            "created_at": {
                                "bsonType": "date",
                                "description": "Input timestamp"
                            }
                        }
                    }
                }
            },
            "saved_paragraph": {
                "model": SavedParagraphInDB,
                "indexes": [
                    IndexModel([("input_history_id", ASCENDING)], name="input_history_id_asc"),
                    IndexModel([("created_at", DESCENDING)], name="created_at_desc"),
                    IndexModel([("input_history_id", ASCENDING), ("created_at", DESCENDING)], name="input_history_created_compound"),
                ],
                "validation": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["input_history_id", "paragraph", "created_at"],
                        "properties": {
                            "input_history_id": {
                                "bsonType": "objectId",
                                "description": "Reference to input history document"
                            },
                            "paragraph": {
                                "bsonType": "string",
                                "minLength": 1,
                                "description": "Generated paragraph content"
                            },
                            "created_at": {
                                "bsonType": "date",
                                "description": "Paragraph creation timestamp"
                            }
                        }
                    }
                }
            }
        }
    
    async def sync_all_collections(self, auto_create: bool = True, update_indexes: bool = True, update_validation: bool = True) -> Dict[str, bool]:
        """
        Synchronize all collections with their schemas
        
        Args:
            auto_create: Create collections if they don't exist
            update_indexes: Update/create indexes
            update_validation: Update validation rules
            
        Returns:
            Dict with sync status for each collection
        """
        results = {}
        
        logger.info("Starting schema synchronization...")
        
        for collection_name, config in self.collections_config.items():
            try:
                result = await self._sync_collection(
                    collection_name, 
                    config, 
                    auto_create, 
                    update_indexes, 
                    update_validation
                )
                results[collection_name] = result
                logger.info(f"✓ {collection_name}: {'Synced' if result else 'Skipped'}")
            except Exception as e:
                logger.error(f"✗ {collection_name}: Failed to sync - {e}")
                results[collection_name] = False
        
        logger.info(f"Schema synchronization completed. Results: {results}")
        return results
    
    async def _sync_collection(self, collection_name: str, config: Dict[str, Any], 
                              auto_create: bool, update_indexes: bool, update_validation: bool) -> bool:
        """Sync a single collection"""
        collection = self.db[collection_name]
        
        # Check if collection exists
        collections = await self.db.list_collection_names()
        collection_exists = collection_name in collections
        
        if not collection_exists and auto_create:
            await self._create_collection_with_validation(collection_name, config.get("validation"))
            logger.debug(f"Created collection: {collection_name}")
        elif not collection_exists:
            logger.debug(f"Skipped creating collection: {collection_name}")
            return False
        
        # Update indexes
        if update_indexes and "indexes" in config:
            await self._update_indexes(collection, config["indexes"])
        
        # Update validation rules
        if update_validation and collection_exists and "validation" in config:
            await self._update_validation(collection_name, config["validation"])
        
        return True
    
    async def _create_collection_with_validation(self, collection_name: str, validation: Optional[Dict[str, Any]]):
        """Create a collection with validation rules"""
        create_options = {}
        if validation:
            create_options["validator"] = validation
            create_options["validationLevel"] = "strict"
            create_options["validationAction"] = "error"
        
        await self.db.create_collection(collection_name, **create_options)
    
    async def _update_indexes(self, collection, indexes: List[IndexModel]):
        """Update collection indexes"""
        if not indexes:
            return
        
        try:
            # Get existing indexes
            existing_indexes = await collection.list_indexes().to_list(length=None)
            existing_index_names = {idx["name"] for idx in existing_indexes if idx["name"] != "_id_"}
            
            # Get new index names
            new_index_names = {idx.document["name"] for idx in indexes}
            
            # Drop indexes that are no longer needed
            for index_name in existing_index_names - new_index_names:
                try:
                    await collection.drop_index(index_name)
                    logger.debug(f"Dropped index: {index_name}")
                except Exception as e:
                    logger.warning(f"Failed to drop index {index_name}: {e}")
            
            # Create new indexes
            if indexes:
                await collection.create_indexes(indexes)
                logger.debug(f"Created/updated {len(indexes)} indexes")
        
        except Exception as e:
            logger.error(f"Failed to update indexes: {e}")
            raise
    
    async def _update_validation(self, collection_name: str, validation: Dict[str, Any]):
        """Update collection validation rules"""
        try:
            await self.db.command({
                "collMod": collection_name,
                "validator": validation,
                "validationLevel": "strict",
                "validationAction": "error"
            })
            logger.debug(f"Updated validation for: {collection_name}")
        except Exception as e:
            logger.warning(f"Failed to update validation for {collection_name}: {e}")
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get detailed information about a collection"""
        try:
            # Check if collection exists
            collections = await self.db.list_collection_names()
            if collection_name not in collections:
                return {"exists": False}
            
            collection = self.db[collection_name]
            
            # Get collection stats
            stats = await self.db.command("collStats", collection_name)
            
            # Get indexes
            indexes = await collection.list_indexes().to_list(length=None)
            
            # Get validation rules
            collection_info = await self.db.command("listCollections", filter={"name": collection_name})
            validation_info = {}
            if collection_info["cursor"]["firstBatch"]:
                options = collection_info["cursor"]["firstBatch"][0].get("options", {})
                if "validator" in options:
                    validation_info = {
                        "validator": options["validator"],
                        "validationLevel": options.get("validationLevel", "strict"),
                        "validationAction": options.get("validationAction", "error")
                    }
            
            return {
                "exists": True,
                "document_count": stats.get("count", 0),
                "size_bytes": stats.get("size", 0),
                "avg_document_size": stats.get("avgObjSize", 0),
                "indexes": [{"name": idx["name"], "key": idx["key"]} for idx in indexes],
                "validation": validation_info
            }
        
        except Exception as e:
            logger.error(f"Failed to get collection info for {collection_name}: {e}")
            return {"exists": False, "error": str(e)}
    
    async def validate_all_collections(self) -> Dict[str, Dict[str, Any]]:
        """Validate all collections and return their status"""
        results = {}
        
        for collection_name in self.collections_config.keys():
            results[collection_name] = await self.get_collection_info(collection_name)
        
        return results

async def auto_sync_schema(database: AsyncIOMotorDatabase, 
                          auto_create: bool = True,
                          update_indexes: bool = True, 
                          update_validation: bool = True) -> Dict[str, bool]:
    """
    Convenience function to automatically sync all schemas
    
    Args:
        database: MongoDB database instance
        auto_create: Create collections if they don't exist
        update_indexes: Update/create indexes  
        update_validation: Update validation rules
        
    Returns:
        Dict with sync status for each collection
    """
    migration = SchemaMigration(database)
    return await migration.sync_all_collections(auto_create, update_indexes, update_validation)
