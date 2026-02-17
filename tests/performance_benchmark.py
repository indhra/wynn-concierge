#!/usr/bin/env python3
"""
Performance Benchmarking Script for Wynn Concierge
Tests response latency with the new optimizations
"""

import time
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from vector_store import ResortKnowledgeBase
from luxury_concierge_v2 import LuxuryConciergeAgentV2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

def run_benchmark():
    """Run latency benchmarks"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set. Please configure .env file.")
        return
    
    print("🚀 Wynn Concierge Performance Benchmark")
    print("=" * 60)
    
    # Initialize
    print("\n📦 Initializing knowledge base...")
    kb = ResortKnowledgeBase(api_key)
    
    print("🤖 Initializing concierge agent...")
    agent = LuxuryConciergeAgentV2(kb, api_key, model="gpt-4o-mini", enable_tracing=True)
    
    # Test guest
    guest_profile = {
        'name': 'Test Guest',
        'loyalty_tier': 'Platinum',
        'dietary_restrictions': 'None',
        'preferences': 'Luxury dining, nightlife'
    }
    
    agent.initiate_guest_session(guest_profile)
    
    # Test queries
    test_queries = [
        "What's the best restaurant for tonight?",
        "Can you plan an evening for me?",
        "Best place for romantic dinner?",
        "What's the best restaurant for tonight?",  # Repeat - should hit cache
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}/4: '{query}'")
        print("-" * 60)
        
        start = time.time()
        response, metrics = agent.create_luxury_response(query, guest_profile)
        elapsed_ms = metrics['response_time_ms']
        
        print(f"⏱️  Response time: {elapsed_ms}ms")
        print(f"📊 Confidence: {metrics['confidence_score']:.2f}")
        print(f"✨ Streaming: {'Enabled' if metrics.get('streaming_enabled') else 'Disabled'}")
        print(f"📌 Response preview: {response[:100]}...")
        
        results.append({
            'query': query,
            'elapsed_ms': elapsed_ms,
            'confidence': metrics['confidence_score']
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 BENCHMARK SUMMARY")
    print("=" * 60)
    
    avg_time = sum(r['elapsed_ms'] for r in results) / len(results)
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    
    print(f"\n✅ Average response time: {avg_time:.0f}ms")
    print(f"✅ Average confidence: {avg_confidence:.2f}")
    
    # Check if repeat query was faster (cache)
    first_query_time = results[0]['elapsed_ms']
    repeat_query_time = results[3]['elapsed_ms']  # Same as query 0
    cache_speedup = first_query_time / max(repeat_query_time, 1)
    
    print(f"\n💾 Cache Performance:")
    print(f"   First query: {first_query_time}ms")
    print(f"   Repeat query: {repeat_query_time}ms")
    print(f"   Speedup: {cache_speedup:.1f}x faster")
    
    # Session summary
    session_summary = agent.end_guest_session()
    if session_summary:
        print(f"\n📈 Session Stats:")
        print(f"   Turns: {session_summary['turns']}")
        print(f"   Duration: {session_summary['total_duration_sec']}s")
        print(f"   Avg confidence: {session_summary['avg_confidence']}")
    
    print("\n✨ Benchmark complete!")

if __name__ == "__main__":
    run_benchmark()
