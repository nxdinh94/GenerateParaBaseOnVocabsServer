"""
Demo script showcasing the grouped paragraphs functionality
"""
import requests
import json

def print_header(title):
    print(f"\n{'=' * 60}")
    print(f"🔸 {title}")
    print(f"{'=' * 60}")

def demo_grouped_overview():
    """Demonstrate the grouped overview"""
    print_header("GROUPED OVERVIEW")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=true")
        result = response.json()
        
        if response.status_code == 200:
            groups = result.get('data', [])
            total_groups = result.get('total', 0)
            
            print(f"📊 Total Vocabulary Groups: {total_groups}")
            
            # Show statistics
            groups_with_multiple = [g for g in groups if g.get('total_paragraphs', 0) > 1]
            single_paragraph_groups = [g for g in groups if g.get('total_paragraphs', 0) == 1]
            
            print(f"   • Groups with multiple paragraphs: {len(groups_with_multiple)}")
            print(f"   • Groups with single paragraph: {len(single_paragraph_groups)}")
            
            # Show top groups by paragraph count
            sorted_groups = sorted(groups, key=lambda x: x.get('total_paragraphs', 0), reverse=True)
            
            print(f"\n🏆 Top 5 Groups by Paragraph Count:")
            for i, group in enumerate(sorted_groups[:5], 1):
                vocabs = ', '.join(group.get('vocabs', []))
                count = group.get('total_paragraphs', 0)
                print(f"   {i}. [{vocabs}] - {count} paragraph(s)")
            
            return groups_with_multiple
        else:
            print(f"❌ Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def demo_group_drill_down(groups_with_multiple):
    """Demonstrate drilling down into group details"""
    print_header("GROUP DRILL-DOWN")
    
    if not groups_with_multiple:
        print("ℹ️  No groups with multiple paragraphs to demonstrate")
        return
    
    # Select the group with most paragraphs
    target_group = max(groups_with_multiple, key=lambda x: x.get('total_paragraphs', 0))
    
    group_id = target_group['id']
    vocabs = target_group['vocabs']
    total_paragraphs = target_group['total_paragraphs']
    
    print(f"🎯 Selected Group:")
    print(f"   ID: {group_id}")
    print(f"   Vocabularies: {vocabs}")
    print(f"   Total Paragraphs: {total_paragraphs}")
    
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/v1/paragraphs-by-group/{group_id}")
        result = response.json()
        
        if response.status_code == 200:
            paragraphs = result.get('paragraphs', [])
            
            print(f"\n📄 Detailed Paragraphs:")
            for i, para in enumerate(paragraphs, 1):
                para_id = para.get('id', '')
                text = para.get('paragraph', '')
                created = para.get('created_at', 'N/A')
                
                # Truncate long text for display
                display_text = text[:80] + "..." if len(text) > 80 else text
                
                print(f"\n   {i}. Paragraph ID: {para_id}")
                print(f"      Created: {created}")
                print(f"      Text: {display_text}")
            
            # Show how this demonstrates vocabulary reuse
            print(f"\n💡 Insight:")
            print(f"   These {len(paragraphs)} paragraphs all use the same vocabulary set:")
            print(f"   {vocabs}")
            print(f"   This shows efficient vocabulary reuse in the learning process!")
            
        else:
            print(f"❌ Error getting group details: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_comparison():
    """Compare grouped vs ungrouped responses"""
    print_header("GROUPED VS UNGROUPED COMPARISON")
    
    try:
        # Get both formats
        grouped_response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=true")
        ungrouped_response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=false")
        
        if grouped_response.status_code == 200 and ungrouped_response.status_code == 200:
            grouped_result = grouped_response.json()
            ungrouped_result = ungrouped_response.json()
            
            grouped_count = grouped_result.get('total', 0)
            ungrouped_count = ungrouped_result.get('total', 0)
            
            # Calculate response sizes (approximate)
            grouped_size = len(json.dumps(grouped_result))
            ungrouped_size = len(json.dumps(ungrouped_result))
            
            compression_ratio = ((ungrouped_size - grouped_size) / ungrouped_size * 100) if ungrouped_size > 0 else 0
            
            print(f"📊 Response Comparison:")
            print(f"   Grouped format:")
            print(f"     • Items returned: {grouped_count} vocabulary groups")
            print(f"     • Response size: ~{grouped_size:,} bytes")
            print(f"   Ungrouped format:")
            print(f"     • Items returned: {ungrouped_count} individual paragraphs")
            print(f"     • Response size: ~{ungrouped_size:,} bytes")
            print(f"   📉 Size reduction: {compression_ratio:.1f}%")
            
            # Calculate total paragraphs in groups
            grouped_data = grouped_result.get('data', [])
            total_paragraphs_in_groups = sum(group.get('total_paragraphs', 0) for group in grouped_data)
            
            print(f"\n🔍 Data Verification:")
            print(f"   • Paragraphs in groups: {total_paragraphs_in_groups}")
            print(f"   • Individual paragraphs: {ungrouped_count}")
            print(f"   • Data consistency: {'✅ VERIFIED' if total_paragraphs_in_groups == ungrouped_count else '❌ MISMATCH'}")
            
        else:
            print(f"❌ Error getting comparison data")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_use_cases():
    """Show practical use cases for grouped API"""
    print_header("PRACTICAL USE CASES")
    
    print("🎯 When to use GROUPED format:")
    print("   ✅ Dashboard overview showing vocabulary progress")
    print("   ✅ Identifying which vocabulary sets need more practice")
    print("   ✅ Analytics on vocabulary reuse patterns")
    print("   ✅ Reducing bandwidth for mobile apps")
    print("   ✅ Better UX with large datasets")
    
    print("\n🎯 When to use UNGROUPED format:")
    print("   ✅ Displaying chronological timeline of all writings")
    print("   ✅ Full-text search across all paragraphs")
    print("   ✅ Individual paragraph editing/management")
    print("   ✅ Export functionality for backup")
    
    print("\n🎯 Workflow Example:")
    print("   1. Use GROUPED for main dashboard (fast overview)")
    print("   2. User clicks on interesting vocabulary group")
    print("   3. Use /paragraphs-by-group/{id} for detailed view")
    print("   4. User can read/edit individual paragraphs")

def main():
    """Run the complete demo"""
    print("🚀 GROUPED PARAGRAPHS FUNCTIONALITY DEMO")
    print("Showcasing the new grouped API features...")
    
    # Step 1: Show grouped overview
    groups_with_multiple = demo_grouped_overview()
    
    # Step 2: Drill down into a specific group
    demo_group_drill_down(groups_with_multiple)
    
    # Step 3: Compare formats
    demo_comparison()
    
    # Step 4: Show use cases
    demo_use_cases()
    
    print_header("DEMO COMPLETED")
    print("✅ Key Benefits Demonstrated:")
    print("   • 📊 Better data organization by vocabulary groups")
    print("   • 🔍 Easy identification of vocabulary reuse patterns")
    print("   • 📱 Reduced response size for better performance")
    print("   • 🎯 Flexible API supporting both grouped and ungrouped views")
    print("   • 🔗 Seamless navigation from overview to details")
    
    print("\n🎉 The grouped paragraphs API is ready for production!")

if __name__ == "__main__":
    main()
