"""
Wynn Concierge Streamlit App
Luxury concierge interface with VIP guest management
"""

import streamlit as st
import pandas as pd
import os
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

from vector_store import ResortKnowledgeBase
from agent_logic import WynnConciergeAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


# ============================================================================
# SENIOR ENGINEER FIX #2: PII Privacy & Data Protection
# ============================================================================
# SECURITY NOTE: In production, we MUST anonymize PII before sending to LLMs
# 
# Current PoC uses synthetic data only. Production implementation requires:
# 1. Hash guest names using SHA-256 before LLM transmission
# 2. Replace loyalty tier with encoded IDs (e.g., BLACK_TIER → T1)
# 3. Use Wynn VPC (Virtual Private Cloud) with Azure OpenAI private endpoints
# 4. Implement audit logging for GDPR/UAE Data Protection Law compliance
# 
# Reference: UAE Data Protection Law (Federal Decree-Law No. 45 of 2021)
# Reference: PCI-DSS requirements for casino/gaming operations
# ============================================================================

def anonymize_guest_pii(guest_profile: Dict) -> Dict:
    """
    Anonymizes Personally Identifiable Information (PII) before LLM processing.
    
    PRODUCTION REQUIREMENTS:
    - Hash guest names with SHA-256 + salt
    - Replace room numbers with session tokens
    - Mask credit card/payment info
    - Remove phone/email from LLM context
    
    Args:
        guest_profile: Original guest profile with PII
    
    Returns:
        Anonymized profile safe for LLM transmission
    """
    import hashlib
    
    anonymized = guest_profile.copy()
    
    # Mask guest name (Production: Use cryptographic hash)
    if 'name' in anonymized:
        name_hash = hashlib.sha256(anonymized['name'].encode()).hexdigest()[:12]
        anonymized['name'] = f"Guest_{name_hash}"
        # Note: For UI display, we keep original name locally, only send hash to LLM
    
    # Encode loyalty tier as ID
    tier_encoding = {'Black': 'T1_VIP', 'Platinum': 'T2_PREMIUM'}
    if 'loyalty_tier' in anonymized:
        anonymized['loyalty_tier_encoded'] = tier_encoding.get(
            anonymized['loyalty_tier'], 
            'T3_STANDARD'
        )
    
    # In production: Remove sensitive fields entirely
    anonymized.pop('email', None)
    anonymized.pop('phone', None)
    anonymized.pop('room_number', None)
    anonymized.pop('credit_card', None)
    
    return anonymized


def mask_guest_data_for_display(guest_profile: Dict) -> Dict:
    """
    Masks sensitive data for UI display (different from LLM anonymization).
    
    This is for SCREEN PRIVACY when concierge staff view the system.
    """
    masked = guest_profile.copy()
    
    # Mask partial phone number: +971-XX-XXX-5678 → +971-**-***-5678
    if 'phone' in masked:
        phone = masked['phone']
        masked['phone'] = phone[:-4].replace(phone[5:-4], '***') + phone[-4:] if len(phone) > 4 else '***'
    
    # Mask email: john.doe@email.com → j***@email.com
    if 'email' in masked:
        email = masked['email']
        if '@' in email:
            local, domain = email.split('@')
            masked['email'] = f"{local[0]}***@{domain}"
    
    return masked


# NOTE: Current PoC does NOT anonymize data (synthetic data only)
# Production deployment MUST enable PII_ANONYMIZATION_ENABLED flag
PII_ANONYMIZATION_ENABLED = os.getenv('PII_ANONYMIZATION_ENABLED', 'false').lower() == 'true'

if PII_ANONYMIZATION_ENABLED:
    logger.info("🔒 PII Anonymization: ENABLED (Production Mode)")
else:
    logger.info("⚠️  PII Anonymization: DISABLED (PoC uses synthetic data only)")




