# 🏝️ Wynn Concierge AI Agent

A hyper-personalized luxury concierge system powered by GPT-4 and LangChain RAG, designed for Wynn Al Marjan Island.

## 🎯 Overview

This AI agent acts as a 24/7 Digital Butler, creating personalized evening itineraries that account for:
- Guest dietary restrictions & allergies
- Loyalty tier status (Black/Platinum)
- Vibe preferences (Romantic, Energetic, etc.)
- Real-time venue availability

## 🏗️ Architecture

- **Orchestration**: LangChain
- **AI Engine**: OpenAI GPT-4
- **Knowledge Retrieval**: FAISS Vector Store + RAG
- **Interface**: Streamlit Dashboard
- **Data**: Synthetic luxury resort venues + guest profiles

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API Key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/indhra/wynn-concierge.git
cd wynn-concierge
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

5. **Generate initial data**
```bash
python src/data_generator.py
```

6. **Run the application**
```bash
streamlit run src/app.py
```

## 📁 Project Structure

```
wynn-concierge/
├── src/
│   ├── data_generator.py    # Generates synthetic resort & guest data
│   ├── vector_store.py       # FAISS vector store + RAG logic
│   ├── agent_logic.py        # GPT-4 agent with concierge persona
│   └── app.py                # Streamlit UI
├── data/
│   ├── resort_data.json      # 25 luxury venues
│   └── guests.csv            # Guest profiles with preferences
├── logs/                     # Application logs
├── .env.example              # Environment template
└── requirements.txt          # Python dependencies
```

## 🧪 Testing the System

**Test Scenario**: Vegetarian guest requesting steak dinner

1. Select a guest with "Vegetarian" dietary restriction
2. Request: *"I want a steak dinner and a wild night out."*
3. **Expected Result**: The AI should gracefully suggest a plant-based alternative while maintaining luxury tone

## 🎨 Key Features

✅ **Safety-First Logic**: Filters venues by dietary restrictions  
✅ **Vibe Matching**: Suggests venues matching guest mood  
✅ **Time Management**: Prevents double-booking with realistic travel time  
✅ **VIP Recognition**: Adjusts tone for Black Tier guests  
✅ **Luxury Persona**: Sophisticated, anticipatory communication style  

## 🔮 Roadmap

- **Phase 1** (Current): Core logic validation with synthetic data
- **Phase 2**: Integration with live PMS systems (Opera/Micros)
- **Phase 3**: Voice interface with OpenAI Whisper

## 📝 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

**Indhra Kiranu N A**  
[github.com/indhra](https://github.com/indhra)

---

*"Choice Paralysis is the Enemy of Luxury."*
