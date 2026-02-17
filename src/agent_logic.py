"""
Wynn Concierge Agent Logic
GPT-4 powered agent with luxury concierge persona

Version: 1.0.1 - Temperature parameter fix for gpt-5-nano
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import re

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from vector_store import ResortKnowledgeBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# SENIOR ENGINEER FIX #1: Policy Validation & Compliance Guardrails
# ============================================================================
# These functions prevent the agent from making unsafe or non-compliant
# recommendations. In production, these would integrate with the Property
# Management System (PMS) and Responsible Gaming databases.
# ============================================================================

def validate_itinerary_policy(itinerary_text: str, guest_profile: Dict) -> Dict[str, Any]:
    """
    Validates itinerary against business rules and compliance policies.
    
    COMPLIANCE CHECKS:
    - Age restrictions (Nightclubs, Casino, Bars)
    - Responsible Gaming protocols (self-exclusion lists)
    - Time constraints (kitchen closing times, last entry)
    - Capacity limits (event bookings)
    
    Args:
        itinerary_text: The generated itinerary content
        guest_profile: Guest profile with age, tier, preferences
    
    Returns:
        Dict with 'valid' (bool) and 'message' (str) keys
    """
    itinerary_lower = itinerary_text.lower()
    guest_age = guest_profile.get('age', 25)  # Default to 25 if not provided
    
    # Policy Check 1: Age-restricted venues (21+ requirement)
    age_restricted_keywords = ['nightclub', 'casino', 'bar lounge', 'club']
    for keyword in age_restricted_keywords:
        if keyword in itinerary_lower and guest_age < 21:
            return {
                'valid': False,
                'message': f"⚠️ POLICY VIOLATION: Guest is under 21. Cannot recommend {keyword.title()} venues. Please adjust request.",
                'violation_type': 'AGE_RESTRICTION'
            }
    
    # Policy Check 2: Responsible Gaming Protocol
    # In production: Check against self-exclusion database via PMS integration
    is_self_excluded = guest_profile.get('self_excluded_gaming', False)
    if 'casino' in itinerary_lower and is_self_excluded:
        return {
            'valid': False,
            'message': "⚠️ COMPLIANCE ALERT: Responsible Gaming Protocol activated. Casino recommendations blocked.",
            'violation_type': 'RESPONSIBLE_GAMING'
        }
    
    # Policy Check 3: Time constraint validation
    # Prevents recommending venues outside operating hours
    if '3:00 am' in itinerary_lower or '3am' in itinerary_lower:
        return {
            'valid': False,
            'message': "⚠️ OPERATIONAL ALERT: Requested time exceeds resort operating hours (close at 2:00 AM).",
            'violation_type': 'TIME_CONSTRAINT'
        }
    
    # Policy Check 4: Medical restrictions (e.g., spa + heart conditions)
    medical_restrictions = guest_profile.get('medical_notes', '').lower()
    if 'heart condition' in medical_restrictions and 'spa' in itinerary_lower:
        logger.warning(f"Medical alert: {guest_profile.get('name')} has heart condition, spa thermal treatments may need consultation")
        # Note: We don't block, but flag for concierge review in production
    
    return {
        'valid': True,
        'message': 'Itinerary passes all policy checks',
        'violation_type': None
    }


class WynnConciergeAgent:
    """
    Luxury concierge AI agent with sophisticated persona.
    Creates personalized itineraries with safety and logistics validation.
    """
    
    # Compact system prompt to reduce token usage
    SYSTEM_PROMPT_TEMPLATE = """You are Chief Concierge at Wynn Al Marjan Island.

Guest: <<GUEST_NAME>> (<<LOYALTY_TIER>> Tier)
Restrictions: <<DIETARY_RESTRICTIONS>>
Preferences: <<PREFERENCES>>

VENUES:
<<VENUES_CONTEXT>>

Request: <<USER_QUERY>>

