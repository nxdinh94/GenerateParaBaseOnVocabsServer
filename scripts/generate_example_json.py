"""
Generate example JSON for the new grouped API format
"""
import requests
import json

def generate_example_json():
    """Generate clean example JSON for documentation"""
    print("📝 Generating example JSON for new format...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/saved-paragraphs?grouped=true")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', [])
            
            # Find a good example group (one with multiple paragraphs)
            example_groups = []
            
            for group in data:
                if group.get('total_paragraphs', 0) > 1:
                    example_groups.append(group)
            
            # Create a clean example with 2 groups
            if len(example_groups) >= 2:
                clean_example = {
                    "status": True,
                    "total": 2,
                    "data": [
                        {
                            "id": example_groups[0].get('id'),
                            "vocabs": example_groups[0].get('vocabs'),
                            "is_group": True,
                            "paragraphs": example_groups[0].get('paragraphs')[:2],  # Limit to 2 for example
                            "total_paragraphs": len(example_groups[0].get('paragraphs', []))
                        },
                        {
                            "id": example_groups[1].get('id') if len(example_groups) > 1 else data[0].get('id'),
                            "vocabs": example_groups[1].get('vocabs') if len(example_groups) > 1 else data[0].get('vocabs'),
                            "is_group": True,
                            "paragraphs": example_groups[1].get('paragraphs')[:2] if len(example_groups) > 1 else data[0].get('paragraphs', [])[:1],
                            "total_paragraphs": len(example_groups[1].get('paragraphs', [])) if len(example_groups) > 1 else len(data[0].get('paragraphs', []))
                        }
                    ]
                }
            else:
                # Fallback to first two groups
                clean_example = {
                    "status": True,
                    "total": min(2, len(data)),
                    "data": data[:2]
                }
            
            # Pretty print the JSON
            print("✅ Example JSON Response:")
            print(json.dumps(clean_example, indent=4, ensure_ascii=False))
            
            # Save to file for documentation
            with open('scripts/example_grouped_response.json', 'w', encoding='utf-8') as f:
                json.dump(clean_example, f, indent=4, ensure_ascii=False)
            
            print(f"\n💾 Example saved to: scripts/example_grouped_response.json")
            
            return clean_example
            
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def show_structure_summary():
    """Show a summary of the new structure"""
    print("\n📋 NEW STRUCTURE SUMMARY:")
    print("=" * 50)
    
    structure = {
        "response": {
            "status": "boolean - API success status",
            "total": "number - Total number of vocabulary groups", 
            "data": "array - Array of vocabulary groups"
        },
        "each_group_item": {
            "id": "string - Input history ID (group identifier)",
            "vocabs": "array - Array of vocabulary strings",
            "is_group": "boolean - Always true for grouped format",
            "paragraphs": "array - Array of paragraph text strings",
            "total_paragraphs": "number - Count of paragraphs in this group"
        }
    }
    
    print("🏗️  Response Structure:")
    print(json.dumps(structure, indent=2))
    
    print("\n🔧 Key Changes from Old Format:")
    print("✅ paragraphs: Now array of strings (not objects)")
    print("✅ Removed: paragraph field (replaced by paragraphs array)")
    print("✅ Removed: created_at field (not needed in grouped view)")
    print("✅ Simplified: Direct access to paragraph text")
    
    print("\n💡 Usage Examples:")
    print("   • group.paragraphs[0] - Get first paragraph text")
    print("   • group.paragraphs.length - Get paragraph count")
    print("   • group.vocabs.join(', ') - Display vocabulary list")

def main():
    """Generate example and documentation"""
    print("🚀 Generating Documentation for New Format")
    print("=" * 60)
    
    example = generate_example_json()
    
    if example:
        show_structure_summary()
        
        print(f"\n{'='*60}")
        print("✅ Documentation generation completed!")
        print("📁 Files created:")
        print("   • scripts/example_grouped_response.json")
    else:
        print("❌ Failed to generate documentation")

if __name__ == "__main__":
    main()
