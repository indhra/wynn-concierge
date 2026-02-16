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


class WynnConciergeAgent:
    """
    Luxury concierge AI agent with sophisticated persona.
    Creates personalized itineraries with safety and logistics validation.
    """
    
    # System prompt defining the persona
    SYSTEM_PROMPT = """You are the Chief Concierge at Wynn Al Marjan Island. You are sophisticated, anticipatory, and discreet.

YOUR MISSION:
Create a seamless evening itinerary (6:00 PM - 2:00 AM) for the guest based on their request.

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

RESPONSE FORMAT:
Provide a time-sequenced itinerary with:
- Venue name and category
- Arrival time
- Why it matches their request
- VIP perks (if Black Tier)
- Brief logistics note (travel time, dress code if strict)

Be conversational, not a bulleted list. Make them feel special."""
    
    def __init__(self, knowledge_base: ResortKnowledgeBase, openai_api_key: str, model: str = "gpt-4"):
        """
        Initialize the concierge agent.
        
        Args:
            knowledge_base: ResortKnowledgeBase instance
            openai_api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4)
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
        logger.info(f"🎯 Creating itinerary for {guest_profile['name']}: '{user_query}'")
        
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
            
            logger.info("✅ Itinerary created successfully")
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
    agent = WynnConciergeAgent(kb, api_key, model="gpt-4")
    
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