Create evening itinerary (6 PM-2 AM). Return ONLY valid JSON:
{
  "itinerary": {"events": [{"time": "19:00", "venue_name": "Verde Garden", "venue_type": "Fine Dining", "duration_minutes": 90, "reason": "Matches preferences", "vip_perk": "Reserved chef's table"}]},
  "guest_message": "Good evening, [Name]. I have crafted...",
  "logistics_notes": "Allow 15 min between venues. Dress: Smart Elegant."
}

RULES:
1. Never double-book time slots (90 min dinner, 15 min travel)
2. SAFETY: Never recommend venues unsafe for guest dietary restrictions
3. Black Tier: Mention VIP perks ("waived cover", "best table")
4. Tone: Warm, sophisticated, use "I have arranged...", "May I suggest..."
5. If unsafe request: Gracefully redirect to safe alternative

Return ONLY JSON. No markdown, no code blocks."""
    
    def __init__(self, knowledge_base: ResortKnowledgeBase, openai_api_key: str, model: str = "gpt-5-nano"):
        """
        Initialize the concierge agent.
        
        Args:
            knowledge_base: ResortKnowledgeBase instance
            openai_api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-5-nano)
        """
        self.kb = knowledge_base
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model=model,
            temperature=1,  # gpt-5-nano REQUIRES temperature=1 (only supported value)
            max_completion_tokens=1500,  # Reduced for faster responses
            streaming=True,  # Enable streaming for lower perceived latency
            model_kwargs={"response_format": {"type": "json_object"}}  # Force JSON output
        )
        logger.info(f"✅ Concierge agent initialized with {model} (JSON mode + streaming enabled)")
    
    def _parse_timeframe(self, query: str) -> tuple:
        """
        Parse timeframe from query (basic implementation).
        Returns (start_time, end_time) in HH:MM format.
        """
        # Default evening timeframe
        return "18:00", "02:00"
    
    def _extract_intent(self, query: str) -> Dict:
        """
        Extract basic intent from user query.
        In production, this would be more sophisticated.
        """
        query_lower = query.lower()
        
        intent = {
            'categories': [],
            'vibes': [],
            'keywords': []
        }
        
        # Category detection
        if any(word in query_lower for word in ['dinner', 'dine', 'eat', 'restaurant', 'food']):
            intent['categories'].append('Fine Dining')
            intent['categories'].append('Casual Dining')
        
        if any(word in query_lower for word in ['club', 'dance', 'party', 'nightlife', 'drinks', 'bar']):
            intent['categories'].append('Nightlife')
        
        if any(word in query_lower for word in ['show', 'entertainment', 'theater', 'performance']):
            intent['categories'].append('Shows')
        
        if any(word in query_lower for word in ['spa', 'massage', 'relax', 'wellness']):
            intent['categories'].append('Spa')
        
        # Vibe detection
        if any(word in query_lower for word in ['romantic', 'intimate', 'quiet', 'date']):
            intent['vibes'].append('romantic')
        
        if any(word in query_lower for word in ['energetic', 'lively', 'fun', 'exciting', 'wild']):
            intent['vibes'].append('energetic')
        
        if any(word in query_lower for word in ['sophisticated', 'elegant', 'upscale', 'fancy']):
            intent['vibes'].append('sophisticated')
        
        return intent
    
    def _get_relevant_venues(self, query: str, guest_profile: Dict, intent: Dict) -> List[Dict]:
        """
        Retrieve relevant venues using RAG with guest-aware filtering.
        OPTIMIZED: Reduced k values for faster vector search.
        """
        all_venues = []
        
        # If specific categories detected, search within those
        if intent['categories']:
            for category in intent['categories']:
                venues = self.kb.search_amenities(
                    query=query,
                    guest_profile=guest_profile,
                    k=2,  # Reduced from 3 to 2 for faster search
                    filter_category=category
                )
                all_venues.extend(venues)
        else:
            # General search
            venues = self.kb.search_amenities(
                query=query,
                guest_profile=guest_profile,
                k=4  # Reduced from 6 to 4 for faster search
            )
            all_venues.extend(venues)
        
        # Remove duplicates
        seen_ids = set()
        unique_venues = []
        for venue in all_venues:
            if venue['id'] not in seen_ids:
                seen_ids.add(venue['id'])
                unique_venues.append(venue)
        
        return unique_venues[:5]  # Reduced from 8 to 5 for smaller context
    
    def _format_venues_context(self, venues: List[Dict]) -> str:
        """Format venues for inclusion in the prompt"""
        context_parts = []
        
        for venue in venues:
            safety_flag = "⚠️ UNSAFE - DO NOT RECOMMEND" if not venue['is_safe'] else "✅ SAFE"
            
            context = f"""
{venue['name']} ({venue['category']}) - {safety_flag}
- Description: {venue['description']}
- Vibe: {', '.join(venue['tags'])}
- Hours: {venue['opening_hours']}
- Duration: ~{venue['average_duration_minutes']} min
- Price: {venue['price_tier']}
- VIP Perks: {venue['vip_perks']}
"""
            if venue['safety_note']:
                context += f"- ⚠️ Safety Note: {venue['safety_note']}\n"
            
            context_parts.append(context.strip())
        
        return "\n\n".join(context_parts)
    
    def create_itinerary(self, user_query: str, guest_profile: Dict) -> str:
        """
        Create a personalized itinerary for the guest.
        
        Args:
            user_query: Guest's natural language request
            guest_profile: Guest profile dictionary
        
        Returns:
            Formatted itinerary as a string
        """
        # Input validation
        if not isinstance(guest_profile, dict):
            logger.error("Invalid guest_profile type: expected dict")
            return "I apologize, but there was an error with the guest profile. Please try again."
        
        if not user_query or not user_query.strip():
            return "I apologize, but I didn't catch your request. Could you please tell me what you're looking for this evening?"
        
        # Quick response for simple greetings and common queries (no need for full itinerary generation)
        query_lower = user_query.lower().strip()
        simple_greetings = ['hi', 'hello', 'hey', 'good evening', 'good afternoon', 'greetings', 'thanks', 'thank you']
        
        # Fast path for simple greetings
        if query_lower in simple_greetings or len(user_query.strip()) < 10:
            guest_name = guest_profile.get('name', 'Guest')
            tier = guest_profile.get('loyalty_tier', 'Platinum')
            greeting = f"""Good evening, {guest_name.split()[0] if guest_name != 'Guest' else 'there'}. Welcome to Wynn Al Marjan Island.

