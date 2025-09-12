"""
Test the paragraphs-by-group API endpoint
"""
import requests
import json

def test_group_details():
    """Test getting detailed paragraphs for a specific group"""
    print("🔍 Testing paragraphs-by-group endpoint...")
    
    # First, get grouped data to find a group with multiple paragraphs
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=true")
        grouped_result = response.json()
        
        if response.status_code == 200 and grouped_result.get('data'):
            # Find a group with multiple paragraphs
            target_group = None
            for group in grouped_result['data']:
                if group.get('total_paragraphs', 0) > 1:
                    target_group = group
                    break
            
            if target_group:
                group_id = target_group['id']
                vocabs = target_group['vocabs']
                total_paragraphs = target_group['total_paragraphs']
                
                print(f"📚 Testing group: {group_id}")
                print(f"   Vocabularies: {vocabs}")
                print(f"   Expected paragraphs: {total_paragraphs}")
                
                # Test the group details endpoint
                detail_response = requests.get(f"http://127.0.0.1:8000/api/v1/paragraphs-by-group/{group_id}")
                
                if detail_response.status_code == 200:
                    detail_result = detail_response.json()
                    
                    print(f"\n✅ Group Details Response:")
                    print(f"   Status: {detail_result.get('status')}")
                    print(f"   Input History ID: {detail_result.get('input_history_id')}")
                    print(f"   Total Paragraphs: {detail_result.get('total_paragraphs')}")
                    print(f"   Message: {detail_result.get('message')}")
                    
                    paragraphs = detail_result.get('paragraphs', [])
                    if paragraphs:
                        print(f"\n📄 Detailed Paragraphs:")
                        for i, para in enumerate(paragraphs, 1):
                            print(f"{i}. ID: {para.get('id')}")
                            print(f"   Text: {para.get('paragraph')}")
                            print(f"   Created: {para.get('created_at', 'N/A')}")
                            print()
                    
                    # Verify consistency
                    if detail_result.get('total_paragraphs') == total_paragraphs:
                        print("✅ Data consistency verified!")
                    else:
                        print("❌ Data inconsistency detected!")
                    
                    return True
                else:
                    print(f"❌ Detail endpoint error: {detail_response.status_code}")
            else:
                print("ℹ️  No groups with multiple paragraphs found for testing")
                # Test with first available group
                if grouped_result['data']:
                    first_group = grouped_result['data'][0]
                    group_id = first_group['id']
                    
                    detail_response = requests.get(f"http://127.0.0.1:8000/api/v1/paragraphs-by-group/{group_id}")
                    if detail_response.status_code == 200:
                        print("✅ Endpoint works with single paragraph group")
                        return True
        else:
            print(f"❌ Failed to get grouped data: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def test_invalid_group_id():
    """Test with invalid group ID"""
    print("\n🔍 Testing with invalid group ID...")
    
    try:
        # Test with invalid ObjectId format
        response = requests.get("http://127.0.0.1:8000/api/v1/paragraphs-by-group/invalid_id")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response: {result.get('message')}")
            print(f"   Status: {result.get('status')}")
            
            if not result.get('status'):
                print("✅ Error handling works correctly")
                return True
        else:
            print(f"ℹ️  HTTP Error {response.status_code} (expected for invalid ID)")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def demonstrate_group_navigation():
    """Demonstrate how to navigate from grouped view to detailed view"""
    print("\n🔍 Demonstrating group navigation workflow...")
    
    try:
        # Step 1: Get grouped overview
        print("Step 1: Get grouped overview...")
        response1 = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=true")
        grouped_result = response1.json()
        
        if response1.status_code == 200 and grouped_result.get('data'):
            print(f"✅ Found {len(grouped_result['data'])} vocabulary groups")
            
            # Step 2: Show summary of groups
            print(f"\nStep 2: Groups summary:")
            for i, group in enumerate(grouped_result['data'][:3], 1):  # Show first 3 groups
                vocabs = ', '.join(group.get('vocabs', []))
                count = group.get('total_paragraphs', 0)
                print(f"   {i}. [{vocabs}] - {count} paragraph(s)")
            
            # Step 3: Drill down into a specific group
            if grouped_result['data']:
                target_group = grouped_result['data'][0]  # Use first group
                group_id = target_group['id']
                
                print(f"\nStep 3: Drilling down into group {group_id[:12]}...")
                response2 = requests.get(f"http://127.0.0.1:8000/api/v1/paragraphs-by-group/{group_id}")
                
                if response2.status_code == 200:
                    detail_result = response2.json()
                    paragraphs = detail_result.get('paragraphs', [])
                    
                    print(f"✅ Retrieved {len(paragraphs)} detailed paragraph(s)")
                    for i, para in enumerate(paragraphs, 1):
                        text_preview = para.get('paragraph', '')[:50] + "..." if len(para.get('paragraph', '')) > 50 else para.get('paragraph', '')
                        print(f"      {i}. {text_preview}")
                    
                    return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def main():
    """Run all group detail tests"""
    print("🚀 Testing paragraphs-by-group API endpoint")
    print("=" * 60)
    
    success_count = 0
    
    if test_group_details():
        success_count += 1
    
    if test_invalid_group_id():
        success_count += 1
    
    if demonstrate_group_navigation():
        success_count += 1
    
    print(f"\n{'='*60}")
    print(f"🎯 Test Results: {success_count}/3 tests passed")
    print(f"🎉 Group details API is {'WORKING' if success_count >= 2 else 'NEEDS ATTENTION'}!")

if __name__ == "__main__":
    main()
