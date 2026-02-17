#!/usr/bin/env python3
"""
Quick Verification Script for Streamlit Deployment
Run this before deploying to ensure everything works
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def check_deployment_readiness():
    """Quick checks for deployment readiness"""
    
    print("\n" + "🔍" * 30)
    print("QUICK DEPLOYMENT VERIFICATION")
    print("🔍" * 30 + "\n")
    
    issues = []
    
    # Check 1: Python version
    print("1️⃣  Checking Python version...")
    if sys.version_info >= (3, 9):
        print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    else:
        print(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor} (need 3.9+)")
        issues.append("Python version too old")
    
    # Check 2: Required files
    print("\n2️⃣  Checking required files...")
    required_files = [
        'streamlit_app.py',
        'requirements.txt',
        'runtime.txt',
        'data/resort_data.json',
        'data/guests.csv',
        'src/agent_logic.py',
        'src/vector_store.py',
        'src/app.py'
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} MISSING")
            issues.append(f"Missing {file}")
    
    # Check 3: Environment
    print("\n3️⃣  Checking environment...")
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"   ✅ OPENAI_API_KEY set ({len(api_key)} chars)")
    else:
        print("   ⚠️  OPENAI_API_KEY not set (required for deployment)")
        issues.append("No API key in environment")
    
    # Check 4: Import test
    print("\n4️⃣  Testing imports...")
    try:
        import streamlit
        print(f"   ✅ streamlit {streamlit.__version__}")
    except ImportError:
        print("   ❌ streamlit not installed")
        issues.append("streamlit not installed")
    
    try:
        from langchain_openai import ChatOpenAI
        print("   ✅ langchain_openai")
    except ImportError:
        print("   ❌ langchain_openai not installed")
        issues.append("langchain_openai not installed")
    
    try:
        import faiss
        print("   ✅ faiss")
    except ImportError:
        print("   ❌ faiss not installed")
        issues.append("faiss not installed")
    
    # Check 5: JSON mode verification
    print("\n5️⃣  Verifying JSON mode fix...")
    try:
        from agent_logic import WynnConciergeAgent
        import inspect
        
        source = inspect.getsource(WynnConciergeAgent.__init__)
        if 'response_format' in source and 'json_object' in source:
            print("   ✅ JSON mode enabled in agent")
        else:
            print("   ❌ JSON mode not found")
            issues.append("JSON mode not configured")
    except Exception as e:
        print(f"   ❌ Could not verify: {e}")
        issues.append("Could not verify JSON mode")
    
    # Summary
    print("\n" + "=" * 70)
    if not issues:
        print("✅ ALL CHECKS PASSED - READY TO DEPLOY!")
        print("\nTo deploy to Streamlit Cloud:")
        print("  1. git add . && git commit -m 'Ready for deployment'")
        print("  2. git push origin main")
        print("  3. Deploy on share.streamlit.io")
        print("  4. Add OPENAI_API_KEY to Streamlit secrets")
        return True
    else:
        print("⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nFix these issues before deploying")
        return False


if __name__ == "__main__":
    success = check_deployment_readiness()
    sys.exit(0 if success else 1)