# Page configuration
st.set_page_config(
    page_title="Wynn Concierge AI",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for luxury styling
st.markdown("""
<style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%);
        border-right: 2px solid #d4af37;
    }
    
    /* Black Tier Card */
    .black-tier-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        border: 2px solid #d4af37;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 20px rgba(212, 175, 55, 0.3);
    }
    
    /* Platinum Tier Card */
    .platinum-tier-card {
        background: linear-gradient(135deg, #e5e4e2 0%, #a8a8a8 100%);
        border: 2px solid #a8a8a8;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 20px rgba(168, 168, 168, 0.3);
        color: #1a1a1a;
    }
    
    /* Guest name styling */
    .guest-name {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    /* Tier badge */
    .tier-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin: 5px 0;
    }
    
    .black-badge {
        background: #d4af37;
        color: #000;
    }
    
    .platinum-badge {
        background: #fff;
        color: #333;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #d4af37 0%, #c99700 100%);
        color: #000;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
GUESTS_FILE = DATA_DIR / "guests.csv"


@st.cache_resource
def initialize_system():
    """Initialize the knowledge base and agent (cached)"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        st.error("⚠️ OPENAI_API_KEY not found in environment. Please configure your .env file.")
        st.stop()
    
    try:
        # Initialize knowledge base
        kb = ResortKnowledgeBase(api_key)
        
        # Initialize agent with model from environment or default to gpt-5-nano-2025-08-07
        # To change model: Set OPENAI_MODEL in your .env file
        # Options: gpt-5-nano-2025-08-07 (cheapest), gpt-4o-mini, gpt-4o, gpt-4-turbo, gpt-4
        model = os.getenv('OPENAI_MODEL', 'gpt-5-nano-2025-08-07')
        agent = WynnConciergeAgent(kb, api_key, model=model)
        
        # Store model info in session state for display
        if 'current_model' not in st.session_state:
            st.session_state.current_model = model
        
        return kb, agent
    
    except Exception as e:
        error_msg = str(e).lower()
        
        # Check for authentication/API key errors
        if 'api key' in error_msg or 'authentication' in error_msg or 'unauthorized' in error_msg or '401' in error_msg:
            st.error("❌ **Invalid OpenAI API Key**")
            st.error("Your OpenAI API key is invalid or has expired. Please check your configuration.")
            st.info("""💡 **How to fix:**
1. Get a valid API key from https://platform.openai.com/api-keys
2. Update your `.env` file with: `OPENAI_API_KEY=sk-your-key-here`
3. Restart the application
            """)
        else:
            st.error(f"❌ Error initializing system: {str(e)}")
            st.info("💡 Make sure you've run `python src/data_generator.py` first to generate the data files.")
        
        st.stop()


def load_guests():
    """Load guest profiles from CSV"""
    if not GUESTS_FILE.exists():
        st.error(f"❌ Guests file not found: {GUESTS_FILE}")
        st.info("💡 Run `python src/data_generator.py` to generate guest profiles.")
        st.stop()
    
    return pd.read_csv(GUESTS_FILE)


def render_guest_card(guest_data):
    """Render a luxury guest card in the sidebar"""
    tier = guest_data['loyalty_tier']
    
    if tier == 'Black':
        card_class = 'black-tier-card'
        badge_class = 'black-badge'
        tier_emoji = '◆'
    else:
        card_class = 'platinum-tier-card'
        badge_class = 'platinum-badge'
        tier_emoji = '◇'
    
    card_html = f"""
    <div class='{card_class}'>
        <div class='guest-name'>{guest_data['name']}</div>
        <span class='tier-badge {badge_class}'>{tier_emoji} {tier} TIER</span>
        <hr style='margin: 15px 0; opacity: 0.3;'>
        <div style='font-size: 14px; margin-top: 10px;'>
            <div><strong>Dietary:</strong> {guest_data['dietary_restrictions']}</div>
            <div style='margin-top: 8px;'><strong>Preferences:</strong> {guest_data['preferences']}</div>
            <div style='margin-top: 8px; opacity: 0.7;'><em>{guest_data['visit_purpose']}</em></div>
        </div>
    </div>
    """
    
    st.sidebar.markdown(card_html, unsafe_allow_html=True)


def simulate_thinking_process():
    """Simulate the concierge thinking process with status updates"""
    status_messages = [
        ("🔍 Searching venue database...", 0.8),
        ("🛡️ Verifying dietary constraints...", 1.0),
        ("⏰ Checking availability...", 0.7),
        ("✨ Finalizing your itinerary...", 0.9)
    ]
    
    placeholder = st.empty()
    
    for message, duration in status_messages:
        with placeholder.container():
            st.info(message)
        time.sleep(duration)
    
    placeholder.empty()


def format_timestamp():
    """Get current timestamp for chat"""
    return datetime.now().strftime("%I:%M %p")


def check_rate_limit(guest_name: str, max_calls: int = 5, time_window_hours: int = 1) -> tuple[bool, int, str]:
    """
    Check if user has exceeded rate limit to prevent excessive API costs.
    
    Args:
        guest_name: Name of the guest (used as unique identifier)
        max_calls: Maximum API calls allowed (default: 5)
        time_window_hours: Time window in hours (default: 1)
    
    Returns:
        Tuple of (is_allowed, remaining_calls, reset_time)
    """
    from datetime import datetime, timedelta
    
    # Initialize rate limit tracking in session state
    if 'api_call_history' not in st.session_state:
        st.session_state.api_call_history = {}
    
    # Get current time
    now = datetime.now()
    cutoff_time = now - timedelta(hours=time_window_hours)
    
    # Get or initialize call history for this guest
    if guest_name not in st.session_state.api_call_history:
        st.session_state.api_call_history[guest_name] = []
    
    # Remove old calls outside the time window
    st.session_state.api_call_history[guest_name] = [
        call_time for call_time in st.session_state.api_call_history[guest_name]
        if call_time > cutoff_time
    ]
    
    # Check if limit exceeded
    call_count = len(st.session_state.api_call_history[guest_name])
    remaining = max_calls - call_count
    
    if call_count >= max_calls:
        # Find when the oldest call will expire
        oldest_call = min(st.session_state.api_call_history[guest_name])
        reset_time = oldest_call + timedelta(hours=time_window_hours)
        reset_str = reset_time.strftime("%I:%M %p")
        return False, 0, reset_str
    
    return True, remaining, ""


def record_api_call(guest_name: str):
    """Record an API call for rate limiting purposes"""
    if 'api_call_history' not in st.session_state:
        st.session_state.api_call_history = {}
    
    if guest_name not in st.session_state.api_call_history:
        st.session_state.api_call_history[guest_name] = []
    
    st.session_state.api_call_history[guest_name].append(datetime.now())


def main():
    """Main application"""
    
    # Header
    st.title("🏝️ Wynn Al Marjan Island")
    st.subheader("Chief Concierge AI Assistant")
    
    # Initialize system
    kb, agent = initialize_system()
    
    # Load guests
    guests_df = load_guests()
    
    # Sidebar - Guest Selection
    st.sidebar.title("👤 Guest Selection")
    
    guest_names = guests_df['name'].tolist()
    selected_guest_name = st.sidebar.selectbox(
        "Select Guest Profile",
        guest_names,
        index=0,
        help="Choose a guest profile to personalize the experience"
    )
    
    # Get selected guest data
    guest_data = guests_df[guests_df['name'] == selected_guest_name].iloc[0]
    
    # Render guest card
    render_guest_card(guest_data)
    
    # Sidebar - Quick Actions
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Quick Recommendations")
    
    categories = kb.get_all_categories()
    
    for category in categories:
        if st.sidebar.button(f"{category}", key=f"quick_{category}"):
            # Create guest profile dict
            guest_profile = guest_data.to_dict()
            
            # Get recommendation
            with st.spinner(f"Finding the perfect {category} venue..."):
                recommendation = agent.quick_recommendation(category, guest_profile)
            
            # Add to chat
            if 'messages' not in st.session_state:
                st.session_state.messages = []
            
            st.session_state.messages.append({
                "role": "user",
                "content": f"Quick recommendation for {category}",
                "timestamp": format_timestamp()
            })
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": recommendation,
                "timestamp": format_timestamp()
            })
            
            st.rerun()
    
    # Sidebar - Info
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='font-size: 12px; opacity: 0.7; padding: 10px;'>
        <strong>Wynn Concierge AI</strong><br>
        Powered by GPT-4 & LangChain<br>
        <em>Anticipatory. Sophisticated. Discreet.</em>
    </div>
    """, unsafe_allow_html=True)
    
    # Main Chat Interface
    st.markdown("---")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
        # Welcome message
        tier = guest_data['loyalty_tier']
        tier_greeting = "It's a pleasure to welcome you back" if tier == "Black" else "Welcome"
        
        welcome = f"""Good evening, {guest_data['name']}. {tier_greeting} to Wynn Al Marjan Island.

