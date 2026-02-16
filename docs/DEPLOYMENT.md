# Deploying to Streamlit Cloud (Free)

## ✅ **DEPLOYMENT SUCCESSFUL!**

**🎉 Live URL:** **[https://wynn-concierge.streamlit.app/](https://wynn-concierge.streamlit.app/)** ✨

---

This guide shows how to deploy the Wynn Concierge AI to Streamlit Cloud for instant hiring manager access.

## Prerequisites

- GitHub account
- OpenAI API key
- Project pushed to GitHub

## Step 1: Prepare the Repository

1. **Ensure all files are committed:**
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

2. **Verify your .gitignore includes:**
```
.env
venv/
*.pkl
*.faiss
```

## Step 2: Create Streamlit Cloud Account

1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"

## Step 3: Configure the App

**App settings:**
- **Repository:** `indhra/wynn-concierge`
- **Branch:** `main`
- **Main file path:** `streamlit_app.py` (entry point that loads from src/)

## Step 4: Add Secrets (API Key)

In the Streamlit Cloud dashboard:

1. Click "Advanced settings"
2. Go to "Secrets" section
3. Add your secrets in TOML format:

```toml
# .streamlit/secrets.toml format
OPENAI_API_KEY = "sk-your-api-key-here"
OPENAI_MODEL = "gpt-5-nano"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
```

## Step 5: Update Code to Use Streamlit Secrets

**Modify `src/vector_store.py`:**

```python
# Add at top of file after imports
import streamlit as st

# In __init__ method, change:
def __init__(self, openai_api_key: str = None, force_rebuild: bool = False):
    if openai_api_key is None:
        # Try Streamlit secrets first, then env
        try:
            openai_api_key = st.secrets["OPENAI_API_KEY"]
        except:
            openai_api_key = os.getenv("OPENAI_API_KEY")
```

**Modify `src/agent_logic.py`:**

```python
# Similar change in __init__
def __init__(self, knowledge_base: ResortKnowledgeBase, openai_api_key: str = None, model: str = "gpt-5-nano"):
    if openai_api_key is None:
        try:
            openai_api_key = st.secrets["OPENAI_API_KEY"]
        except:
            openai_api_key = os.getenv("OPENAI_API_KEY")
```

**Modify `src/app.py`:**

```python
@st.cache_resource
def initialize_system():
    """Initialize the knowledge base and agent (cached)"""
    # Try Streamlit secrets first
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        st.error("⚠️ OPENAI_API_KEY not configured. Please add it to Streamlit secrets.")
        st.stop()
```

## Step 6: Deploy!

1. Click "Deploy"
2. Wait 2-3 minutes for build
3. Your app will be live at: `https://wynn-concierge.streamlit.app`

## Step 7: Protect Your API Key (Usage Limits)

To prevent abuse when sharing with hiring managers:

### Option A: OpenAI Usage Limits
1. Go to [platform.openai.com/account/billing/limits](https://platform.openai.com/account/billing/limits)
2. Set monthly budget: **$20** (enough for ~200 demo sessions)
3. Enable email alerts at $10, $15, $20

### Option B: Create Separate API Key
1. Create a new OpenAI API key specifically for demo
2. Name it "Demo - Wynn Concierge"
3. Set usage limits in OpenAI dashboard
4. Use this key in Streamlit secrets
5. Delete key after hiring process

### Option C: Add Rate Limiting to App

**NOTE:** Rate limiting is now built-in! The app includes 5 requests/hour per user by default.

To customize the rate limit, modify [`app.py:319`](../src/app.py#L319):

Add to `src/app.py`:

```python
# Add after imports
import time

# Session-based rate limiting (already implemented)
# See src/app.py for full implementation
is_allowed, remaining, reset_time = check_rate_limit(guest_name, max_calls=5, time_window_hours=1)
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0
    st.session_state.last_reset = time.time()

# Reset counter every hour
if time.time() - st.session_state.last_reset > 3600:
    st.session_state.request_count = 0
    st.session_state.last_reset = time.time()

# Limit to 10 requests per session per hour
if st.session_state.request_count >= 10:
    st.warning("⏰ Demo limit reached. Please wait 1 hour or contact me for extended access.")
    st.stop()

# In chat input handler, add:
st.session_state.request_count += 1
```

## Step 8: Update README with Live Demo Link

Add badge to README.md:

```markdown
## 🚀 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://wynn-concierge.streamlit.app)

**Try it now:** [wynn-concierge.streamlit.app](https://wynn-concierge.streamlit.app)

No setup required - just click and explore!
```

## Troubleshooting

### Build Fails
- Check `requirements.txt` has all dependencies
- Ensure Python version compatibility (add `runtime.txt` with `python-3.10`)

### App Crashes on Start
- Verify secrets are set correctly
- Check if data files are generated (may need to generate on first run)

### Slow Performance
- FAISS index builds on first run (cached after)
- Consider pre-building index and committing `.pkl` file (remove from .gitignore)

## Alternative: Deploy with Pre-built Index

To speed up cold starts:

1. **Build index locally:**
```bash
python3 -c "
from src.vector_store import ResortKnowledgeBase
import os
kb = ResortKnowledgeBase(os.getenv('OPENAI_API_KEY'), force_rebuild=True)
print('Index built!')
"
```

2. **Commit the index file:**
```bash
git add data/faiss_index.pkl
git commit -m "Add pre-built FAISS index for faster deployment"
git push
```

3. **Modify .gitignore:**
Remove `*.pkl` from .gitignore (only for deployment repo)

## Cost Estimation

**Streamlit Cloud:** Free (1 app)  
**OpenAI API Costs per demo session:**
- Embeddings (one-time index build): ~$0.01
- GPT-4 responses (3-5 queries): ~$0.05-0.15
- **Total per hiring manager:** ~$0.20

**Monthly cost for 50 demos:** ~$10

## Monitoring Usage

Check Streamlit Cloud analytics:
- View count
- Session duration
- Error rates

Check OpenAI dashboard:
- Token usage
- Cost tracking
- Request patterns

---

## Final Checklist

- [ ] Code updated to use Streamlit secrets
- [ ] Secrets added to Streamlit Cloud
- [ ] App deployed successfully
- [ ] Tested live deployment works
- [ ] Usage limits configured on OpenAI
- [ ] README updated with live demo link
- [ ] HIRING_MANAGER.md references live URL

**Your app is now live and hiring-manager ready! 🎉**
