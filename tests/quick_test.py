#!/usr/bin/env python3
"""
Quick Test Script for Wynn Concierge App
Tests both quick greetings and full itinerary generation
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
from src.vector_store import ResortKnowledgeBase
from src.agent_logic import WynnConciergeAgent

def main():
    print('\n🧪 Testing Wynn Concierge App...\n')
    
    # Load environment
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL', 'gpt-5-nano')
    
    if not api_key or api_key == 'your-actual-api-key-here':
        print('❌ API key not set properly')
        return 1
    
    print(f'✅ API key loaded (length: {len(api_key)})')
    print(f'✅ Model: {model}')
    
    # Initialize components
    print('\n📦 Initializing knowledge base...')
    kb = ResortKnowledgeBase(api_key)
    print(f'✅ Loaded {len(kb.venues)} venues')
    
    print('\n🤖 Initializing agent...')
    agent = WynnConciergeAgent(kb, api_key, model=model)
    
    # Test guest
    guest = {
        'name': 'Sarah Chen',
        'loyalty_tier': 'Black',
        'dietary_restrictions': 'Vegetarian, Gluten-Free',
        'preferences': 'Romantic settings',
        'age': 32
    }
    
    # Test 1: Simple greeting
    print('\n' + '='*60)
    print('TEST 1: Simple Greeting (should be instant)')
    print('='*60)
    
    start = time.time()
    response = agent.create_itinerary('hi', guest)
    elapsed = time.time() - start
    
    print(f'\n⏱️  Response time: {elapsed:.2f}s')
    print(f'\n📝 Response:\n{response[:300]}...\n')
    
    if elapsed < 2:
        print('✅ PASS: Quick greeting response!')
    else:
        print('⚠️  WARNING: Greeting took too long')
    
    # Test 2: Actual request
    print('\n' + '='*60)
    print('TEST 2: Real Itinerary Request')
    print('='*60)
    
    start = time.time()
    try:
        response = agent.create_itinerary('I want romantic dinner with wine', guest)
        elapsed = time.time() - start
        
        print(f'\n⏱️  Response time: {elapsed:.2f}s')
        print(f'\n📝 Response:\n{response[:500]}...\n')
        
        if 'technical difficulty' in response or 'error' in response.lower():
            print('❌ FAIL: Error in response')
            return 1
        else:
            print('✅ PASS: Got proper itinerary!')
            
    except Exception as e:
        print(f'\n❌ ERROR: {e}')
        import traceback
        traceback.print_exc()
        return 1
    
    print('\n' + '='*60)
    print('🎉 ALL TESTS PASSED!')
    print('='*60)
    return 0

if __name__ == '__main__':
    sys.exit(main())
