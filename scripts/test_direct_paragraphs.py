"""
Simple test for the API without external HTTP calls
"""
import asyncio
from app.database.connection import connect_to_mongo, close_mongo_connection

async def test_get_all_paragraphs_direct():
    """Test getting all paragraphs directly from database"""
    print("🔌 Connecting to MongoDB...")
    await connect_to_mongo()
    
    try:
        from app.database.crud import get_saved_paragraph_crud
        
        saved_paragraph_crud = get_saved_paragraph_crud()
        default_user_id = "68c13d6181373f816d763a41"
        
        print(f"📚 Getting paragraphs for user: {default_user_id}")
        
        # Get user's saved paragraphs with input history info
        paragraphs_data = await saved_paragraph_crud.get_user_saved_paragraphs(default_user_id, 100)
        
        print(f"✅ Found {len(paragraphs_data)} paragraphs")
        
        if paragraphs_data:
            print(f"\n📄 All Paragraphs with Vocabularies:")
            for i, item in enumerate(paragraphs_data, 1):
                print(f"\n{i}. ID: {item['_id']}")
                print(f"   Vocabs: {item['input_history']['words']}")
                print(f"   Paragraph: {item['paragraph'][:100]}...")
                # Print all available keys to debug
                print(f"   Available keys: {list(item.keys())}")
                if 'created_at' in item:
                    print(f"   Created: {item['created_at']}")
                else:
                    print(f"   Created: Not available")
            
            # Summary
            all_vocabs = []
            for item in paragraphs_data:
                all_vocabs.extend(item['input_history']['words'])
            unique_vocabs = list(set(all_vocabs))
            
            print(f"\n📊 Summary:")
            print(f"   Total paragraphs: {len(paragraphs_data)}")
            print(f"   Total unique vocabularies: {len(unique_vocabs)}")
            print(f"   All unique vocabs: {unique_vocabs}")
            
        else:
            print("❌ No paragraphs found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_get_all_paragraphs_direct())
