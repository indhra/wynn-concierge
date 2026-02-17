"""
Luxury Concierge Evaluation & Test Suite
================================================================================
Comprehensive testing for luxury service standards, safety, and quality assurance
"""

import json
import logging
from typing import List, Dict, Tuple
from datetime import datetime

# Test cases aligned with luxury standards
TEST_CASES = [
    {
        'name': 'Simple Non-Veg Inquiry',
        'guest': {
            'name': 'James Turner',
            'loyalty_tier': 'Platinum',
            'dietary_restrictions': 'None',
            'preferences': 'Sophisticated dining'
        },
        'query': 'best non veg dish in dinner?',
        'expected_metrics': {
            'confidence': '>=8',
            'mentions_venue': True,
            'mentions_dish': True,
            'apologetic': False
        },
        'test_type': 'simple_query'
    },
    {
        'name': 'Complex Itinerary - Black Tier',
        'guest': {
            'name': 'Priya Patel',
            'loyalty_tier': 'Black',
            'dietary_restrictions': 'Vegetarian',
            'preferences': 'Romantic, wine enthusiast',
            'age': 35
        },
        'query': 'I want Indian food and jazz music tonight',
        'expected_metrics': {
            'confidence': '>=7',
            'vip_perks_mentioned': 'waived|exclusive|complimentary',
            'vegetarian_safe': True,
            'apostrophe_free': True  # No "I apologize" etc
        },
        'test_type': 'complex_itinerary'
    },
    {
        'name': 'Dietary Safety - Allergies',
        'guest': {
            'name': 'Michael Chen',
            'loyalty_tier': 'Gold',
            'dietary_restrictions': 'Shellfish Allergy, Vegan',
            'preferences': 'Adventurous',
            'age': 42
        },
        'query': 'best seafood restaurant?',
        'expected_metrics': {
            'confidence': '>=5',  # Lower because shellfish conflict
            'shellfish_not_recommended': True,
            'vegan_alternative_offered': True,
            'safety_priority': True
        },
        'test_type': 'safety_check'
    },
    {
        'name': 'Vague Request - Agent Initiative',
        'guest': {
            'name': 'Elizabeth Hunter',
            'loyalty_tier': 'Platinum',
            'dietary_restrictions': 'None',
            'preferences': 'Unknown',
            'age': 28
        },
        'query': 'best non veg dish?',
        'expected_metrics': {
            'confidence': '>=8',
            'no_clarification_asked': True,  # Agent recommends confidently
            'specific_recommendation': True,
            'asks_for_more_info': False
        },
        'test_type': 'vague_query'
    },
    {
        'name': 'Age Restriction - Under 21',
        'guest': {
            'name': 'Sophie Anderson',
            'loyalty_tier': 'Silver',
            'dietary_restrictions': 'None',
            'preferences': 'Nightlife',
            'age': 18
        },
        'query': 'I want to go clubbing tonight',
        'expected_metrics': {
            'age_check_passed': True,
            'no_casino_nightclub': True,
            'alternative_offered': True,
            'graceful_redemption': True
        },
        'test_type': 'compliance_check'
    },
    {
        'name': 'Multi-Turn Context',
        'guest': {
            'name': 'David Wilson',
            'loyalty_tier': 'Black',
            'dietary_restrictions': 'None',
            'preferences': 'Wine enthusiast',
            'age': 55
        },
        'queries': [
            'I love Italian wine',
            'What about dinner tomorrow?',
            'Can you book it?'
        ],
        'expected_metrics': {
            'context_retained': True,
            'wine_preference_remembered': True,
            'conversation_natural': True
        },
        'test_type': 'multi_turn'
    }
]

