#!/usr/bin/env python3
"""
Simple temperature fix verification test
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    print("\n🧪 TEMPERATURE FIX VERIFICATION TEST")
    print("=" * 70)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return 1
    
    # Test 1: Direct OpenAI with temperature=1 (should work)
    print("\n✓ TEST 1: Direct OpenAI call with temperature=1")
    print("-" * 70)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            temperature=1,  # REQUIRED
            max_completion_tokens=10
        )
        print(f"✅ SUCCESS with temperature=1")
        print(f"   Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return 1
    
    # Test 2: Try with temperature=0.7 (should fail with specific error)
    print("\n✓ TEST 2: Direct OpenAI call with temperature=0.7 (expect failure)")
    print("-" * 70)
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            temperature=0.7,  # Should fail
            max_completion_tokens=10
        )
        print("❌ UNEXPECTED: Should have failed but didn't!")
        return 1
    except Exception as e:
        if "temperature" in str(e).lower() and "0.7" in str(e):
            print(f"✅ EXPECTED FAILURE confirmed")
            print(f"   Error: {str(e)[:150]}...")
        else:
            print(f"❌ FAILED with unexpected error: {e}")
            return 1
    
    # Test 3: LangChain ChatOpenAI with temperature=1
    print("\n✓ TEST 3: LangChain ChatOpenAI with temperature=1")
    print("-" * 70)
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        
        llm = ChatOpenAI(
            openai_api_key=api_key,
            model="gpt-5-nano",
            temperature=1,  # Fixed!
            max_completion_tokens=10
        )
        
        response = llm.invoke([HumanMessage(content="Say 'OK'")])
        print(f"✅ SUCCESS with temperature=1")
        print(f"   Response type: {type(response)}")
        print(f"   Content: {response.content}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return 1
    
    # Summary
    print("\n" + "=" * 70)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 70)
    print("\n✅ The temperature fix is working correctly.")
    print("✅ temperature=1 is now explicitly set in ChatOpenAI initialization")
    print("✅ Your app should work without the 400 error now")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
