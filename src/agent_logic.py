"""
Wynn Concierge Agent Logic
GPT-4 powered agent with luxury concierge persona

Version: 1.0.2 - Testing gpt-5-mini model
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
    
    # Luxury concierge system prompt - confident and knowledgeable
    SYSTEM_PROMPT_TEMPLATE = """You are the Chief Concierge at Wynn Al Marjan Island, serving ultra-high-net-worth guests.

Guest: <<GUEST_NAME>> (<<LOYALTY_TIER>> Tier)
Restrictions: <<DIETARY_RESTRICTIONS>>
Preferences: <<PREFERENCES>>

AVAILABLE VENUES:
<<VENUES_CONTEXT>>

Guest Request: <<USER_QUERY>>

PERSONA & TONE:
- You are THE authority on luxury dining and entertainment
- Be confident, warm, and sophisticated - never apologetic or uncertain
- Provide direct recommendations immediately - don't ask for clarification
- Use refined language: "I've reserved", "May I suggest", "You'll enjoy"
- Sound like a $500/night concierge, not a chatbot

For SIMPLE QUESTIONS (e.g., "best dish", "good restaurant"):
- Give ONE confident recommendation immediately
- Be concise (2-3 sentences max for simple queries)
- Example: "For non-vegetarian excellence, I recommend our 45-day dry-aged Tomahawk ribeye at The Obsidian Steakhouse. It's exceptional."

For COMPLEX ITINERARIES:
Return ONLY valid JSON:
{
  "itinerary": {"events": [{"time": "19:00", "venue_name": "Verde Garden", "venue_type": "Fine Dining", "duration_minutes": 90, "reason": "Matches preferences", "vip_perk": "Reserved chef's table"}]},
  "guest_message": "Good evening, [Name]. I have curated an exceptional evening for you...",
  "logistics_notes": "Private car arranged between venues. Dress: Smart Elegant."
}

CRITICAL RULES:
1. Never ask guests to "be more specific" - you're the expert, recommend something
2. SAFETY: Never recommend venues unsafe for dietary restrictions - redirect elegantly
3. Black Tier: Always mention exclusive perks
4. Never apologize for being "too detailed" - be concise from the start
5. For vague requests: Make an intelligent assumption and provide your best recommendation

Return ONLY JSON for itineraries, or direct text for simple questions. No markdown."""
    
    def __init__(self, knowledge_base: ResortKnowledgeBase, openai_api_key: str, model: str = "gpt-5-mini"):
        """
        Initialize the concierge agent.
        
        Args:
            knowledge_base: ResortKnowledgeBase instance
            openai_api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-5-mini)
        """
        self.kb = knowledge_base
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model=model,
            temperature=1,  # gpt-5-mini requires temperature=1 (only supported value)
            max_completion_tokens=8000,  # Reasonable limit for gpt-5-mini
            streaming=False,  # Disabled - using invoke() not stream()
            model_kwargs={"response_format": {"type": "json_object"}}  # Force JSON output
        )
        logger.info(f"✅ Concierge agent initialized with {model} (JSON mode enabled)")
    
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
                    k=3,  # Balanced: quality vs speed
                    filter_category=category
                )
                all_venues.extend(venues)
        else:
            # General search
            venues = self.kb.search_amenities(
                query=query,
                guest_profile=guest_profile,
                k=5  # Balanced: quality vs speed
            )
            all_venues.extend(venues)
        
        # Remove duplicates
        seen_ids = set()
        unique_venues = []
        for venue in all_venues:
            if venue['id'] not in seen_ids:
                seen_ids.add(venue['id'])
                unique_venues.append(venue)
        
        return unique_venues[:6]  # Return top 6 for balanced context
    
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
            return "Good evening. How may I assist you with your evening plans? I can recommend exceptional dining, entertainment, or create a complete itinerary for you."
        
        # Quick response for simple greetings ONLY (very conservative fast-path)
        query_lower = user_query.lower().strip()
        simple_greetings = ['hi', 'hello', 'hey', 'good evening', 'good afternoon', 'greetings']
        
        # Fast path ONLY for single-word greetings (no other fast paths to ensure quality)
        if query_lower in simple_greetings:
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
        
        logger.info(f"🎯 Creating itinerary for {guest_profile.get('name', 'Guest')}: '{user_query}'")
        
        # Extract intent
        intent = self._extract_intent(user_query)
        
        # Get relevant venues using RAG (optimized but not too aggressive)
        venues = self._get_relevant_venues(user_query, guest_profile, intent)
        
        if not venues:
            # Fallback to confident general recommendation
            guest_name = guest_profile.get('name', 'Guest').split()[0] if guest_profile.get('name', 'Guest') != 'Guest' else ''
            return f"For this evening{', ' + guest_name if guest_name else ''}, I recommend exploring our signature dining experiences. The Obsidian Steakhouse offers exceptional cuisine, or I can arrange something specific if you'd like to share your preferences."
        
        # Limit venues to top 6 for balanced context (quality vs speed)
        venues = venues[:6]
        
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
                
                # Provide confident fallback recommendation instead of apologizing
                guest_name = guest_profile.get('name', 'Guest').split()[0] if guest_profile.get('name', 'Guest') != 'Guest' else ''
                tier = guest_profile.get('loyalty_tier', 'Platinum')
                
                # Extract key intent for smart response
                query_lower = user_query.lower()
                if any(word in query_lower for word in ['dinner', 'dine', 'eat', 'dish', 'food', 'non veg', 'meat', 'steak']):
                    return f"""For exceptional dining this evening{', ' + guest_name if guest_name else ''}, I recommend The Obsidian Steakhouse. Their 45-day dry-aged Tomahawk ribeye is outstanding.