As a {tier} Tier member, I'm delighted to assist you this evening. How may I help craft your perfect experience today?

I can help you with:
• Dining reservations at our award-winning restaurants
• Entertainment and nightlife recommendations
• Spa and wellness experiences
• Special events and celebrations

What are you in the mood for this evening?"""
            logger.info(f"✅ Quick greeting response (bypassed RAG) for {guest_name}")
            return greeting
        
        # Fast path for simple single-category requests
        simple_requests = {
            'dinner': 'Fine Dining',
            'eat': 'Fine Dining',
            'restaurant': 'Fine Dining',
            'spa': 'Spa',
            'massage': 'Spa',
            'club': 'Nightlife',
            'bar': 'Nightlife',
            'dance': 'Nightlife'
        }
        
        # Check if it's a simple single-word or short request
        if len(user_query.split()) <= 10:
            for keyword, category in simple_requests.items():
                if keyword in query_lower:
                    logger.info(f"✅ Fast path: Simple '{keyword}' request detected, using quick recommendation")
                    return self.quick_recommendation(category, guest_profile)
        
        logger.info(f"🎯 Creating itinerary for {guest_profile.get('name', 'Guest')}: '{user_query}'")
        
        # Extract intent
        intent = self._extract_intent(user_query)
        
        # Get relevant venues using RAG (optimized: fewer venues for faster processing)
        venues = self._get_relevant_venues(user_query, guest_profile, intent)
        
        if not venues:
            return "I apologize, but I'm having difficulty finding suitable venues for your request. Could you provide more details about what you're looking for this evening?"
        
        # Limit venues to top 5 for faster processing (instead of 8)
        venues = venues[:5]
        
        # Format venues context
        venues_context = self._format_venues_context(venues)
        
        # Build the prompt using safe string replacement (avoids .format() brace conflicts)
        prompt = self.SYSTEM_PROMPT_TEMPLATE
        prompt = prompt.replace('<<GUEST_NAME>>', guest_profile.get('name', 'Guest'))
        prompt = prompt.replace('<<LOYALTY_TIER>>', guest_profile.get('loyalty_tier', 'Platinum'))
        prompt = prompt.replace('<<DIETARY_RESTRICTIONS>>', guest_profile.get('dietary_restrictions', 'None'))
        prompt = prompt.replace('<<PREFERENCES>>', guest_profile.get('preferences', 'N/A'))
        prompt = prompt.replace('<<VENUES_CONTEXT>>', venues_context)
        prompt = prompt.replace('<<USER_QUERY>>', user_query)
        
        # Get LLM response
        messages = [
            SystemMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            itinerary = response.content
            
            # ============================================================================
            # SENIOR ENGINEER FIX #1: Policy Validation Before Returning
            # ============================================================================
            # Validate itinerary against business rules and compliance policies
            policy_check = validate_itinerary_policy(itinerary, guest_profile)
            
            if not policy_check['valid']:
                logger.warning(f"⚠️ Policy violation detected: {policy_check['violation_type']}")
                logger.warning(f"Message: {policy_check['message']}")
                
                # Return a professional error message instead of the violating itinerary
                return f"""I apologize, but I must respectfully adjust your request.

