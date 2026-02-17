"""
Full Integration Test & Verification Script
Tests the complete luxury concierge system end-to-end
"""

import os
import sys
import logging
from typing import Dict, Tuple
from dotenv import load_dotenv

# Add src to path - handle both test file and src file access
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
test_dir = current_dir

sys.path.insert(0, src_dir)
sys.path.insert(0, test_dir)
sys.path.insert(0, os.path.dirname(current_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_integration_tests() -> Dict[str, bool]:
    """Run full integration test suite"""
    
    print("\n" + "="*80)
    print("🎯 LUXURY CONCIERGE SYSTEM - FULL INTEGRATION TEST")
    print("="*80)
    
    results = {
        'environment': False,
        'imports': False,
        'agent_init': False,
        'simple_response': False,
        'luxury_response': False,
        'tracing': False,
        'evaluation': False,
        'all_passed': False
    }
    
    try:
        # ================================================================
        # TEST 1: Environment Setup
        # ================================================================
        print("\n[1/7] Testing Environment Setup...")
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("❌ FAILED: OPENAI_API_KEY not found in .env")
            return results
        
        print("✅ PASSED: Environment configured")
        results['environment'] = True
        
        # ================================================================
        # TEST 2: Module Imports
        # ================================================================
        print("\n[2/7] Testing Module Imports...")
        try:
            from vector_store import ResortKnowledgeBase
            from agent_logic import WynnConciergeAgent
            from luxury_concierge_v2 import (
                LuxuryConciergeAgentV2,
                LuxuryServiceStandards,
                ConversationTracer,
                ConciergeEvaluationFramework
            )
            from evaluation_suite import ConciergeTestRunner
            
            print("✅ PASSED: All modules imported successfully")
            results['imports'] = True
        except ImportError as e:
            print(f"❌ FAILED: Import error - {e}")
            return results
        
        # ================================================================
        # TEST 3: Agent Initialization (V1)
        # ================================================================
        print("\n[3/7] Testing V1 Agent Initialization...")
        try:
            kb = ResortKnowledgeBase(api_key)
            agent_v1 = WynnConciergeAgent(kb, api_key, model="gpt-5-nano")
            
            print("✅ PASSED: V1 Agent initialized")
            results['agent_init'] = True
        except Exception as e:
            print(f"❌ FAILED: V1 Agent initialization - {e}")
            return results
        
        # ================================================================
        # TEST 4: Simple Response (V1)
        # ================================================================
        print("\n[4/7] Testing Simple Response (V1)...")
        try:
            guest_profile = {
                'name': 'Test Guest',
                'loyalty_tier': 'Platinum',
                'dietary_restrictions': 'None',
                'preferences': 'Fine dining'
            }
            
            response = agent_v1.create_itinerary(
                "best non veg dish?",
                guest_profile
            )
            
            if len(response) > 20 and 'Obsidian' in response or 'steak' in response.lower():
                print(f"✅ PASSED: Simple response generated")
                print(f"   Response preview: {response[:80]}...")
                results['simple_response'] = True
            else:
                print(f"❌ FAILED: Response too short or irrelevant")
                print(f"   Response: {response}")
        except Exception as e:
            print(f"❌ FAILED: Simple response - {e}")
        
        # ================================================================
        # TEST 5: Luxury V2 Agent Response
        # ================================================================
        print("\n[5/7] Testing Luxury V2 Agent...")
        try:
            agent_v2 = LuxuryConciergeAgentV2(kb, api_key, enable_tracing=True)
            
            agent_v2.initiate_guest_session(guest_profile)
            
            response, metrics = agent_v2.create_luxury_response(
                "I want the best steak and wine pairing",
                guest_profile
            )
            
            confidence = metrics.get('confidence_score', 0)
            
            if confidence >= 0.5 and len(response) > 30:
                print(f"✅ PASSED: V2 Luxury response generated")
                print(f"   Confidence Score: {confidence:.2f}/1.0")
                print(f"   Response: {response[:100]}...")
                results['luxury_response'] = True
            else:
                print(f"⚠️  WARNING: Low confidence or short response")
                print(f"   Confidence: {confidence}, Length: {len(response)}")
            
            session_summary = agent_v2.end_guest_session()
        except Exception as e:
            print(f"❌ FAILED: V2 Luxury response - {e}")
            import traceback
            traceback.print_exc()
        
        # ================================================================
        # TEST 6: Tracing Verification
        # ================================================================
        print("\n[6/7] Testing Tracing & Observability...")
        try:
            agent_v2_trace = LuxuryConciergeAgentV2(kb, api_key, enable_tracing=True)
            agent_v2_trace.initiate_guest_session({
                'name': 'Sarah Chen',
                'loyalty_tier': 'Black',
                'dietary_restrictions': 'Vegetarian',
                'preferences': 'Romantic'
            })
            
            resp1, m1 = agent_v2_trace.create_luxury_response(
                "romantic dinner?", guest_profile
            )
            resp2, m2 = agent_v2_trace.create_luxury_response(
                "with wine pairing?", guest_profile
            )
            
            summary = agent_v2_trace.end_guest_session()
            
            if summary and summary.get('turns') >= 2:
                print(f"✅ PASSED: Tracing active and recording")
                print(f"   Conversation turns: {summary['turns']}")
                print(f"   Avg confidence: {summary['avg_confidence']:.2f}")
                results['tracing'] = True
            else:
                print(f"⚠️  WARNING: Tracing may not be complete")
        except Exception as e:
            print(f"⚠️  WARNING: Tracing test - {e}")
        
        # ================================================================
        # TEST 7: Evaluation Framework
        # ================================================================
        print("\n[7/7] Testing Evaluation Framework...")
        try:
            test_response = "I recommend The Obsidian Steakhouse. Their 45-day dry-aged Tomahawk ribeye is exceptional. As a Black Tier guest, the chef's table and wine pairing are complimentary."
            
            scores = ConciergeEvaluationFramework.evaluate_response(
                test_response,
                'Black',
                {'guest_name': 'Test Guest', 'mention_vip_perks': True}
            )
            
            luxury_score = ConciergeEvaluationFramework.calculate_luxury_score(scores)
            
            if luxury_score >= 6.0:
                print(f"✅ PASSED: Evaluation framework working")
                print(f"   Luxury Score: {luxury_score}/10")
                print(f"   Metrics: {scores}")
                results['evaluation'] = True
            else:
                print(f"⚠️  WARNING: Low luxury score: {luxury_score}/10")
        except Exception as e:
            print(f"❌ FAILED: Evaluation framework - {e}")
        
        # ================================================================
        # Final Summary
        # ================================================================
        print("\n" + "="*80)
        print("📊 INTEGRATION TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for v in results.values() if v is True)
        total = len(results) - 1  # Exclude 'all_passed'
        
        print(f"\nTests Passed: {passed}/{total}")
        
        for test_name, test_result in results.items():
            if test_name != 'all_passed':
                status = "✅" if test_result else "❌"
                print(f"  {status} {test_name.replace('_', ' ').title()}")
        
        results['all_passed'] = passed == total
        
        if results['all_passed']:
            print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        else:
            print(f"\n⚠️  {total - passed} test(s) need attention")
        
        return results
    
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return results


# Test Case Scenarios
TEST_SCENARIOS = [
    {
        'name': 'VIP Black Tier Guest - Steak Preference',
        'guest': {
            'name': 'Alexandra Knight',
            'loyalty_tier': 'Black',
            'dietary_restrictions': 'None',
            'preferences': 'Luxury, exclusive',
            'age': 45
        },
        'query': 'best non veg dish?'
    },
    {
        'name': 'Health-Conscious Premium Guest',
        'guest': {
            'name': 'Dr. Michael Santos',
            'loyalty_tier': 'Platinum',
            'dietary_restrictions': 'Gluten-Free, Heart-Healthy',
            'preferences': 'Mediterranean, seafood',
            'age': 52
        },
        'query': 'healthy dinner options with excellent wine?'
    },
    {
        'name': 'Vegetarian Romantic Evening',
        'guest': {
            'name': 'Emma Thompson',
            'loyalty_tier': 'Gold',
            'dietary_restrictions': 'Vegetarian',
            'preferences': 'Romantic, intimate',
            'age': 29
        },
        'query': 'romantic vegetarian dinner for two?'
    }
]


def run_scenario_tests(agent_v2, kb):
    """Run test scenarios to verify agent handles various guest types"""
    print("\n" + "="*80)
    print("🎯 GUEST SCENARIO TESTING")
    print("="*80)
    
    for scenario in TEST_SCENARIOS:
        print(f"\n📋 Scenario: {scenario['name']}")
        print("-" * 60)
        
        guest = scenario['guest']
        print(f"Guest: {guest['name']} ({guest['loyalty_tier']} Tier)")
        print(f"Request: \"{scenario['query']}\"")
        
        try:
            agent_v2.initiate_guest_session(guest)
            
            response, metrics = agent_v2.create_luxury_response(
                scenario['query'],
                guest
            )
            
            print(f"✅ Response generated")
            print(f"   Confidence: {metrics['confidence_score']:.2f}/1.0")
            print(f"   Response: {response[:150]}...")
            
            summary = agent_v2.end_guest_session()
            print(f"   Session time: {summary.get('total_duration_sec', 0):.2f}s")
        
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Run full integration tests
    results = run_integration_tests()
    
    if results.get('all_passed'):
        print("\n" + "="*80)
        print("✅ FULL SYSTEM READY FOR PRODUCTION")
        print("="*80)
        print("\nNext steps:")
        print("1. Deploy to production")
        print("2. Monitor concierge quality metrics")
        print("3. Collect guest feedback data")
        print("4. Run continuous evaluation")
    else:
        print("\n❌ Some tests failed - review logs above")
        sys.exit(1)
