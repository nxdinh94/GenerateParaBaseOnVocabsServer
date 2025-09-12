"""
Database initialization script
Creates indexes and initial data if needed
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def init_database():
    """Initialize database with indexes"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    
    print(f"Initializing database: {settings.MONGODB_DATABASE}")
    
    # Create indexes for users collection
    users_collection = db.users
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("created_at")
    print("✓ Created indexes for users collection")
    
    # Create indexes for input_history collection
    input_history_collection = db.input_history
    await input_history_collection.create_index("user_id")
    await input_history_collection.create_index("created_at")
    await input_history_collection.create_index([("user_id", 1), ("created_at", -1)])
    print("✓ Created indexes for input_history collection")
    
    # Create indexes for saved_paragraph collection
    saved_paragraph_collection = db.saved_paragraph
    await saved_paragraph_collection.create_index("input_history_id")
    await saved_paragraph_collection.create_index("created_at")
    await saved_paragraph_collection.create_index([("input_history_id", 1), ("created_at", -1)])
    print("✓ Created indexes for saved_paragraph collection")
    
    print("Database initialization completed!")
    client.close()

if __name__ == "__main__":
    asyncio.run(init_database())