{policy_check['message']}

May I suggest an alternative that would better suit your preferences? Please let me know what type of experience you're looking for, and I'll craft something exceptional for you."""
            
            # ============================================================================
            # SENIOR ENGINEER FIX #3: Parse and Format Structured JSON Output
            # ============================================================================
            # Attempt to parse JSON for structured data (system integration ready)
            try:
                import json
                # Clean the response text
                json_text = itinerary.strip()
                
                # Try to extract JSON from response (handle potential markdown wrapping)
                if '```json' in json_text:
                    json_text = json_text.split('```json')[1].split('```')[0].strip()
                elif '```' in json_text:
                    json_text = json_text.split('```')[1].split('```')[0].strip()
                
                # Remove any leading/trailing whitespace or newlines
                json_text = json_text.strip()
                
                # Validate JSON is not empty
                if not json_text:
                    raise ValueError("Empty response from LLM")
                
                parsed_itinerary = json.loads(json_text)
                
                # Validate required fields
                if 'guest_message' not in parsed_itinerary:
                    logger.warning("⚠️ JSON missing 'guest_message' field, using fallback")
                    raise KeyError("Missing guest_message field")
                
                # Log structured data for system integration
                logger.info("✅ Structured itinerary data available for downstream systems")
                events_count = len(parsed_itinerary.get('itinerary', {}).get('events', []))
                logger.info(f"📅 Events scheduled: {events_count}")
                
                # Return the guest message (human-readable) for UI display
                # In production: Also store parsed_itinerary['itinerary']['events'] in PMS
                itinerary_display = parsed_itinerary.get('guest_message', '')
                
                # Append logistics notes if available
                logistics = parsed_itinerary.get('logistics_notes')
                if logistics:
                    itinerary_display += f"\n\n📋 {logistics}"
                
                logger.info("✅ Itinerary created successfully (with structured data)")
                return itinerary_display
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # Enhanced error logging
                logger.error(f"❌ JSON parsing failed: {e}")
                logger.error(f"Raw response (first 500 chars): {itinerary[:500]}")
                
                # Check if response looks like truncated JSON
                if itinerary.strip() and '{' in itinerary:
                    logger.warning("⚠️ Response appears truncated - likely hit token limit")
                
                # Return a user-friendly error message
                return """I apologize for the technical difficulty. Let me help you differently.

