# 🎯 For Hiring Managers: Wynn Concierge AI

**5-Minute Evaluation Guide**

---

## What You're Looking At

A **production-ready luxury concierge AI** that creates personalized itineraries while enforcing safety constraints (dietary restrictions, allergies). This demonstrates:

✅ **AI/ML Engineering** - RAG with FAISS, LangChain, GPT-4  
✅ **System Design** - Scalable architecture, safety-first logic  
✅ **Full-Stack Development** - Python backend + Streamlit UI  
✅ **Product Thinking** - Real business value, exceptional UX  
✅ **Code Quality** - Testing, documentation, best practices  

---

## 🚀 Try It Live (No Setup Needed)

**✨ LIVE DEMO:** **[https://wynn-concierge.streamlit.app/](https://wynn-concierge.streamlit.app/)** 🎉

**GitHub:** [github.com/indhra/wynn-concierge](https://github.com/indhra/wynn-concierge)

---

## ⚡ The 5-Minute Demo

### **Test 1: The "Intelligence Test"** (2 min)
This proves the AI doesn't just respond—it **protects**.

1. Click **"Sarah Chen"** in the sidebar (she's Vegetarian)
2. Type: **"I want a steak dinner and a wild night out"**
3. **Watch the AI:**
   - ❌ Reject The Obsidian Steakhouse (unsafe)
   - ✅ Redirect to Verde Garden (vegetarian fine dining)
   - ✅ Add nightlife without dietary conflicts
   - ✅ Maintain luxury tone (never says "I can't do that")

**Why this matters:** Shows constraint-aware reasoning, not just keyword matching.

---

### **Test 2: The "VIP Recognition Test"** (1 min)
1. Select **"Marcus Al-Rashid"** (Black Tier VIP)
2. Ask: **"Recommend a fine dining restaurant"**
3. **Notice:**
   - AI mentions "I have secured the best table"
   - References VIP perks (waived cover, chef's table)
   - Different tone than Platinum tier guests

**Why this matters:** Context-aware personalization at scale.

---

### **Test 3: The "Safety Filtering Test"** (1 min)
1. Select **"Marcus Al-Rashid"** (Nut Allergy)
2. Ask: **"Best place for dinner?"**
3. **Verify:** No venues with nut warnings appear

**Why this matters:** Safety-critical AI design (like medical/legal AI).

---

### **Test 4: Quick Scan** (1 min)
- Click **"Fine Dining"** in sidebar → Instant recommendation
- Check **Loyalty Card** styling (Black = gold, Platinum = silver)
- Observe **"Thinking" spinner** with realistic stages

---

## 🏗️ Technical Architecture

```
┌─────────────────────────────────────────────────────┐
│                  STREAMLIT UI                       │
│  (Luxury Interface + Guest Profiles + Chat)         │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│              AGENT ORCHESTRATOR                     │
│  (LangChain + GPT-4 + Custom Persona Prompt)        │
└─────────────────┬───────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
┌─────────────────┐  ┌─────────────────────────┐
│  VECTOR STORE   │  │  SAFETY FILTER          │
│  (FAISS + RAG)  │  │  (Dietary Logic)        │
│  25 Venues      │  │  Allergy Detection      │
└─────────────────┘  └─────────────────────────┘
        │                   │
        └─────────┬─────────┘
                  ▼
        ┌────────────────────┐
        │   DATA LAYER       │
        │ resort_data.json   │
        │   guests.csv       │
        └────────────────────┘
```

**Key Design Decisions:**
- **RAG over Fine-Tuning**: Allows real-time venue updates without retraining
- **FAISS over Cloud Vector DB**: Fast, cost-effective for PoC
- **Streamlit over React**: Rapid prototyping, data science friendly
- **GPT-4 over GPT-3.5**: Better at nuanced persona maintenance

---

## 📊 Code Quality Metrics

| Metric | Value |
|--------|-------|
| **Test Coverage** | End-to-end validation suite |
| **Documentation** | README + QUICKSTART + Inline docs |
| **Code Structure** | Modular (4 files, single responsibility) |
| **Error Handling** | Try/catch with logging |
| **Security** | .env for secrets, .gitignore configured |
| **Dependencies** | Pinned versions, requirements.txt |

---

## 🎯 Skills Demonstrated

### **1. AI/ML Engineering**
- ✅ Retrieval Augmented Generation (RAG) implementation
- ✅ Vector embeddings with FAISS
- ✅ LangChain agent orchestration
- ✅ Prompt engineering (persona-based system prompts)
- ✅ Multi-step reasoning (intent extraction → retrieval → filtering → generation)

### **2. System Design**
- ✅ Scalable architecture (vector DB, cached embeddings)
- ✅ Safety-critical constraints (allergy filtering)
- ✅ State management (session tracking)
- ✅ Error handling and logging
- ✅ Production-ready structure (src/, data/, tests/)

### **3. Full-Stack Development**
- ✅ Python backend (OOP, type hints)
- ✅ Frontend UI (Streamlit + Custom CSS)
- ✅ Data processing (Pandas, JSON)
- ✅ API integration (OpenAI)
- ✅ Environment configuration (.env)

### **4. Product Thinking**
- ✅ Real business problem (choice paralysis in luxury)
- ✅ User-centered design (VIP tiers, safety-first)
- ✅ Exceptional UX (thinking states, luxury styling)
- ✅ Test scenarios anticipate edge cases

### **5. Professional Practices**
- ✅ Git best practices (.gitignore, clear commits)
- ✅ Documentation (README, QUICKSTART, inline)
- ✅ Testing (validation suite)
- ✅ Deployment-ready (setup scripts)
- ✅ Code readability (PEP 8, docstrings)

---

## 💼 Business Value

**Problem Solved:**
High-net-worth guests waste time debating where to go, reducing transaction velocity. Generic recommendations ignore critical constraints (allergies, preferences).

**Solution Impact:**
- ⬆️ **Revenue**: Faster booking decisions → Higher capture rate
- ⬆️ **NPS**: Personalized, safe recommendations → Better satisfaction
- ⬇️ **Cost**: 24/7 AI availability without additional concierge staff
- 🎯 **Differentiation**: VIP-aware service impossible at scale manually

**ROI Example:**
If 10% of 1,000 daily guests use this to book one additional experience ($100 avg):
- Daily: $10,000
- Annual: $3.6M revenue impact

---

## 🔍 What to Look For in the Code

### **Impressive Details:**

**1. Safety Filtering** (`vector_store.py`, lines 120-165)
```python
def _check_dietary_safety(self, venue, dietary_restrictions):
    # Not just keyword matching - hierarchical logic:
    # 1. Critical allergies (MUST filter)
    # 2. Dietary preferences (SHOULD redirect)
    # 3. Returns (is_safe, reason) for transparency
```

**2. Persona Prompt** (`agent_logic.py`, lines 22-75)
- Not generic - specific phrases like "I have taken the liberty of..."
- Graceful redirects: "While X is exceptional, given your preferences..."
- VIP tier awareness built into prompt

**3. Rich Data Model** (`data_generator.py`)
- 25 hand-crafted luxury venues (not lorem ipsum)
- Realistic constraints (dress codes, hours, allergies)
- Edge cases built in (vegetarian steakhouse, nut allergies)

**4. UI Polish** (`app.py`, lines 24-100)
- Custom CSS gradients by tier (Black = gold, Platinum = silver)
- Thinking states simulate hotel concierge experience
- Session state management for chat history

---

## 🚀 Extending This (Future Roadmap)

If this were a real product, next steps would be:

**Phase 2: Integration**
- Connect to PMS (Property Management System like Opera)
- Real-time availability checking
- One-click booking with payment

**Phase 3: Intelligence**
- User preference learning (implicit feedback)
- A/B test recommendation strategies
- Sentiment analysis on guest feedback

**Phase 4: Scale**
- Deploy to Azure Kubernetes Service
- Connect to Delta Lake (unified guest profile)
- Multi-property support (Wynn Las Vegas, Encore, etc.)

---

## ⏱️ Build Time

**Estimated development time:** 12-16 hours
- Data generation & modeling: 2 hours
- RAG implementation: 3 hours
- Agent logic & prompting: 3 hours
- UI development: 3 hours
- Testing & documentation: 2 hours
- Polish & deployment prep: 1-2 hours

**This demonstrates:** Ability to ship production-quality features rapidly.

---

## 📧 Questions or Want to Discuss?

I'm happy to walk through:
- Design decisions (why FAISS vs. Pinecone?)
- Trade-offs (why GPT-4 vs. fine-tuned smaller model?)
- Scaling strategies (how would this handle 10K requests/min?)
- Code deep-dive (any file you want to review)

---

## ✅ Quick Verdict Checklist

**Use this to evaluate:**

- [ ] **Does it work?** → Try the vegetarian steak test
- [ ] **Is the code clean?** → Check `agent_logic.py` structure
- [ ] **Is it documented?** → README is comprehensive
- [ ] **Production-ready?** → Has tests, error handling, .env
- [ ] **Business-minded?** → Solves real problem with ROI thinking
- [ ] **Impressive?** → Not a tutorial copy, shows original thinking

---

**Expected evaluation time:** 5-15 minutes  
**Best way to evaluate:** Try the live demo, then scan the code

Thank you for your time reviewing this project! 🙏
