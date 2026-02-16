# 🏝️ Wynn Concierge AI Agent

A hyper-personalized luxury concierge system powered by GPT-4 and LangChain RAG, designed for Wynn Al Marjan Island.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🚀 **For Hiring Managers**

**👉 [5-Minute Evaluation Guide](docs/HIRING_MANAGER.md)** - Quick demo scenarios to test the AI

**📺 LIVE DEMO:** **[https://wynn-concierge.streamlit.app/](https://wynn-concierge.streamlit.app/)** ✨

**💡 See it in action:**
1. Select **Sarah Chen** (Vegetarian guest)
2. Ask: *"I want a steak dinner and a wild night out"*
3. Watch the AI gracefully redirect to vegetarian fine dining + nightlife

**Why this matters:** Demonstrates safety-critical AI that prioritizes guest protection over literal request fulfillment.

---

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
� Screenshots

> **Note:** After deploying the app, capture screenshots following [SCREENSHOTS.md](docs/SCREENSHOTS.md)

### Guest Selection with VIP Card
*Black Tier card with gold gradient, dietary restrictions visible*

### The "Intelligence Test" - Vegetarian Redirect
*AI gracefully sug[LICENSE](LICENSE) file for details

## 📚 Documentation

- **[HIRING_MANAGER.md](docs/HIRING_MANAGER.md)** - 5-minute evaluation guide for recruiters
- **[QUICKSTART.md](docs/QUICKSTART.md)** - Quick start guide with troubleshooting
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and technical deep-dive
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deploy to Streamlit Cloud (free)
- **[SCREENSHOTS.md](docs/SCREENSHOTS.md)** - Visual assets creation guide

## 🎓 Skills Demonstrated

This project showcases:
- ✅ **AI/ML Engineering** - RAG, LangChain, GPT-4, FAISS
- ✅ **System Design** - Scalable architecture, safety-critical logic
- ✅ **Full-Stack Development** - Python backend + Streamlit UI
- ✅ **Product Thinking** - Real business value, exceptional UX
- ✅ **Code Quality** - Testing, documentation, best practices

## 👨‍💻 Author

**Indhra Kiranu N A**  
[github.com/indhra](https://github.com/indhra)

---

## ⭐ Star This Repo

If this project helped you or you find it impressive, please give it a star! It helps others discover it.** - Instructions for capturing visual assets

## 🏗️ Architecture & Design

**[View Complete Architecture](docs/ARCHITECTURE.md)** - System design, data flow, and technical decisions

**Key Highlights:**
- **RAG Pattern**: FAISS vector search with semantic matching
- **Safety-Critical Design**: Multi-layer filtering (allergies → dietary → preferences)
- **Production-Ready**: Error handling, logging, rate limiting, deployment scripts

## �
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