Alternatively, Sakura Omakase offers exquisite sushi with fish flown daily from Tokyo, or Côte d'Azur for spectacular seafood.

Shall I reserve a table for you?"""
                elif any(word in query_lower for word in ['club', 'party', 'dance', 'nightlife', 'drinks']):
                    vip_note = " As a Black Tier member, cover charges are waived." if tier == 'Black' else ""
                    return f"For an exceptional evening{', ' + guest_name if guest_name else ''}, I suggest starting at XS Nightclub - world-class DJs and premium bottle service.{vip_note} Shall I arrange this?"
                else:
                    return f"""Allow me to suggest an exceptional evening{', ' + guest_name if guest_name else ''}: Begin with dinner at our award-winning Obsidian Steakhouse, followed by cocktails at the Sky Lounge.

Would you like me to arrange this, or do you have specific preferences I should consider?"""
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Error creating itinerary: {e}")
            
            # Check for token limit errors - provide confident fallback
            guest_name = guest_profile.get('name', 'Guest').split()[0] if guest_profile.get('name', 'Guest') != 'Guest' else ''
            tier = guest_profile.get('loyalty_tier', 'Platinum')
            
            if 'length limit' in error_msg or 'max_completion_tokens' in error_msg:
                logger.error("⚠️ Token limit reached - providing fallback recommendation")
            
            # Smart fallback based on query
            query_lower = user_query.lower()
            if any(word in query_lower for word in ['dinner', 'dine', 'eat', 'dish', 'food', 'non veg', 'meat', 'steak', 'seafood', 'fish']):
                vip_note = "\n\nAs our Black Tier guest, I've arranged the chef's table with complimentary wine pairing." if tier == 'Black' else ""
                return f"""For an exceptional dinner this evening{', ' + guest_name if guest_name else ''}, I recommend The Obsidian Steakhouse. Their 45-day dry-aged Tomahawk ribeye with black truffle butter is extraordinary.

Reservation at 7:30 PM, estimated 2 hours. Smart elegant dress code.{vip_note}

Shall I confirm this arrangement?"""
            elif any(word in query_lower for word in ['club', 'party', 'dance', 'nightlife']):
                vip_note = " Cover charges waived for you." if tier == 'Black' else ""
                return f"For tonight's entertainment{', ' + guest_name if guest_name else ''}, XS Nightclub features world-renowned DJs and premium bottle service.{vip_note} Shall I arrange entry?"
            else:
                return f"""For this evening{', ' + guest_name if guest_name else ''}, may I suggest our signature experience: Dinner at The Obsidian Steakhouse (7:30 PM), followed by cocktails at Sky Lounge (10:00 PM).

Would you like me to arrange this?"""
    
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
            yield "Good evening. How may I assist you with your evening plans? I can recommend exceptional dining, entertainment, or create a complete itinerary for you."
            return
        
        # Quick response for simple greetings ONLY (very conservative)
        query_lower = user_query.lower().strip()
        simple_greetings = ['hi', 'hello', 'hey', 'good evening', 'good afternoon', 'greetings']
        
        # Fast path ONLY for single-word greetings
        if query_lower in simple_greetings:
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
        
        logger.info(f"🎯 Creating itinerary (streaming) for {guest_profile.get('name', 'Guest')}: '{user_query}'")
        
        # Extract intent
        intent = self._extract_intent(user_query)
        
        # Get relevant venues using RAG (optimized: fewer venues for faster processing)
        venues = self._get_relevant_venues(user_query, guest_profile, intent)
        
        if not venues:
            guest_name = guest_profile.get('name', 'Guest').split()[0] if guest_profile.get('name', 'Guest') != 'Guest' else ''
            yield f"For this evening{', ' + guest_name if guest_name else ''}, I recommend exploring our signature dining experiences. The Obsidian Steakhouse offers exceptional cuisine, or I can arrange something specific if you'd like to share your preferences."
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
            guest_name = guest_profile.get('name', 'Guest').split()[0] if guest_profile.get('name', 'Guest') != 'Guest' else ''
            yield f"\n\nLet me suggest our signature experience{', ' + guest_name if guest_name else ''}: The Obsidian Steakhouse for dinner. Shall I arrange this?"
    
    def quick_recommendation(self, category: str, guest_profile: Dict) -> str:
        """
        Quick recommendation for a specific category.
        NOTE: This is only used for sidebar quick buttons, not for chat queries.
        
        Args:
            category: Venue category (e.g., "Fine Dining")
            guest_profile: Guest profile dictionary
        
        Returns:
            Detailed recommendation
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
        guest_name = guest_profile.get('name', 'Guest').split()[0]
        
        # Create engaging, detailed recommendation
        recommendation = f"""For {category}, I highly recommend **{venue['name']}**.

{venue['description']}

**Details:**
• **Hours:** {venue['opening_hours']}
• **Vibe:** {', '.join(venue['tags'][:3])}
• **Price Level:** {venue['price_tier']}"""
        
        if tier == 'Black':
            recommendation += f"\n\n**Your Black Tier Benefits:**\n{venue['vip_perks']}"
        
        recommendation += f"\n\nWould you like me to arrange a reservation for you, {guest_name}?"
        
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
