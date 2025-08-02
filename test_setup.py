#!/usr/bin/env python3
"""
Quick Setup Test for Enhanced RepoToVideo

This script quickly tests if your setup is working correctly.
Run this before using the main application.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_basic_setup():
    """Test basic setup and dependencies."""
    print("🔍 Testing Enhanced RepoToVideo Setup...")
    print("=" * 50)
    
    # Check Python version
    print(f"✅ Python version: {sys.version}")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️ .env file not found - API keys may not be loaded")
    
    # Check API keys
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    e2b_key = os.getenv('E2B_API_KEY')
    
    if elevenlabs_key:
        print(f"✅ ELEVENLABS_API_KEY found: {elevenlabs_key[:8]}...{elevenlabs_key[-4:]}")
    else:
        print("⚠️ ELEVENLABS_API_KEY not found")
    
    if e2b_key:
        print(f"✅ E2B_API_KEY found: {e2b_key[:8]}...{e2b_key[-4:]}")
    else:
        print("⚠️ E2B_API_KEY not found")
    
    # Test imports
    print("\n📦 Testing imports...")
    
    try:
        import streamlit
        print("✅ streamlit")
    except ImportError:
        print("❌ streamlit - Install with: pip install streamlit")
    
    try:
        import moviepy
        print("✅ moviepy")
    except ImportError:
        print("❌ moviepy - Install with: pip install moviepy")
    
    try:
        import manim
        print("✅ manim")
    except ImportError:
        print("❌ manim - Install with: pip install manim")
    
    try:
        import requests
        print("✅ requests")
    except ImportError:
        print("❌ requests - Install with: pip install requests")
    
    try:
        import numpy
        print("✅ numpy")
    except ImportError:
        print("❌ numpy - Install with: pip install numpy")
    
    try:
        import matplotlib
        print("✅ matplotlib")
    except ImportError:
        print("❌ matplotlib - Install with: pip install matplotlib")
    
    # Test enhanced modules
    print("\n🔧 Testing enhanced modules...")
    
    try:
        from code_analysis import EnhancedCodeAnalyzer
        print("✅ code_analysis")
    except ImportError as e:
        print(f"❌ code_analysis: {e}")
    
    try:
        from error_simulation import ErrorSimulator
        print("✅ error_simulation")
    except ImportError as e:
        print(f"❌ error_simulation: {e}")
    
    try:
        from narration import AINarrator
        print("✅ narration")
    except ImportError as e:
        print(f"❌ narration: {e}")
    
    try:
        from parsers import ParserManager
        print("✅ parsers")
    except ImportError as e:
        print(f"❌ parsers: {e}")
    
    # Test optional dependencies
    print("\n🎯 Testing optional dependencies...")
    
    try:
        import e2b
        print("✅ e2b (for dynamic execution)")
    except ImportError:
        print("⚠️ e2b not installed - dynamic execution will use simulation")
    
    try:
        import elevenlabs
        print("✅ elevenlabs (for AI narration)")
    except ImportError:
        print("⚠️ elevenlabs not installed - AI narration will use fallback")
    
    try:
        import pycallgraph2
        print("✅ pycallgraph2 (for call graphs)")
    except ImportError:
        print("⚠️ pycallgraph2 not installed - call graphs will use fallback")
    
    try:
        import networkx
        print("✅ networkx (for graph visualization)")
    except ImportError:
        print("⚠️ networkx not installed - graph visualization will use fallback")
    
    print("\n" + "=" * 50)
    print("🎉 Setup test complete!")
    print("\nNext steps:")
    print("1. If you see any ❌ errors, install missing dependencies")
    print("2. Run: python debug_config.py for comprehensive testing")
    print("3. Run: python enhanced_example.py for feature demonstration")
    print("4. Run: streamlit run app.py for the web interface")
    print("=" * 50)

if __name__ == "__main__":
    test_basic_setup() 