# Wynn Concierge AI - Quick Start Guide

## 🎯 What is This?

A production-ready AI concierge system that creates personalized luxury itineraries while ensuring guest safety through dietary restriction filtering and VIP tier recognition.

## 🚀 Installation (2 Minutes)

### Option 1: Automated Setup (Recommended)
```bash
./setup.sh
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY

# Generate data
python src/data_generator.py
```

## 🔑 Get Your OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Create a new secret key
3. Add it to `.env`:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

## ▶️ Run the Application

```bash
streamlit run src/app.py
```

The app will open in your browser at `http://localhost:8501`

## 🧪 Test the System

Run the comprehensive test suite:
```bash
python test_system.py
```

This validates:
- ✅ Data generation (25 venues, 5 guests)
- ✅ Vector store & RAG search
- ✅ Agent persona & itinerary creation
- ✅ Safety filtering (allergies, dietary restrictions)

## 📱 Using the App

1. **Select a Guest** from the sidebar
2. **View their Profile** (dietary restrictions, preferences, VIP tier)
3. **Type a Request** like:
   - "I want a romantic dinner followed by live jazz"
   - "Plan a wild night out"
   - "Something quiet and sophisticated"
4. **Watch** the AI create a personalized, safe itinerary

## 🎬 The "Ultimate Test"

This is the scenario from the plan that proves the AI works:

1. Select guest: **Sarah Chen** (Vegetarian)
2. Type: **"I want a steak dinner and a wild night out"**
3. Expected: AI should gracefully redirect to vegetarian-friendly fine dining

**Why this matters**: It proves the AI doesn't just respond—it **protects** the guest.

## 📂 Project Structure

```
wynn-concierge/
├── src/
│   ├── data_generator.py    # Creates synthetic luxury data
│   ├── vector_store.py       # RAG with FAISS
│   ├── agent_logic.py        # GPT-4 concierge persona
│   └── app.py                # Streamlit UI
├── data/
│   ├── resort_data.json      # 25 luxury venues
│   └── guests.csv            # 5 diverse guest profiles
├── test_system.py            # Comprehensive validation
└── .env                      # Your API key (create this!)
```

## 🐛 Troubleshooting

**"OPENAI_API_KEY not found"**
- Make sure `.env` exists and contains `OPENAI_API_KEY=sk-...`

**"Resort data not found"**
- Run: `python src/data_generator.py`

**Import errors**
- Make sure virtual environment is activated: `source venv/bin/activate`
- Re-run: `pip install -r requirements.txt`

## 💡 What Makes This Special?

This isn't just a chatbot. It's a **safety-aware reasoning system**:

1. **RAG**: Searches 25 venues semantically
2. **Filtering**: Enforces dietary restrictions automatically
3. **Persona**: Maintains luxury tone (never robotic)
4. **Logistics**: Manages time slots, travel time, dress codes
5. **VIP Recognition**: Adjusts perks based on loyalty tier

## 📚 Next Steps

- Add real-time availability integration
- Connect to PMS (Property Management System)
- Add voice interface (Whisper)
- Multi-language support
- Mobile app version

## 🤝 Contributing

This is a showcase project. Feel free to fork and adapt for your use case!

## 📧 Questions?

Created by **Indhra Kiranu N A**

---

*"Choice Paralysis is the Enemy of Luxury."* ✨
