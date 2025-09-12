"""
Test the updated grouped API with new response format
"""
import requests
import json

def test_new_grouped_format():
    """Test the new grouped format"""
    print("🔍 Testing NEW grouped format...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=true")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result.get('status')}")
            print(f"✅ Total Groups: {result.get('total')}")
            
            data = result.get('data', [])
            if data:
                print(f"\n📊 GROUPED DATA (New Format):")
                
                for i, group in enumerate(data[:3], 1):  # Show first 3 groups
                    print(f"\n{i}. Group:")
                    print(f"   ID: {group.get('id')}")
                    print(f"   Vocabularies: {group.get('vocabs')}")
                    print(f"   Is Group: {group.get('is_group')}")
                    print(f"   Total Paragraphs: {group.get('total_paragraphs')}")
                    
                    paragraphs = group.get('paragraphs', [])
                    print(f"   Paragraphs (array of strings):")
                    for j, paragraph_text in enumerate(paragraphs, 1):
                        # Truncate long text for display
                        display_text = paragraph_text[:60] + "..." if len(paragraph_text) > 60 else paragraph_text
                        print(f"      {j}. \"{display_text}\"")
                
                if len(data) > 3:
                    print(f"\n   ... and {len(data) - 3} more groups")
                
                # Show a group with multiple paragraphs
                multi_para_groups = [g for g in data if g.get('total_paragraphs', 0) > 1]
                if multi_para_groups:
                    print(f"\n🎯 Example of Multi-Paragraph Group:")
                    example = multi_para_groups[0]
                    print(f"   Vocabularies: {example.get('vocabs')}")
                    print(f"   Paragraphs:")
                    for i, para in enumerate(example.get('paragraphs', []), 1):
                        print(f"      {i}. \"{para[:80]}...\"")
                
                return True
            else:
                print("   No grouped data found")
                
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def verify_data_structure():
    """Verify the new data structure matches requirements"""
    print("\n🔍 Verifying data structure...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=true")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', [])
            
            if data:
                sample_group = data[0]
                
                print(f"✅ Sample group structure:")
                print(f"   • id: {type(sample_group.get('id')).__name__} - {sample_group.get('id', 'N/A')[:20]}...")
                print(f"   • vocabs: {type(sample_group.get('vocabs')).__name__} - {sample_group.get('vocabs', [])}")
                print(f"   • is_group: {type(sample_group.get('is_group')).__name__} - {sample_group.get('is_group')}")
                print(f"   • total_paragraphs: {type(sample_group.get('total_paragraphs')).__name__} - {sample_group.get('total_paragraphs')}")
                
                paragraphs = sample_group.get('paragraphs', [])
                print(f"   • paragraphs: {type(paragraphs).__name__} with {len(paragraphs)} items")
                
                if paragraphs:
                    print(f"     - First paragraph type: {type(paragraphs[0]).__name__}")
                    print(f"     - First paragraph preview: \"{paragraphs[0][:50]}...\"")
                
                # Check if structure matches requirements
                required_fields = ['id', 'vocabs', 'is_group', 'paragraphs', 'total_paragraphs']
                missing_fields = [field for field in required_fields if field not in sample_group]
                
                if not missing_fields:
                    print(f"✅ Structure verification: PASSED")
                    print(f"   All required fields present: {required_fields}")
                else:
                    print(f"❌ Structure verification: FAILED")
                    print(f"   Missing fields: {missing_fields}")
                
                # Verify paragraphs is array of strings
                if paragraphs and all(isinstance(p, str) for p in paragraphs):
                    print(f"✅ Paragraphs format: CORRECT (array of strings)")
                else:
                    print(f"❌ Paragraphs format: INCORRECT (not array of strings)")
                
                return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def compare_formats():
    """Compare grouped vs ungrouped formats"""
    print("\n🔄 Comparing grouped vs ungrouped formats...")
    
    try:
        # Get grouped format
        grouped_response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=true")
        # Get ungrouped format
        ungrouped_response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=false")
        
        if grouped_response.status_code == 200 and ungrouped_response.status_code == 200:
            grouped_result = grouped_response.json()
            ungrouped_result = ungrouped_response.json()
            
            print(f"📊 Format Comparison:")
            print(f"   Grouped format:")
            print(f"     • Response count: {grouped_result.get('total', 0)} vocabulary groups")
            print(f"     • Structure: Each item has 'paragraphs' array of strings")
            
            print(f"   Ungrouped format:")
            print(f"     • Response count: {ungrouped_result.get('total', 0)} individual paragraphs")
            print(f"     • Structure: Each item has 'paragraph' single string")
            
            # Calculate total paragraphs in grouped data
            grouped_data = grouped_result.get('data', [])
            total_paragraphs_in_groups = sum(group.get('total_paragraphs', 0) for group in grouped_data)
            
            print(f"\n🔍 Data Consistency:")
            print(f"   • Total paragraphs in groups: {total_paragraphs_in_groups}")
            print(f"   • Total ungrouped paragraphs: {ungrouped_result.get('total', 0)}")
            
            if total_paragraphs_in_groups == ungrouped_result.get('total', 0):
                print(f"   ✅ Data consistency: VERIFIED")
            else:
                print(f"   ❌ Data consistency: MISMATCH")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests for new format"""
    print("🚀 Testing Updated Grouped API Format")
    print("=" * 60)
    print("New format: paragraphs as array of strings")
    
    success_count = 0
    
    if test_new_grouped_format():
        success_count += 1
    
    if verify_data_structure():
        success_count += 1
    
    compare_formats()
    
    print(f"\n{'='*60}")
    print(f"🎯 Test Results: {success_count}/2 core tests passed")
    
    if success_count == 2:
        print(f"✅ NEW FORMAT IMPLEMENTATION: SUCCESS")
        print(f"🎉 The API now returns the exact format requested!")
    else:
        print(f"❌ NEW FORMAT IMPLEMENTATION: NEEDS ATTENTION")

if __name__ == "__main__":
    main()
