"""
Quick script to check input_history collection in MongoDB
"""
import asyncio
from app.database.connection import get_collection

async def check_input_history():
    """Check what's currently in the input_history collection"""
    collection = get_collection("input_history")
    
    print("Current input_history records:")
    print("=" * 50)
    
    cursor = collection.find({})
    count = 0
    async for doc in cursor:
        count += 1
        print(f"Record {count}:")
        print(f"  ID: {doc['_id']}")
        print(f"  User ID: {doc['user_id']}")
        print(f"  Words: {doc['words']}")
        print(f"  Created: {doc['created_at']}")
        print("-" * 30)
    
    if count == 0:
        print("No records found.")
    else:
        print(f"Total records: {count}")

if __name__ == "__main__":
    asyncio.run(check_input_history())