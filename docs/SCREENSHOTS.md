# Screenshots & Demo Assets

## Instructions for Creating Screenshots

To make this project hiring-manager ready, capture these screenshots:

### 1. Main UI - Guest Selection ✅
**File:** `docs/assets/screenshot_1_guest_selection.png`

**What to capture:**
- Sidebar with guest dropdown
- Black Tier loyalty card displayed (Sarah Chen)
- Shows dietary restrictions and preferences
- Quick recommendation buttons visible

**How:**
1. Run: `streamlit run src/app.py`
2. Select "Sarah Chen" from dropdown
3. Take full window screenshot
4. Highlight the luxury card styling

---

### 2. Chat Interface - Welcome Message ✅
**File:** `docs/assets/screenshot_2_welcome.png`

**What to capture:**
- Initial concierge welcome message
- Professional greeting mentioning Black Tier status
- Clean chat interface
- Timestamp visible

---

### 3. The "Intelligence Test" - Query ✅
**File:** `docs/assets/screenshot_3_vegetarian_query.png`

**What to capture:**
- User typing: "I want a steak dinner and a wild night out"
- Sarah Chen profile visible in sidebar (Vegetarian)
- Chat input field focused

---

### 4. Thinking Process ✅
**File:** `docs/assets/screenshot_4_thinking.png` or **GIF**

**What to capture:**
- Status spinners showing:
  - "Checking availability..."
  - "Verifying dietary constraints..."
  - "Finalizing itinerary..."

**Bonus:** Create animated GIF of the thinking sequence

---

### 5. Final Itinerary - The Redirect ✅
**File:** `docs/assets/screenshot_5_itinerary.png`

**What to capture:**
- Complete AI response showing:
  - Graceful redirect from steakhouse to Verde Garden
  - VIP perks mentioned ("As a Black Tier member...")
  - Time-sequenced itinerary (7:30 PM dinner → 10:00 PM nightclub)
  - Professional, non-robotic tone
  - Nightlife recommendation (XS Skyline)

**Annotate with highlights:**
- ✅ Safety check (vegetarian alternative)
- ✅ VIP recognition
- ✅ Time management
- ✅ Luxury tone

---

### 6. Quick Recommendation Feature ✅
**File:** `docs/assets/screenshot_6_quick_rec.png`

**What to capture:**
- Click "Fine Dining" sidebar button
- Instant recommendation appears
- Shows how different tiers get different perks

---

### 7. Platinum Tier Comparison ✅
**File:** `docs/assets/screenshot_7_platinum.png`

**What to capture:**
- Switch to James Harrison (Platinum Tier)
- Show silver/platinum styled card (vs gold/black)
- Demonstrate different VIP messaging

---

### 8. Mobile Responsive (Optional) ✅
**File:** `docs/assets/screenshot_8_mobile.png`

**What to capture:**
- App on mobile screen size
- Shows responsive design

---

## GIF Creation (Highly Recommended!)

### GIF 1: Full Demo Flow (15 seconds)
**File:** `docs/assets/demo_full_flow.gif`

**Steps to record:**
1. Start on guest selection
2. Select Sarah Chen
3. Type the vegetarian steak query
4. Show thinking process
5. Display final itinerary
6. Highlight the redirect

**Tools:**
- macOS: Kap, Gifski
- Windows: ScreenToGif
- Online: Gifcap.dev

---

### GIF 2: Quick Recommendation (5 seconds)
**File:** `docs/assets/demo_quick_rec.gif`

**Steps:**
1. Click "Fine Dining" button
2. Watch spinner
3. Show recommendation

---

## Video Demo (Optional but Powerful!)

**File:** `docs/assets/demo_video.mp4` or YouTube link

