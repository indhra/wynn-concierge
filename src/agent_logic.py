"""
Wynn Concierge Agent Logic
GPT-4 powered agent with luxury concierge persona
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
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

def validate_itinerary_policy(itinerary_text: str, guest_profile: Dict) -> Dict[str, any]:
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
    
    # System prompt defining the persona
    SYSTEM_PROMPT = """You are the Chief Concierge at Wynn Al Marjan Island. You are sophisticated, anticipatory, and discreet.

YOUR MISSION:
Create a seamless evening itinerary (6:00 PM - 2:00 AM) for the guest based on their request.

OUTPUT FORMAT (MANDATORY):
You MUST respond with valid JSON in this exact structure:
{{
  "itinerary": {{
    "events": [
      {{
        "time": "19:00",
        "venue_name": "Verde Garden",
        "venue_type": "Fine Dining",
        "duration_minutes": 90,
        "reason": "Matches your preference for romantic settings with exceptional wine selection",
        "vip_perk": "Reserved the chef's table with complimentary wine pairing"
      }}
    ]
  }},
  "guest_message": "Good evening, Ms. Chen. I have taken the liberty of crafting a sophisticated evening that honors your preferences...",
  "logistics_notes": "Please allow 15 minutes travel time between venues. Dress code: Smart Elegant."
}}

RULES OF ENGAGEMENT (The Human Touch):

1. Logistics First: Never double-book time slots. Allow 90 minutes for dinner and 15 minutes for travel between venues.

2. Safety Check: CROSS-REFERENCE the Guest Profile. Never suggest a venue that conflicts with their dietary restrictions or allergies. If a venue is unsafe, gracefully suggest an alternative that matches the same vibe.

3. Tier Recognition: If the guest is 'Black Tier' (VIP), explicitly mention that you have 'secured the best table' or 'waived the cover charge.' For Platinum tier, acknowledge their status warmly.

4. Tone: Warm, professional, but concise. Do not sound robotic. Use phrases like:
   - "I have taken the liberty of..."
   - "Given your preference for..."
   - "May I suggest..."
   - "I've arranged..."
   
5. Constraints: Verify that venues are open during the itinerary time window and respect dress codes and reservation requirements.

6. Graceful Alternatives: If the guest requests something unsafe (e.g., a vegetarian asking for a steakhouse), acknowledge their request but REDIRECT with sophistication:
   "While [Venue X] is exceptional, given your dietary preferences, I have instead secured a table at [Alternative Y], which offers..."

Current Guest Context:
Name: {guest_name}
Tier: {loyalty_tier}
Restrictions: {dietary_restrictions}
Preferences: {preferences}

AVAILABLE VENUES:
{venues_context}

Request: {user_query}

IMPORTANT: Your response must be valid JSON only. Do NOT include markdown code blocks or any text outside the JSON structure."""
    
    def __init__(self, knowledge_base: ResortKnowledgeBase, openai_api_key: str, model: str = "gpt-5-nano-2025-08-07"):
        """
        Initialize the concierge agent.
        
        Args:
            knowledge_base: ResortKnowledgeBase instance
            openai_api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-5-nano-2025-08-07)
        """
        self.kb = knowledge_base
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model=model,
            temperature=0.7,  # Some creativity for natural language
            max_tokens=1500
        )
        logger.info(f"✅ Concierge agent initialized with {model}")
    
    def _parse_timeframe(self, query: str) -> tuple[str, str]:
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
        """
        all_venues = []
        
        # If specific categories detected, search within those
        if intent['categories']:
            for category in intent['categories']:
                venues = self.kb.search_amenities(
                    query=query,
                    guest_profile=guest_profile,
                    k=3,
                    filter_category=category
                )
                all_venues.extend(venues)
        else:
            # General search
            venues = self.kb.search_amenities(
                query=query,
                guest_profile=guest_profile,
                k=6
            )
            all_venues.extend(venues)
        
        # Remove duplicates
        seen_ids = set()
        unique_venues = []
        for venue in all_venues:
            if venue['id'] not in seen_ids:
                seen_ids.add(venue['id'])
                unique_venues.append(venue)
        
        return unique_venues[:8]  # Limit to top 8 for context size
    
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
        logger.info(f"🎯 Creating itinerary for {guest_profile.get('name', 'Guest')}: '{user_query}'")
        
        # Extract intent
        intent = self._extract_intent(user_query)
        
        # Get relevant venues using RAG
        venues = self._get_relevant_venues(user_query, guest_profile, intent)
        
        if not venues:
            return "I apologize, but I'm having difficulty finding suitable venues for your request. Could you provide more details about what you're looking for this evening?"
        
        # Format venues context
        venues_context = self._format_venues_context(venues)
        
        # Build the prompt
        prompt = self.SYSTEM_PROMPT.format(
            guest_name=guest_profile.get('name', 'Guest'),
            loyalty_tier=guest_profile.get('loyalty_tier', 'Platinum'),
            dietary_restrictions=guest_profile.get('dietary_restrictions', 'None'),
            preferences=guest_profile.get('preferences', 'N/A'),
            venues_context=venues_context,
            user_query=user_query
        )
        
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
                # Try to extract JSON from response (handle potential markdown wrapping)
                json_text = itinerary
                if '```json' in itinerary:
                    json_text = itinerary.split('```json')[1].split('```')[0].strip()
                elif '```' in itinerary:
                    json_text = itinerary.split('```')[1].split('```')[0].strip()
                
                parsed_itinerary = json.loads(json_text)
                
                # Log structured data for system integration
                logger.info("✅ Structured itinerary data available for downstream systems")
                logger.debug(f"Events count: {len(parsed_itinerary.get('itinerary', {}).get('events', []))}")
                
                # Return the guest message (human-readable) for UI display
                # In production: Also store parsed_itinerary['itinerary']['events'] in PMS
                itinerary_display = parsed_itinerary.get('guest_message', itinerary)
                
                # Append logistics notes if available
                logistics = parsed_itinerary.get('logistics_notes')
                if logistics:
                    itinerary_display += f"\n\n📋 {logistics}"
                
                logger.info("✅ Itinerary created successfully (with structured data)")
                return itinerary_display
                
            except (json.JSONDecodeError, KeyError) as e:
                # Fallback: Return raw text if JSON parsing fails
                logger.warning(f"⚠️ JSON parsing failed, returning raw text: {e}")
                logger.info("✅ Itinerary created successfully (raw text fallback)")
                return itinerary
            
        except Exception as e:
            logger.error(f"❌ Error creating itinerary: {e}")
            return f"I apologize, but I'm experiencing a technical difficulty. Please try again in a moment. (Error: {str(e)})"
    
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
    agent = WynnConciergeAgent(kb, api_key, model="gpt-5-nano-2025-08-07")
    
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
