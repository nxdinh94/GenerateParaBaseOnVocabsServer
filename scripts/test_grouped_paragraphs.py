"""
Test the grouped saved-paragraphs API
"""
import requests
import json

def test_grouped_paragraphs():
    """Test getting paragraphs in grouped format"""
    print("🔍 Testing GROUPED saved paragraphs...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=true")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result.get('status')}")
            print(f"✅ Total Groups: {result.get('total')}")
            
            data = result.get('data', [])
            if data:
                print(f"\n📊 GROUPED PARAGRAPHS:")
                for i, group in enumerate(data, 1):
                    print(f"\n{i}. Group ID: {group.get('id')}")
                    print(f"   Vocabularies: {group.get('vocabs')}")
                    print(f"   Total Paragraphs: {group.get('total_paragraphs', 0)}")
                    print(f"   Is Group: {group.get('is_group', False)}")
                    
                    # Show individual paragraphs in the group
                    paragraphs = group.get('paragraphs', [])
                    if paragraphs:
                        print(f"   📄 Paragraphs in this group:")
                        for j, para in enumerate(paragraphs, 1):
                            text = para.get('paragraph', '')[:60] + "..." if len(para.get('paragraph', '')) > 60 else para.get('paragraph', '')
                            print(f"      {j}. ID: {para.get('id')[:12]}... | {text}")
                    
                # Summary statistics
                total_paragraphs = sum(group.get('total_paragraphs', 0) for group in data)
                total_groups = len(data)
                avg_paragraphs_per_group = total_paragraphs / total_groups if total_groups > 0 else 0
                
                print(f"\n📈 SUMMARY:")
                print(f"   • Total vocabulary groups: {total_groups}")
                print(f"   • Total individual paragraphs: {total_paragraphs}")
                print(f"   • Average paragraphs per group: {avg_paragraphs_per_group:.1f}")
                
                return True
            else:
                print("   No grouped data found")
                
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def test_ungrouped_paragraphs():
    """Test getting paragraphs in ungrouped (original) format"""
    print("\n🔍 Testing UNGROUPED saved paragraphs...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=false")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result.get('status')}")
            print(f"✅ Total Individual Paragraphs: {result.get('total')}")
            
            data = result.get('data', [])
            if data:
                print(f"\n📄 INDIVIDUAL PARAGRAPHS (showing first 5):")
                for i, item in enumerate(data[:5], 1):
                    text = item.get('paragraph', '')[:50] + "..." if len(item.get('paragraph', '')) > 50 else item.get('paragraph', '')
                    print(f"{i}. ID: {item.get('id')[:12]}...")
                    print(f"   Vocabs: {item.get('vocabs')}")
                    print(f"   Text: {text}")
                    print()
                
                if len(data) > 5:
                    print(f"   ... and {len(data) - 5} more paragraphs")
                
                return True
            else:
                print("   No ungrouped data found")
                
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def compare_grouped_vs_ungrouped():
    """Compare grouped vs ungrouped results"""
    print("\n🔄 Comparing GROUPED vs UNGROUPED results...")
    
    try:
        # Get grouped data
        response1 = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=true")
        grouped_result = response1.json()
        
        # Get ungrouped data  
        response2 = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=false")
        ungrouped_result = response2.json()
        
        if response1.status_code == 200 and response2.status_code == 200:
            grouped_count = grouped_result.get('total', 0)
            ungrouped_count = ungrouped_result.get('total', 0)
            
            # Calculate total paragraphs in grouped data
            grouped_data = grouped_result.get('data', [])
            total_paragraphs_in_groups = sum(group.get('total_paragraphs', 0) for group in grouped_data)
            
            print(f"📊 COMPARISON RESULTS:")
            print(f"   • Grouped format: {grouped_count} vocabulary groups")
            print(f"   • Ungrouped format: {ungrouped_count} individual paragraphs")
            print(f"   • Total paragraphs in groups: {total_paragraphs_in_groups}")
            
            if total_paragraphs_in_groups == ungrouped_count:
                print(f"   ✅ Data consistency: VERIFIED")
                compression_ratio = (ungrouped_count - grouped_count) / ungrouped_count * 100 if ungrouped_count > 0 else 0
                print(f"   📉 Data compression: {compression_ratio:.1f}% reduction in response size")
            else:
                print(f"   ❌ Data consistency: MISMATCH")
        
    except Exception as e:
        print(f"❌ Error in comparison: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing GROUPED Saved Paragraphs API")
    print("=" * 60)
    
    success_count = 0
    
    if test_grouped_paragraphs():
        success_count += 1
    
    if test_ungrouped_paragraphs():
        success_count += 1
    
    compare_grouped_vs_ungrouped()
    
    print(f"\n{'='*60}")
    print(f"🎯 Test Results: {success_count}/2 tests passed")
    print(f"🎉 Grouped API functionality is {'WORKING' if success_count == 2 else 'NEEDS ATTENTION'}!")

if __name__ == "__main__":
    main()
