"""
Streamlit Cloud Entry Point
This file launches the main app from the src directory.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main app
from app import main

# Run the main application
if __name__ == "__main__":
    main()