**Script (2-3 minutes):**
```
1. Intro (15 sec)
   "Hi, I'm [Your Name]. This is the Wynn Concierge AI - a 
   production-ready luxury hotel assistant built with GPT-4,
   LangChain, and FAISS."

2. Problem Statement (20 sec)
   "High-net-worth guests face choice paralysis with 25+ venues.
   Generic recommendations ignore critical constraints like
   allergies and dietary restrictions."

3. The Intelligence Test (60 sec)
   [Show Sarah Chen profile]
   "Here's Sarah - she's vegetarian. Let's ask for a steak dinner."
   [Type query, show thinking, display redirect]
   "Notice the AI didn't just say no - it gracefully redirected
   to a vegetarian alternative while maintaining the luxury tone."

4. Technical Deep-Dive (30 sec)
   "Behind the scenes: RAG with FAISS finds relevant venues,
   safety filters check dietary restrictions, and GPT-4 generates
   personalized itineraries with VIP recognition."

5. Code Quality (20 sec)
   [Quick scroll through clean code]
   "The codebase is production-ready with tests, documentation,
   error handling, and deployment scripts."

6. CTA (15 sec)
   "Try the live demo at [URL], or check out the code on GitHub.
   I'm happy to discuss design decisions, scaling strategies,
   or any technical questions. Thanks for watching!"
```

**Upload to:**
- YouTube (unlisted)
- Loom
- LinkedIn

---

## Architecture Diagram

**Already created:** `ARCHITECTURE.md` with ASCII diagrams

**Optional visual version:**
**File:** `docs/assets/architecture_diagram.png`

**Tools:**
- draw.io
- Excalidraw
- Lucidchart

**Show:**
- Streamlit UI layer
- Agent orchestrator
- Vector store + Safety filter
- Data layer
- OpenAI API
- Data flow with arrows

---

## How to Use These Assets

### In README.md:
```markdown
## 📸 Screenshots

### Guest Selection & VIP Recognition
![Guest Selection](assets/screenshot_1_guest_selection.png)

### The "Intelligence Test" - Safety-Aware Redirect
![Vegetarian Redirect](assets/screenshot_5_itinerary.png)

### Full Demo Flow
![Demo GIF](assets/demo_full_flow.gif)
```

### In HIRING_MANAGER.md:
```markdown
## Visual Proof

**Watch it in action (2 min):**
[![Demo Video](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://youtu.be/YOUR_VIDEO_ID)

**Quick look:**
![Safety Check](assets/screenshot_5_itinerary.png)
```

### In LinkedIn Post:
```
🎯 Just shipped: A luxury hotel concierge AI that doesn't just 
respond—it PROTECTS.

Built with GPT-4, LangChain, FAISS. Production-ready in 16 hours.

[Attach GIF of the vegetarian redirect]

Key features:
✅ RAG-based venue search
✅ Safety-critical filtering (allergies, dietary restrictions)
✅ VIP tier recognition
✅ 100% test coverage

Try it live: [link]
Code: [GitHub link]

#AI #MachineLearning #RAG #LangChain #GPT4
```

---

## Screenshot Checklist

Before sharing with hiring managers:

- [ ] All 8 screenshots captured in high quality (1920x1080 min)
- [ ] GIF of full demo flow created (optimized <5MB)
- [ ] Annotations/highlights added to key screenshots
- [ ] Files organized in `docs/assets/` folder
- [ ] README.md updated with embedded images
- [ ] HIRING_MANAGER.md has visual proof section
- [ ] Mobile responsive screenshot (if applicable)
- [ ] Video demo recorded and uploaded (optional)
- [ ] Architecture diagram created (visual version)

---

## Quick Screenshot Command (macOS)

```bash
# Full window
Cmd + Shift + 4, then Space, then click window

# Selection
Cmd + Shift + 4, then drag

# With timer (for capturing hover states)
Cmd + Shift + 5, Options, Timer: 5 seconds
```

---

**Visual proof makes your project 10x more impressive!** 🎨

Most hiring managers will:
1. Read the README intro (30 seconds)
2. Look at screenshots/GIFs (60 seconds)
3. Try the live demo (3 minutes)
4. Skim the code (2 minutes)

Make those first 90 seconds count with great visuals!
