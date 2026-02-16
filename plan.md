STEP 1: The "Digital Reality" (Data Generation)
Goal: Create data that forces the AI to make hard choices (e.g., Allergy vs. Restaurant).

Prompt for Copilot (File: data_generator.py):

"Write a Python script to generate a JSON file called resort_data.json.

I need 25 items across categories: 'Fine Dining', 'Casual Dining', 'Nightlife', 'Spa', 'Shows'.

CRITICAL HUMAN FACTORS - Each item must have:

id: Unique ID.

name: Creative luxury name (e.g., 'The Obsidian Steakhouse').

tags: List of vibes (e.g., 'Romantic', 'Loud', 'Live Music', 'Vegan-Friendly').

constraints: Boolean flags (e.g., requires_reservation, adults_only, dress_code_strict).

opening_hours: Specific time strings (e.g., '18:00-23:00').

Also create a guests.csv with 5 profiles including columns for name, loyalty_tier (Black/Platinum), and dietary_restrictions (Gluten-Free, Nut Allergy) to test safety logic."

STEP 2: The "Brain" (Vector Search & RAG)
Goal: The AI must "read" the brochure before it speaks.

Prompt for Copilot (File: vector_store.py):

"Write a Python class ResortKnowledgeBase using LangChain.

Load the resort_data.json.

Use RecursiveCharacterTextSplitter to chunk the descriptions.

Create a FAISS vector store using OpenAIEmbeddings.

HUMAN LOGIC: Add a method search_amenities(query, guest_profile) that not only searches for the query but filters out options that violate the guest's dietary restrictions (e.g., if guest has 'Nut Allergy', filter out 'Peanut Lounge')."

STEP 3: The "Conductor" (The System Prompt)
Goal: This is where the Vibe lives. It stops the AI from sounding like a robot.

Prompt for Copilot (File: agent_logic.py):

"Create a LangChain ChatOpenAI instance (GPT-4) with a custom SystemMessagePromptTemplate.

Use this EXACT System Prompt for the Persona:

'You are the Chief Concierge at Wynn Al Marjan Island. You are sophisticated, anticipatory, and discreet.

YOUR MISSION:
Create a seamless evening itinerary (6:00 PM - 2:00 AM) for the guest based on their request.

RULES OF ENGAGEMENT (The Human Touch):

Logistics First: Never double-book time slots. Allow 90 minutes for dinner and 15 minutes for travel between venues.

Safety Check: CROSS-REFERENCE the Guest Profile. Never suggest a venue that conflicts with their dietary restrictions or allergies.

Tier Recognition: If the guest is 'Black Tier' (VIP), explicitly mention that you have 'secured the best table' or 'waived the cover charge.'

Tone: Warm, professional, but concise. Do not sound robotic. Use phrases like "I have taken the liberty of..." or "Given your preference for..."

Current Guest Context:
Name: {guest_name}
Tier: {loyalty_tier}
Restrictions: {dietary_restrictions}

Request: {user_query}'"

STEP 4: The "Face" (Streamlit UI)
Goal: A dashboard that looks like it belongs on an iPad at the check-in desk.

Prompt for Copilot (File: app.py):

"Build a Streamlit app.

Layout:

Sidebar: A 'Guest Selector' dropdown (loads from guests.csv). Display their 'Loyalty Card' with a gold/black gradient CSS background.

Main Chat: A simple chat interface.

The 'Thinking' State: When the user asks for a plan, show a status spinner that says: 'Checking Reservation Availability...' -> 'Verifying Dietary Constraints...' -> 'Finalizing Itinerary'. (This adds realism).

Output: Display the final itinerary as a structured Timeline (using st.markdown or a timeline component), not just a block of text."

How to Verify You Built It "Right" (The Test)
Once you run the code, test this scenario:

Guest: Select a profile with "Vegetarian".

Request: "I want a steak dinner and a wild night out."

Result: The AI should say: "Sir, while 'The Obsidian Steakhouse' is popular, their vegetarian selection is limited. I have instead taken the liberty of reserving a table at 'Verde Garden' which offers an exceptional plant-based menu, followed by a table at XS Nightclub."

(If it does that, you have built a Senior Engineer level Agent.)