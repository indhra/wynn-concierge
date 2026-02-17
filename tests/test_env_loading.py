#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv

# Test 1: Load .env
env_path = Path("/Users/indhra/Machine_learning/wynn-concierge/.env")
print(f"Step 1: .env file exists: {env_path.exists()}")

load_dotenv(dotenv_path=env_path)

# Test 2: Get API key
api_key = os.getenv('OPENAI_API_KEY')
print(f"Step 2: API key loaded: {api_key is not None}")
print(f"Step 3: API key length: {len(api_key) if api_key else 0}")
print(f"Step 4: API key preview: {api_key[:20]}...{api_key[-20:] if api_key and len(api_key) > 40 else ''}")
print(f"Step 5: Starts with sk-proj: {api_key.startswith('sk-proj-') if api_key else False}")