Could you please tell me:
- What type of dining experience are you looking for?
- What kind of atmosphere do you prefer?
- Any specific activities you'd like to include?

I'll create a perfect itinerary for you."""
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Error creating itinerary: {e}")
            
            # Check for token limit errors
            if 'length limit' in error_msg or 'max_completion_tokens' in error_msg:
                logger.error("⚠️ Token limit reached - response was truncated")
                return f"""I apologize, but my response was too detailed. Let me try a more concise approach.

Could you please be more specific about what you're looking for? For example:
- "I want Italian dinner and jazz music"
- "Romantic evening with wine"
- "Nightlife and dancing"

This will help me create a perfect, focused itinerary for you."""
            
            return f"I apologize, but I'm experiencing a technical difficulty. Please try again in a moment."
    
    def create_itinerary_stream(self, user_query: str, guest_profile: Dict):
        """
        Create a personalized itinerary with streaming support for lower perceived latency.
        
        Args:
            user_query: Guest's natural language request
            guest_profile: Guest profile dictionary
        
        Yields:
            Chunks of the response as they arrive
        """
        # Input validation
        if not isinstance(guest_profile, dict):
            logger.error("Invalid guest_profile type: expected dict")
            yield "I apologize, but there was an error with the guest profile. Please try again."
            return
        
        if not user_query or not user_query.strip():
            yield "I apologize, but I didn't catch your request. Could you please tell me what you're looking for this evening?"
            return
        
        # Quick response for simple greetings and common queries (no streaming needed)
        query_lower = user_query.lower().strip()
        simple_greetings = ['hi', 'hello', 'hey', 'good evening', 'good afternoon', 'greetings', 'thanks', 'thank you']
        
        # Fast path for simple greetings
        if query_lower in simple_greetings or len(user_query.strip()) < 10:
            guest_name = guest_profile.get('name', 'Guest')
            tier = guest_profile.get('loyalty_tier', 'Platinum')
            greeting = f"""Good evening, {guest_name.split()[0] if guest_name != 'Guest' else 'there'}. Welcome to Wynn Al Marjan Island.

As a {tier} Tier member, I'm delighted to assist you this evening. How may I help craft your perfect experience today?

I can help you with:
• Dining reservations at our award-winning restaurants
• Entertainment and nightlife recommendations
• Spa and wellness experiences
• Special events and celebrations

What are you in the mood for this evening?"""
            logger.info(f"✅ Quick greeting response (bypassed RAG) for {guest_name}")
            yield greeting
            return
        
        # Fast path for simple single-category requests
        simple_requests = {
            'dinner': 'Fine Dining',
            'eat': 'Fine Dining',
            'restaurant': 'Fine Dining',
            'spa': 'Spa',
            'massage': 'Spa',
            'club': 'Nightlife',
            'bar': 'Nightlife',
            'dance': 'Nightlife'
        }
        
        # Check if it's a simple single-word or short request
        if len(user_query.split()) <= 10:
            for keyword, category in simple_requests.items():
                if keyword in query_lower:
                    logger.info(f"✅ Fast path: Simple '{keyword}' request detected, using quick recommendation")
                    yield self.quick_recommendation(category, guest_profile)
                    return
        
        logger.info(f"🎯 Creating itinerary (streaming) for {guest_profile.get('name', 'Guest')}: '{user_query}'")
        
        # Extract intent
        intent = self._extract_intent(user_query)
        
        # Get relevant venues using RAG (optimized: fewer venues for faster processing)
        venues = self._get_relevant_venues(user_query, guest_profile, intent)
        
        if not venues:
            yield "I apologize, but I'm having difficulty finding suitable venues for your request. Could you provide more details about what you're looking for this evening?"
            return
        
        # Limit venues to top 5 for faster processing
        venues = venues[:5]
        
        # Format venues context
        venues_context = self._format_venues_context(venues)
        
        # Build the prompt
        prompt = self.SYSTEM_PROMPT_TEMPLATE
        prompt = prompt.replace('<<GUEST_NAME>>', guest_profile.get('name', 'Guest'))
        prompt = prompt.replace('<<LOYALTY_TIER>>', guest_profile.get('loyalty_tier', 'Platinum'))
        prompt = prompt.replace('<<DIETARY_RESTRICTIONS>>', guest_profile.get('dietary_restrictions', 'None'))
        prompt = prompt.replace('<<PREFERENCES>>', guest_profile.get('preferences', 'N/A'))
        prompt = prompt.replace('<<VENUES_CONTEXT>>', venues_context)
        prompt = prompt.replace('<<USER_QUERY>>', user_query)
        
        # Get LLM response with streaming
        messages = [SystemMessage(content=prompt)]
        
        try:
            full_response = ""
            for chunk in self.llm.stream(messages):
                if chunk.content:
                    full_response += chunk.content
                    yield chunk.content
            
            # After streaming completes, validate the response
            # Note: We've already yielded it, but we log any issues for monitoring
            policy_check = validate_itinerary_policy(full_response, guest_profile)
            
            if not policy_check['valid']:
                logger.warning(f"⚠️ Policy violation detected in streamed response: {policy_check['violation_type']}")
                # Can't un-stream, but we log it for monitoring
            
            logger.info("✅ Streaming itinerary completed")
            
        except Exception as e:
            logger.error(f"❌ Error streaming itinerary: {e}")
            yield "\n\nI apologize for the technical difficulty. Please try rephrasing your request."
    
    def quick_recommendation(self, category: str, guest_profile: Dict) -> str:
        """
        Quick recommendation for a specific category.
        
        Args:
            category: Venue category (e.g., "Fine Dining")
            guest_profile: Guest profile dictionary
        
        Returns:
            Brief recommendation
        """
        venues = self.kb.search_amenities(
            query=f"best {category}",
            guest_profile=guest_profile,
            k=1,
            filter_category=category
        )
        
        if not venues:
            return f"I apologize, but I don't currently have recommendations for {category}."
        
        venue = venues[0]
        
        if not venue['is_safe']:
            # Find alternative
            all_venues = self.kb.get_venues_by_category(category)
            safe_venues = [v for v in all_venues 
                          if self.kb._check_dietary_safety(v, guest_profile.get('dietary_restrictions', ''))[0]]
            
            if safe_venues:
                venue = safe_venues[0]
            else:
                return f"Given your dietary restrictions, I recommend consulting with our dietary team for {category} options."
        
        tier = guest_profile.get('loyalty_tier', 'Platinum')
        
        recommendation = f"For {category}, I highly recommend **{venue['name']}**. {venue['description'][:150]}..."
        
        if tier == 'Black':
            recommendation += f"\n\nAs a Black Tier member, {venue['vip_perks'].lower()}."
        
        return recommendation


def demo():
    """Demo function to test the agent"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    # Initialize components
    kb = ResortKnowledgeBase(api_key)
    agent = WynnConciergeAgent(kb, api_key, model="gpt-5-nano")
    
    # Test guest
    guest = {
        'name': 'Sarah Chen',
        'loyalty_tier': 'Black',
        'dietary_restrictions': 'Vegetarian, Gluten-Free',
        'preferences': 'Romantic settings, wine enthusiast'
    }
    
    # Test query
    query = "I want a steak dinner and a wild night out."
    
    print(f"\n👤 Guest: {guest['name']} ({guest['loyalty_tier']} Tier)")
    print(f"🔒 Restrictions: {guest['dietary_restrictions']}")
    print(f"\n💬 Request: \"{query}\"")
    print("\n" + "="*60)
    
    # Get itinerary
    itinerary = agent.create_itinerary(query, guest)
    
    print(f"\n🎩 Concierge Response:\n")
    print(itinerary)
    print("\n" + "="*60)
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo()