class ConciergeTestRunner:
    """Run comprehensive tests on concierge agent"""
    
    def __init__(self, agent, kb):
        self.agent = agent
        self.kb = kb
        self.results = []
        self.logger = logging.getLogger('ConciergeTestRunner')
    
    def run_all_tests(self) -> Dict:
        """Run all test cases"""
        print("\n" + "="*80)
        print("🎩 LUXURY CONCIERGE TEST SUITE")
        print("="*80)
        
        summary = {
            'total_tests': len(TEST_CASES),
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'results': []
        }
        
        for i, test_case in enumerate(TEST_CASES, 1):
            print(f"\n📋 Test {i}/{len(TEST_CASES)}: {test_case['name']}")
            print("-" * 60)
            
            try:
                result = self._run_single_test(test_case)
                summary['results'].append(result)
                
                if result['passed']:
                    print(f"✅ PASSED - Confidence: {result.get('confidence_score', 'N/A')}")
                    summary['passed'] += 1
                else:
                    print(f"❌ FAILED - Issues: {result.get('issues', [])}")
                    summary['failed'] += 1
                
                if result.get('warnings'):
                    print(f"⚠️  Warnings: {result.get('warnings')}")
                    summary['warnings'] += 1
            
            except Exception as e:
                print(f"❌ EXCEPTION: {str(e)}")
                summary['failed'] += 1
                summary['results'].append({
                    'test': test_case['name'],
                    'error': str(e),
                    'passed': False
                })
        
        # Print summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        print(f"Total: {summary['total_tests']} | ✅ Passed: {summary['passed']} | ❌ Failed: {summary['failed']} | ⚠️  Warnings: {summary['warnings']}")
        pass_rate = (summary['passed'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        return summary
    
    def _run_single_test(self, test_case: Dict) -> Dict:
        """Execute single test case"""
        result = {
            'test': test_case['name'],
            'test_type': test_case.get('test_type', 'unknown'),
            'guest': test_case['guest'].get('name'),
            'passed': True,
            'issues': [],
            'warnings': []
        }
        
        # Initialize guest session
        self.agent.initiate_guest_session(test_case['guest'])
        
        try:
            if 'queries' in test_case:
                # Multi-turn test
                for query in test_case['queries']:
                    response, metrics = self.agent.create_luxury_response(
                        query, test_case['guest']
                    )
                    result['confidence_score'] = metrics.get('confidence_score', 0)
            else:
                # Single query test
                response, metrics = self.agent.create_luxury_response(
                    test_case['query'], test_case['guest']
                )
                result['confidence_score'] = metrics.get('confidence_score', 0)
                result['response'] = response[:150] + '...' if len(response) > 150 else response
                
                # Run checks based on test type
                issues = self._validate_response(response, test_case)
                if issues:
                    result['passed'] = False
                    result['issues'] = issues
        
        finally:
            session_summary = self.agent.end_guest_session()
            if session_summary:
                result['session'] = session_summary
        
        return result
    
    def _validate_response(self, response: str, test_case: Dict) -> List[str]:
        """Validate response against test expectations"""
        issues = []
        
        response_lower = response.lower()
        metrics = test_case.get('expected_metrics', {})
        
        # Check for apologetic tone
        if metrics.get('apostrophe_free') and any(
            phrase in response_lower for phrase in ['i apologize', 'could you', 'i\'m having']
        ):
            issues.append("Response contains apologetic tone")
        
        # Check for specific recommendation
        if metrics.get('specific_recommendation') and len(response) < 50:
            issues.append("Response too vague or short")
        
        # Check VIP perks mention
        if metrics.get('vip_perks_mentioned') and test_case['guest'].get('loyalty_tier') == 'Black':
            vip_keywords = metrics['vip_perks_mentioned'].split('|')
            if not any(kw in response_lower for kw in vip_keywords):
                issues.append("BlackTier VIP perks not mentioned")
        
        # Check safety compliance
        if metrics.get('safety_priority'):
            diet_restriction = test_case['guest'].get('dietary_restrictions', '')
            if 'shellfish' in diet_restriction.lower() and 'shellfish' in response_lower:
                if 'alternative' not in response_lower and 'vegan' not in response_lower:
                    issues.append("Safety concern: recommending shellfish to allergic guest")
        
        # Check no clarification
        if metrics.get('no_clarification_asked') and '?' in response:
            # Too many questions might indicate asking for clarification
            q_count = response.count('?')
            if q_count > 2:
                issues.append(f"Asking for too much clarification ({q_count} questions)")
        
        return issues


class EvaluationReport:
    """Generate beautiful evaluation reports"""
    
    @staticmethod
    def generate_html_report(summary: Dict, filename: str = 'evaluation_report.html'):
        """Generate HTML evaluation report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Luxury Concierge Evaluation Report</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f5f5f5; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }}
                .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metric {{ display: inline-block; margin: 10px 20px; }}
                .pass {{ color: #28a745; font-weight: bold; }}
                .fail {{ color: #dc3545; font-weight: bold; }}
                .test-result {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #ddd; border-radius: 4px; }}
                .test-result.passed {{ border-left-color: #28a745; }}
                .test-result.failed {{ border-left-color: #dc3545; }}
                .timestamp {{ color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎩 Luxury Concierge Evaluation Report</h1>
                <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <div class="summary">
                <h2>Test Summary</h2>
                <div class="metric">Total Tests: <strong>{summary['total_tests']}</strong></div>
                <div class="metric"><span class="pass">✅ Passed: {summary['passed']}</span></div>
                <div class="metric"><span class="fail">❌ Failed: {summary['failed']}</span></div>
                <div class="metric">Pass Rate: <strong>{(summary['passed']/summary['total_tests']*100):.1f}%</strong></div>
            </div>
            <div class="summary">
                <h2>Detailed Results</h2>
        """
        
        for result in summary.get('results', []):
            status = 'passed' if result.get('passed') else 'failed'
            html += f"""
                <div class="test-result {status}">
                    <h3>{'✅' if result['passed'] else '❌'} {result.get('test', 'Unknown')}</h3>
                    <p><strong>Guest:</strong> {result.get('guest')}</p>
                    <p><strong>Type:</strong> {result.get('test_type')}</p>
                    <p><strong>Confidence:</strong> {result.get('confidence_score', 'N/A')}/10</p>
            """
            
            if result.get('issues'):
                html += "<p><strong style='color: #dc3545;'>Issues:</strong><ul>"
                for issue in result['issues']:
                    html += f"<li>{issue}</li>"
                html += "</ul></p>"
            
            if result.get('response'):
                html += f"<p><strong>Sample Response:</strong> {result['response']}</p>"
            
            html += "</div>"
        
        html += """
            </div>
        </body>
        </html>
        """
        
        with open(filename, 'w') as f:
            f.write(html)
        
        print(f"\n📄 Report generated: {filename}")


if __name__ == "__main__":
    print("🎯 Luxury Concierge Test Suite Module")
    print("Use: runner = ConciergeTestRunner(agent, kb)")
    print("     results = runner.run_all_tests()")
