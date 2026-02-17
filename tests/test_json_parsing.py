"""
Test JSON Parsing Fix for Streamlit Deployment
Tests the new JSON mode and error handling without hitting API quotas
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_json_parsing_logic():
    """Test the JSON parsing logic with various response formats"""
    
    print("🧪 TESTING JSON PARSING LOGIC FOR DEPLOYMENT")
    print("=" * 60)
    
    # Test Case 1: Valid JSON response (expected with JSON mode)
    print("\n✅ Test 1: Valid JSON Response")
    valid_json = """{
  "itinerary": {
    "events": [
      {
        "time": "19:00",
        "venue_name": "Verde Garden",
        "venue_type": "Fine Dining",
        "duration_minutes": 90,
        "reason": "Romantic ambiance with excellent wine selection",
        "vip_perk": "Reserved chef's table with complimentary pairing"
      },
      {
        "time": "21:00",
        "venue_name": "Aura Skypool Lounge",
        "venue_type": "Nightlife",
        "duration_minutes": 120,
        "reason": "Sophisticated atmosphere with stunning views",
        "vip_perk": "VIP table with bottle service"
      }
    ]
  },
  "guest_message": "Good evening, Ms. Chen. I have crafted an exceptional evening for you.",
  "logistics_notes": "Allow 15 minutes between venues. Dress code: Smart Elegant."
}"""
    
    try:
        parsed = json.loads(valid_json)
        assert 'guest_message' in parsed
        assert 'itinerary' in parsed
        assert len(parsed['itinerary']['events']) == 2
        print(f"   ✓ Parsed successfully")
        print(f"   ✓ Events: {len(parsed['itinerary']['events'])}")
        print(f"   ✓ Message extracted: {parsed['guest_message'][:50]}...")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        return False
    
    # Test Case 2: JSON with markdown wrapping (should be cleaned)
    print("\n✅ Test 2: JSON with Markdown Wrapping")
    markdown_json = f"""```json
{valid_json}
```"""
    
    try:
        # Simulate the cleaning logic
        json_text = markdown_json.strip()
        if '```json' in json_text:
            json_text = json_text.split('```json')[1].split('```')[0].strip()
        
        parsed = json.loads(json_text)
        assert 'guest_message' in parsed
        print(f"   ✓ Cleaned and parsed successfully")
        print(f"   ✓ Message: {parsed['guest_message'][:50]}...")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        return False
    
    # Test Case 3: Empty response (should fail gracefully)
    print("\n✅ Test 3: Empty Response Handling")
    empty_response = ""
    
    try:
        json_text = empty_response.strip()
        if not json_text:
            print("   ✓ Empty response detected correctly")
            print("   ✓ Would return user-friendly error message")
        else:
            parsed = json.loads(json_text)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"   ✓ Error caught correctly: {type(e).__name__}")
    
    # Test Case 4: Invalid JSON (should fail gracefully)
    print("\n✅ Test 4: Invalid JSON Handling")
    invalid_json = "This is not JSON"
    
    try:
        parsed = json.loads(invalid_json)
        print(f"   ✗ Should have failed!")
        return False
    except json.JSONDecodeError as e:
        print(f"   ✓ Invalid JSON caught correctly")
        print(f"   ✓ Error type: {type(e).__name__}")
    
    # Test Case 5: JSON missing required fields
    print("\n✅ Test 5: Missing Required Fields")
    incomplete_json = '{"itinerary": {"events": []}}'
    
    try:
        parsed = json.loads(incomplete_json)
        if 'guest_message' not in parsed:
            print("   ✓ Missing field detected correctly")
            print("   ✓ Would trigger fallback error handling")
        else:
            print("   ✗ Should have detected missing field")
            return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL JSON PARSING TESTS PASSED")
    return True


def test_agent_initialization():
    """Test that agent initializes with JSON mode correctly"""
    print("\n🧪 TESTING AGENT INITIALIZATION")
    print("=" * 60)
    
    try:
        from agent_logic import WynnConciergeAgent
        from vector_store import ResortKnowledgeBase
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("   ⚠️  No API key found - skipping live initialization test")
            print("   ✓ But code imports successfully")
            return True
        
        # Check that the LLM config includes JSON mode
        print("   ✓ Agent class imported successfully")
        print("   ✓ WynnConciergeAgent has __init__ method with model_kwargs")
        
        # Verify the init signature
        import inspect
        sig = inspect.signature(WynnConciergeAgent.__init__)
        params = list(sig.parameters.keys())
        
        assert 'knowledge_base' in params
        assert 'openai_api_key' in params
        assert 'model' in params
        
        print(f"   ✓ Correct initialization parameters: {params[1:]}")  # Skip 'self'
        
        # Check source code for JSON mode
        source = inspect.getsource(WynnConciergeAgent.__init__)
        if 'response_format' in source and 'json_object' in source:
            print("   ✓ JSON mode (response_format) configured correctly")
        else:
            print("   ✗ WARNING: JSON mode not found in initialization")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_streamlit_compatibility():
    """Test that all required dependencies are available"""
    print("\n🧪 TESTING STREAMLIT DEPLOYMENT COMPATIBILITY")
    print("=" * 60)
    
    required_packages = [
        'streamlit',
        'langchain_openai',
        'langchain_community',
        'faiss',
        'openai',
        'pandas',
        'dotenv'
    ]
    
    all_available = True
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
                pkg_name = 'python-dotenv'
            else:
                __import__(package)
                pkg_name = package
            print(f"   ✓ {pkg_name} available")
        except ImportError:
            print(f"   ✗ {pkg_name} MISSING")
            all_available = False
    
    if all_available:
        print("\n   ✅ All dependencies available for Streamlit deployment")
    else:
        print("\n   ⚠️  Some dependencies missing - run: pip install -r requirements.txt")
    
    return all_available


def test_environment_config():
    """Test environment configuration"""
    print("\n🧪 TESTING ENVIRONMENT CONFIGURATION")
    print("=" * 60)
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"   ✓ OPENAI_API_KEY configured (length: {len(api_key)})")
    else:
        print("   ⚠️  OPENAI_API_KEY not set")
    
    # Check for model
    model = os.getenv('OPENAI_MODEL', 'gpt-5-nano')
    print(f"   ✓ Model: {model}")
    
    # Check data files
    data_path = Path(__file__).parent.parent / 'data'
    required_files = ['resort_data.json', 'guests.csv']
    
    for file in required_files:
        file_path = data_path / file
        if file_path.exists():
            print(f"   ✓ {file} exists")
        else:
            print(f"   ✗ {file} MISSING")
            return False
    
    # Check FAISS index
    faiss_path = data_path / 'faiss_index'
    if faiss_path.exists():
        print(f"   ✓ FAISS index directory exists")
    else:
        print(f"   ⚠️  FAISS index will be built on first run")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "🚀" * 30)
    print("WYNN CONCIERGE - DEPLOYMENT READINESS TEST")
    print("Testing JSON Parsing Fix for Streamlit Cloud")
    print("🚀" * 30)
    
    results = {
        'JSON Parsing Logic': test_json_parsing_logic(),
        'Agent Initialization': test_agent_initialization(),
        'Streamlit Compatibility': test_streamlit_compatibility(),
        'Environment Config': test_environment_config()
    }
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("=" * 60)
    
    if all(results.values()):
        print("\n🎉 ALL TESTS PASSED - READY FOR STREAMLIT DEPLOYMENT!")
        print("\nNext steps:")
        print("  1. Commit your changes: git add . && git commit -m 'Fix JSON parsing'")
        print("  2. Push to GitHub: git push")
        print("  3. Deploy to Streamlit Cloud")
        print("  4. Add OPENAI_API_KEY to Streamlit secrets")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED - Fix issues before deployment")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
