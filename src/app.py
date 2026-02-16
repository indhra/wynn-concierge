"""
Wynn Concierge Streamlit App
Luxury concierge interface with VIP guest management
"""

import streamlit as st
import pandas as pd
import os
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from vector_store import ResortKnowledgeBase
from agent_logic import WynnConciergeAgent

# Load environment variables
load_dotenv()

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
        
        # Initialize agent
        model = os.getenv('OPENAI_MODEL', 'gpt-4')
        agent = WynnConciergeAgent(kb, api_key, model=model)
        
        return kb, agent
    
    except Exception as e:
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
            
            # Get itinerary from agent
            with st.spinner("Crafting your itinerary..."):
                itinerary = agent.create_itinerary(prompt, guest_profile)
            
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
    
    # Clear chat button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 New Chat"):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()
