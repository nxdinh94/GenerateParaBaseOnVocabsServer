"""
Test the all-paragraphs API and display results nicely
"""
import json
import subprocess

def test_all_paragraphs():
    """Test the all-paragraphs API using PowerShell"""
    try:
        print("🔍 Testing All Paragraphs API...")
        
        # Use PowerShell to call the API and get JSON
        ps_command = [
            "powershell", "-Command",
            'Invoke-RestMethod -Uri "http://localhost:8000/api/v1/all-paragraphs" -Method Get | ConvertTo-Json -Depth 10'
        ]
        
        result = subprocess.run(ps_command, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            # Parse the JSON response
            data = json.loads(result.stdout)
            
            print(f"✅ API Response:")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Total: {data.get('total', 'N/A')}")
            
            if 'data' in data and data['data']:
                print(f"\n📄 All Saved Paragraphs:")
                
                for i, item in enumerate(data['data'], 1):
                    print(f"\n{i}. ID: {item.get('id', 'N/A')[:8]}...")
                    print(f"   Vocabularies: {item.get('vocabs', [])}")
                    print(f"   Paragraph: {item.get('paragraph', '')[:100]}...")
                
                # Summary
                all_vocabs = []
                for item in data['data']:
                    all_vocabs.extend(item.get('vocabs', []))
                unique_vocabs = list(set(all_vocabs))
                
                print(f"\n📊 Summary:")
                print(f"   Total paragraphs: {len(data['data'])}")
                print(f"   Total unique vocabularies: {len(unique_vocabs)}")
                print(f"   All unique vocabs: {unique_vocabs}")
                
                print(f"\n✅ API '/all-paragraphs' is working successfully!")
                return True
            else:
                print("   No paragraphs found")
                
        else:
            print(f"❌ PowerShell command failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_save_paragraph():
    """Test saving a new paragraph"""
    try:
        print(f"\n🔄 Testing Save Paragraph API...")
        
        # Prepare test data
        test_data = {
            "vocabs": ["test", "api", "success"],
            "paragraph": "This is a test to verify that our API works successfully for saving and retrieving paragraphs."
        }
        
        # Convert to JSON for PowerShell
        json_data = json.dumps(test_data).replace('"', '\\"')
        
        ps_command = [
            "powershell", "-Command",
            f'Invoke-RestMethod -Uri "http://localhost:8000/api/v1/save-paragraph" -Method Post -ContentType "application/json" -Body \\"{json_data}\\" | ConvertTo-Json'
        ]
        
        result = subprocess.run(ps_command, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get('status'):
                print(f"✅ Successfully saved paragraph:")
                print(f"   Input History ID: {data.get('input_history_id')}")
                print(f"   Saved Paragraph ID: {data.get('saved_paragraph_id')}")
                print(f"   Message: {data.get('message')}")
                return True
            else:
                print(f"❌ Save failed: {data.get('message')}")
        else:
            print(f"❌ Save command failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error saving paragraph: {e}")
        
    return False

if __name__ == "__main__":
    print("🚀 Testing English Server APIs...\n")
    
    # Test get all paragraphs
    if test_all_paragraphs():
        # Test save paragraph
        if test_save_paragraph():
            # Test get all again to see the new paragraph
            print(f"\n🔄 Testing get all paragraphs again after saving...")
            test_all_paragraphs()
    
    print(f"\n🎉 API testing completed!")
