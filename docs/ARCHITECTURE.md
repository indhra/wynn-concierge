# Wynn Concierge AI - Architecture

## System Architecture Diagram

```
                                    ┌─────────────────────────────────────┐
                                    │      HIRING MANAGER / GUEST         │
                                    │         (Web Browser)               │
                                    └──────────────┬──────────────────────┘
                                                   │
                                                   │ HTTPS
                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                            STREAMLIT FRONTEND (app.py)                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐    │
│  │  Guest Selector  │  │  Loyalty Card    │  │   Chat Interface         │    │
│  │  (CSV Loader)    │  │  (Tier Display)  │  │   (Session State)        │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘    │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │  Thinking Process Simulator                                             │  │
│  │  • Checking availability  • Verifying constraints  • Finalizing         │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────┬────────────────────────────────────────────┘
                                    │
                                    │ Guest Profile + Query
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                      AGENT ORCHESTRATOR (agent_logic.py)                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │  WynnConciergeAgent                                                     │  │
│  │  • Intent Extraction (query parsing)                                    │  │
│  │  • Guest Context Formation (name, tier, restrictions, preferences)      │  │
│  │  • Multi-step Reasoning (search → filter → rank → generate)             │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────┐         │
│  │  System Prompt Engineering                                       │         │
│  │  • Chief Concierge Persona                                       │         │
│  │  • Safety Rules (dietary cross-reference)                        │         │
│  │  • VIP Recognition Logic                                         │         │
│  │  • Tone Guidelines (sophisticated, anticipatory, discreet)       │         │
│  └──────────────────────────────────────────────────────────────────┘         │
└─────────────┬──────────────────────────────────┬───────────────────────────────┘
              │                                  │
              │ Semantic Search                  │ LLM Generation
              ▼                                  ▼
┌─────────────────────────────────┐   ┌──────────────────────────────────┐
│   VECTOR STORE (vector_store.py)│   │   OPENAI GPT-4 API               │
│  ┌──────────────────────────────┤   │  ┌───────────────────────────────┤
│  │ ResortKnowledgeBase          │   │  │ ChatOpenAI                    │
│  │                              │   │  │ • Model: gpt-4                │
│  │ ┌──────────────────────────┐ │   │  │ • Temperature: 0.7            │
│  │ │  FAISS Vector Index      │ │   │  │ • Max Tokens: 1500            │
│  │ │  • 25 Venue Embeddings   │ │   │  └───────────────────────────────┘
│  │ │  • text-embedding-3-small│ │   │                                  │
│  │ │  • Cached to .pkl        │ │   │  [Rate Limiting & Cost Control]  │
│  │ └──────────────────────────┘ │   │  • Monthly budget: $20           │
│  │                              │   │  • Usage alerts enabled          │
│  │ ┌──────────────────────────┐ │   └──────────────────────────────────┘
│  │ │ Safety Filter Engine     │ │              ▲
│  │ │ • Allergy Detection      │ │              │
│  │ │ • Dietary Restrictions   │ │              │ API Key
│  │ │ • Halal Verification     │ │              │
│  │ │ • Returns: is_safe flag  │ │              │
│  │ └──────────────────────────┘ │   ┌──────────┴───────────────────────┐
│  │                              │   │   ENVIRONMENT / SECRETS          │
│  │ [Similarity Search]          │   │  • .env (local)                  │
│  │ • RecursiveCharacterSplitter │   │  • Streamlit secrets (cloud)     │
│  │ • Semantic matching          │   │  • OPENAI_API_KEY                │
│  └──────────────────────────────┘   │  • OPENAI_MODEL                  │
└─────────────┬────────────────────────└──────────────────────────────────┘
              │
              │ Load Data
              ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                        │
│  ┌──────────────────────────────────┐  ┌────────────────────────────────────┐ │
│  │  resort_data.json (25 venues)    │  │  guests.csv (5 profiles)           │ │
│  │  ┌────────────────────────────┐  │  │  ┌──────────────────────────────┐  │ │
│  │  │ • id, name, category       │  │  │  │ • name, loyalty_tier         │  │ │
│  │  │ • description (rich text)  │  │  │  │ • dietary_restrictions       │  │ │
│  │  │ • tags (vibes)             │  │  │  │ • preferences                │  │ │
│  │  │ • dietary_options          │  │  │  │ • visit_purpose              │  │ │
│  │  │ • allergen_warnings        │  │  │  └──────────────────────────────┘  │ │
│  │  │ • constraints (booleans)   │  │  │                                    │ │
│  │  │ • opening_hours            │  │  │  [Generated by data_generator.py]  │ │
│  │  │ • vip_perks                │  │  │                                    │ │
│  │  └────────────────────────────┘  │  └────────────────────────────────────┘ │
│  │                                  │                                          │
│  │  [Generated by data_generator.py]│                                          │
│  └──────────────────────────────────┘                                          │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
User Query: "I want a steak dinner and a wild night out"
Guest: Sarah Chen (Vegetarian, Black Tier)

┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 1: INPUT PROCESSING                                                 │
│                                                                          │
│  User Query + Guest Profile                                              │
│       │                                                                  │
│       ├─> Intent Extraction                                              │
│       │   • Categories: ["Fine Dining", "Nightlife"]                     │
│       │   • Vibes: ["steak" → "sophisticated", "wild" → "energetic"]    │
│       │                                                                  │
│       └─> Guest Context                                                  │
│           • Name: Sarah Chen                                             │
│           • Tier: Black                                                  │
│           • Restrictions: Vegetarian, Gluten-Free                        │
│           • Preferences: Romantic, wine enthusiast                       │
└──────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 2: VECTOR SEARCH (RAG)                                              │
│                                                                          │
│  Query Embedding: "steak dinner sophisticated fine dining"               │
│       │                                                                  │
│       ├─> FAISS Similarity Search                                        │
│       │   • Top 6 Fine Dining venues                                     │
│       │   • Top 6 Nightlife venues                                       │
│       │                                                                  │
│       └─> Results:                                                       │
│           1. The Obsidian Steakhouse (87% match)                         │
│           2. Verde Garden (81% match)                                    │
│           3. Tartufo Nero (79% match)                                    │
│           4. XS Skyline (nightlife - 92% match)                          │
│           5. The Jazz Lounge (nightlife - 76% match)                     │
└──────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 3: SAFETY FILTERING                                                 │
│                                                                          │
│  For each venue, check: dietary_restrictions = "Vegetarian"             │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ The Obsidian Steakhouse                                         │    │
│  │ • dietary_options: ["Gluten-Free Options"]                      │    │
│  │ • allergen_warnings: ["Contains Dairy", "Contains Shellfish"]   │    │
│  │ • Category: Steakhouse                                          │    │
│  │ ❌ UNSAFE: Limited vegetarian options (meat-focused)            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Verde Garden                                                    │    │
│  │ • dietary_options: ["Vegetarian", "Vegan", "Gluten-Free"]       │    │
│  │ • Description: "Plant-forward fine dining"                      │    │
│  │ ✅ SAFE: Specifically vegetarian-focused                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ XS Skyline (Nightclub)                                          │    │
│  │ • No dietary restrictions for nightlife                         │    │
│  │ ✅ SAFE: No food allergen concerns                              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 4: CONTEXT PREPARATION FOR LLM                                      │
│                                                                          │
│  System Prompt Template filled with:                                     │
│  • guest_name: "Sarah Chen"                                              │
│  • loyalty_tier: "Black"                                                 │
│  • dietary_restrictions: "Vegetarian, Gluten-Free"                       │
│  • preferences: "Romantic settings, wine enthusiast"                     │
│  • venues_context: (formatted list with safety flags)                    │
│      - Verde Garden ✅ SAFE                                              │
│      - The Obsidian Steakhouse ⚠️ UNSAFE - Limited vegetarian options   │
│      - XS Skyline ✅ SAFE                                                │
│  • user_query: "I want a steak dinner and a wild night out"             │
└──────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 5: GPT-4 GENERATION                                                 │
│                                                                          │
│  Input: System prompt + Human message                                    │
│  Temperature: 0.7 (creative but consistent)                              │
│  Max tokens: 1500                                                        │
│                                                                          │
│  LLM applies:                                                            │
│  • Persona rules (sophisticated, anticipatory)                           │
│  • Safety rules (don't suggest unsafe venues)                            │
│  • Graceful redirect ("While X is exceptional, I suggest Y...")          │
│  • VIP recognition ("As a Black Tier member, I've secured...")           │
│  • Time management (90 min dinner + 15 min travel)                       │
└──────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 6: OUTPUT                                                           │
│                                                                          │
│  Good evening, Ms. Chen. I understand you're seeking an exceptional      │
│  evening experience. While The Obsidian Steakhouse is one of our         │
│  signature venues, given your vegetarian preferences, I have instead     │
│  taken the liberty of securing the best table at Verde Garden.           │
│                                                                          │
│  Timeline for your evening:                                              │
│                                                                          │
│  7:30 PM - Verde Garden (Fine Dining)                                    │
│  This plant-forward gem features organic vegetables from our rooftop     │
│  garden and an exceptional wine program. As a Black Tier member, I've    │
│  arranged the private garden table and a complimentary meet-the-chef     │
│  experience. [Duration: ~105 minutes]                                    │
│                                                                          │
│  10:00 PM - XS Skyline (Ultra-Luxury Nightclub)                          │
│  Following dinner, I've coordinated a seamless 15-minute transfer to     │
│  our crown jewel nightclub. Your table minimum has been waived, and      │
│  your dedicated host will ensure a spectacular evening. Celebrity DJ     │
│  tonight with stunning city views. [Open until 4:00 AM]                  │
│                                                                          │
│  Dress code: Smart elegant for both venues. May I arrange anything       │
│  else for your evening?                                                  │
└──────────────────────────────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. **RAG (Retrieval Augmented Generation)**
- Semantic search finds relevant venues
- Embeddings capture nuanced meaning ("steak dinner" → fine dining vibes)
- Grounding prevents hallucination (only real venues suggested)

### 2. **Safety-Critical AI**
- Filter before generation (unsafe venues never reach LLM)
- Hierarchical constraints (allergies > preferences)
- Transparent reasoning (safety_note explains exclusions)

### 3. **Persona Engineering**
- System prompt defines character ("Chief Concierge")
- Few-shot examples in prompt (tone guidelines)
- Context injection (guest profile in every call)

### 4. **Stateful UI**
- Session state preserves chat history
- Guest profile cached across interactions
- Vector store cached (rebuild only when forced)

## Scalability Considerations

### Current (PoC):
- **Users:** 1-10 concurrent (Streamlit Cloud free tier)
- **Latency:** 3-8 seconds per query
- **Cost:** ~$0.20 per session
- **Data:** 25 static venues

### Production Scale:
- **Users:** 1,000+ concurrent → Azure Kubernetes Service
- **Latency:** <2 seconds → Pre-compute embeddings, use Redis cache
- **Cost:** ~$0.05 per session → Cheaper embedding model, cache LLM calls
- **Data:** 500+ venues across multiple properties → Delta Lake integration

## Security & Privacy

- ✅ API keys in environment variables (never committed)
- ✅ Rate limiting (10 requests/hour per session in demo)
- ✅ No PII stored (guest data is synthetic)
- ✅ HTTPS only (Streamlit Cloud enforced)
- ✅ Usage monitoring (OpenAI dashboard alerts)

## Technology Choices & Rationale

| Choice | Alternative | Why This? |
|--------|-------------|-----------|
| **GPT-4** | GPT-3.5 Turbo | Better at persona consistency, nuanced reasoning |
| **FAISS** | Pinecone, Weaviate | Faster for small datasets, no external dependency |
| **Streamlit** | React, Flask | Rapid prototyping, data science friendly, free hosting |
| **LangChain** | Custom orchestration | Standard framework, easier to extend |
| **text-embedding-3-small** | ada-002 | Better quality, lower cost |

---

**This architecture demonstrates:**
- Production thinking (scalability, security, cost)
- AI best practices (RAG, safety filtering)
- Clean separation of concerns (UI, logic, data)
- Deployment readiness (cloud-native design)
