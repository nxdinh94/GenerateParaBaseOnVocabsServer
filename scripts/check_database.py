"""
Check what data exists in the database
"""
import asyncio
from app.database.connection import connect_to_mongo, close_mongo_connection

async def check_database_data():
    """Check what data exists in database"""
    print("🔌 Connecting to MongoDB...")
    await connect_to_mongo()
    
    try:
        from app.database.crud import get_user_crud, get_input_history_crud, get_saved_paragraph_crud
        
        user_crud = get_user_crud()
        input_history_crud = get_input_history_crud()
        saved_paragraph_crud = get_saved_paragraph_crud()
        
        print("\n👥 Checking users...")
        default_user = await user_crud.get_user_by_id("68c13d6181373f816d763a41")
        if default_user:
            print(f"✓ Default user exists: {default_user.name} ({default_user.email})")
            user_id = str(default_user.id)
            
            print(f"\n📚 Checking input histories for user {user_id}...")
            histories = await input_history_crud.get_user_input_history(user_id, 10)
            print(f"✓ Found {len(histories)} input histories")
            
            for i, history in enumerate(histories, 1):
                print(f"   {i}. ID: {history.id}, Words: {history.words}")
                
                print(f"      📖 Checking paragraphs for history {history.id}...")
                paragraphs = await saved_paragraph_crud.get_paragraphs_by_input_history(str(history.id))
                print(f"      ✓ Found {len(paragraphs)} paragraphs")
                
                for j, paragraph in enumerate(paragraphs, 1):
                    print(f"         {j}. {paragraph.paragraph[:50]}...")
            
            print(f"\n📄 Checking user saved paragraphs with lookup...")
            user_paragraphs = await saved_paragraph_crud.get_user_saved_paragraphs(user_id, 10)
            print(f"✓ Found {len(user_paragraphs)} paragraphs with lookup")
            
            for i, item in enumerate(user_paragraphs, 1):
                print(f"   {i}. Paragraph ID: {item['_id']}")
                print(f"      Words: {item['input_history']['words']}")
                print(f"      Text: {item['paragraph'][:50]}...")
                
        else:
            print("❌ Default user not found")
            
            # Check all users
            print("\n👥 Checking all users...")
            all_user = await user_crud.get_user_by_email("default@example.com")
            if all_user:
                print(f"✓ Found user by email: {all_user.id}")
            else:
                print("❌ No default user found by email")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(check_database_data())