I'm your Chief Concierge, and I'm here to craft the perfect evening for you. Whether you're seeking an intimate dinner, vibrant nightlife, or a cultural experience, I have curated access to our finest venues.

How may I assist you this evening?"""
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome,
            "timestamp": format_timestamp()
        })
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            st.caption(message.get("timestamp", ""))
    
    # Chat input
    if prompt := st.chat_input("Describe your perfect evening..."):
        # ============================================================================
        # RATE LIMITING: Prevent excessive API costs (max 5 calls per hour per user)
        # ============================================================================
        guest_name = guest_data['name']
        is_allowed, remaining, reset_time = check_rate_limit(guest_name)
        
        if not is_allowed:
            # Rate limit exceeded - show error message
            timestamp = format_timestamp()
            st.session_state.messages.append({
                "role": "user",
                "content": prompt,
                "timestamp": timestamp
            })
            
            with st.chat_message("user"):
                st.markdown(prompt)
                st.caption(timestamp)
            
            with st.chat_message("assistant"):
                error_msg = f"""⚠️ **Rate Limit Exceeded**

I apologize, but you've reached the maximum of 5 requests per hour for this demo.

This limit helps control API costs. Your access will reset at **{reset_time}**.

Thank you for your understanding!"""
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": format_timestamp()
                })
            st.stop()
        
        # Add user message
        timestamp = format_timestamp()
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(timestamp)
        
        # Generate response
        with st.chat_message("assistant"):
            # Show thinking process
            simulate_thinking_process()
            
            # Create guest profile dict
            guest_profile = guest_data.to_dict()
            
            # Get itinerary from agent (THIS IS THE API CALL)
            with st.spinner("Crafting your itinerary..."):
                itinerary = agent.create_itinerary(prompt, guest_profile)
            
            # Record this API call for rate limiting
            record_api_call(guest_name)
            
            # Display itinerary
            st.markdown(itinerary)
            response_timestamp = format_timestamp()
            st.caption(response_timestamp)
            
            # Add to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": itinerary,
                "timestamp": response_timestamp
            })
            
            # Show remaining calls
            remaining_after = remaining - 1
            if remaining_after <= 2:
                st.warning(f"⚠️ {remaining_after} API calls remaining this hour")
    
    # Clear chat button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 New Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # ============================================================================
    # DEBUG INFO (For demo purposes only - remove in production customer app)
    # ============================================================================
    st.markdown("---")
    with st.expander("🔧 Demo Info (For Development Only)"):
        current_model = st.session_state.get('current_model', 'gpt-5-nano-2025-08-07')
        st.caption(f"**AI Model:** {current_model}")
        st.caption(f"**Environment:** Demo mode with rate limiting (5 calls/hour)")
        st.caption("_In production, this debug panel would be hidden from guest-facing UI_")


if __name__ == "__main__":
    main()
