#!/usr/bin/env python3
"""
Integration test for Wynn Concierge with GPT-5-nano
Tests both direct OpenAI API calls and LangChain agent
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_direct_openai():
    """Test direct OpenAI API call"""
    print("=" * 70)
    print("TEST 1: Direct OpenAI API Call")
    print("=" * 70)
    
    try:
        import openai
        from openai import OpenAI
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not set in environment")
            return False
        
        client = OpenAI(api_key=api_key)
        
        print("Testing GPT-5-nano with temperature=1 (required)...")
        
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "user", "content": "Say 'Test successful!' if you can read this."}
            ],
            temperature=1,  # REQUIRED for gpt-5-nano
            max_completion_tokens=50
        )
        
        print("✅ Direct OpenAI call successful!")
        print(f"   Model: {response.model}")
        print(f"   Response: {response.choices[0].message.content}")
        print(f"   Tokens used: {response.usage.total_tokens}")
        return True
        
    except Exception as e:
        print(f"❌ Direct OpenAI test failed: {e}")
        return False


def test_langchain_agent():
    """Test LangChain agent integration"""
    print("\n" + "=" * 70)
    print("TEST 2: LangChain Agent Integration")
    print("=" * 70)
    
    try:
        from vector_store import ResortKnowledgeBase
        from agent_logic import WynnConciergeAgent
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not set in environment")
            return False
        
        print("Initializing knowledge base...")
        kb = ResortKnowledgeBase(api_key)
        
        print("Initializing agent with gpt-5-nano...")
        agent = WynnConciergeAgent(kb, api_key, model="gpt-5-nano")
        
        # Test guest profile
        guest = {
            'name': 'Test User',
            'loyalty_tier': 'Platinum',
            'dietary_restrictions': 'None',
            'preferences': 'Casual dining',
            'age': 30
        }
        
        print("Creating test itinerary...")
        query = "I want a nice dinner"
        itinerary = agent.create_itinerary(query, guest)
        
        if itinerary and len(itinerary) > 50 and "I apologize" not in itinerary[:50]:
            print("✅ LangChain agent test successful!")
            print(f"   Generated {len(itinerary)} characters of itinerary")
            print(f"   Preview: {itinerary[:200]}...")
            return True
        else:
            print(f"❌ Agent returned unexpected result: {itinerary[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ LangChain agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n🧪 WYNN CONCIERGE INTEGRATION TESTS")
    print("Testing GPT-5-nano with temperature=1 fix")
    print("=" * 70 + "\n")
    
    results = []
    
    # Test 1: Direct OpenAI
    results.append(("Direct OpenAI API", test_direct_openai()))
    
    # Test 2: LangChain Agent
    results.append(("LangChain Agent", test_langchain_agent()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! The temperature fix is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
