# Wynn-Concierge AI Agent
### Executive Summary

**Project:** Hyper-Personalized Guest Itinerary System using Generative AI  
**Architect:** Indhra Kiranu N A  
**Repository:** [github.com/indhra/wynn-concierge](https://github.com/indhra/wynn-concierge)

---

## 1. The "Why": The Business Problem

> *"Choice Paralysis is the Enemy of Luxury."*

### Context
Wynn Al Marjan Island will feature 22 dining venues, a nightclub, a theatre, and extensive gaming facilities. High-net-worth guests often face decision fatigue when navigating these options. Static PDF directories or generic "Top 10" lists fail to capture the nuance of a guest's immediate mood or long-term preferences.

### Key Challenges
- **The Pain Point:** Guests waste time debating "Where should we go?" instead of spending money.
- **The Opportunity:** A "Black Tier" guest expects anticipation, not reaction. They want a curated plan that accounts for their specific taste (e.g., *"Quiet Italian dinner, no seafood, near the casino"*) instantly.
- **The Goal:** Eliminate friction between Intent and Transaction by generating conflict-free, personalized itineraries in seconds.

---

## 2. The "What": The Solution

Wynn-Concierge is a **Multi-Agent GenAI System** designed to act as a 24/7 Digital Butler. Unlike a standard chatbot that simply answers questions, this agent plans logistics.

### Core Capability
Generates a time-sequenced evening itinerary (e.g., *7:00 PM Cocktails → 8:30 PM Dinner → 10:30 PM Show*) based on real-time availability and guest profile data.

### The "Human" Touch: Soft Constraints
The system enforces constraints that traditional code misses:

- **Vibe Matching:** Won't suggest a high-energy nightclub to a guest seeking a "Romantic/Quiet" evening.
- **Safety:** Automatically filters menus based on dietary restrictions (Gluten-Free, Nut Allergies) before suggesting.
- **Status Recognition:** Alters tone and perks based on Guest's Loyalty Tier (Platinum/Black).

---

## 3. The "How": Technical Architecture

This Proof-of-Concept (PoC) demonstrates an **Enterprise-Grade Architecture** aligned with the Wynn Al Marjan Technology Stack (Azure/Databricks).

### Core Components

#### Orchestration
- **Orchestration Brain:** LangChain (Python) manages reasoning loops and tool selection.

#### AI Engine
- **Cognitive Engine:** OpenAI GPT-4 prompted with a specific "Luxury Concierge Persona" to ensure tone consistency (Sophisticated, Anticipatory, Discreet).

#### Knowledge Retrieval (RAG)
- **Vector Store (FAISS):** Stores unstructured data about resort amenities (menus, ambiance descriptions, dress codes).
- **Retrieval:** Uses Semantic Search to find venues matching vague user requests (e.g., *"Somewhere with a view and good jazz"*).

#### Data Logic
- **Mock CRM:** A synthetic dataset representing the "Golden Record" of guest preferences.
- **Guardrails:** Python-based logic layers that prevent hallucinations (e.g., ensuring a restaurant is actually open at the suggested time).

#### Interface
- **User Interface:** A Streamlit dashboard simulating an iPad interface used by Front Desk staff or In-Room Tablets.

---

## 4. The "Where": Deployment Strategy

### Current State
Local Python Environment (Simulating Cloud Execution).

### Target State
- **Compute:** Azure Kubernetes Service (AKS) for low-latency inference.
- **Data Lake:** Azure Databricks (Delta Lake) to unify Guest Telemetry and Reservation Logs.
- **Integration:** API endpoints connecting to the Property Management System (PMS) like Opera or Micros.

---

## 5. The "When": Strategic Roadmap

- **Phase 1 (Completed - Current PoC):** Core logic validation. The Agent successfully reads a profile, checks constraints, and outputs a valid itinerary.
- **Phase 2 (Integration):** Connecting the Agent to live inventory systems to enable "One-Click Booking."
- **Phase 3 (Voice):** Enabling guests to speak to the concierge via room automation systems, powered by OpenAI Whisper.

---

## Conclusion

This project is not just a chatbot; it is a **Revenue Optimization Engine**. By guiding guests to venues that match their preferences, we increase capture rates, improve guest satisfaction scores (NPS), and reinforce the Wynn brand promise of effortless luxury.

The **Wynn-Concierge AI Agent** is poised to transform the guest experience at Wynn Al Marjan Island, setting a new standard for personalized service in the hospitality industry.
