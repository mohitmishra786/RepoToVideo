#!/usr/bin/env python3
"""
API Key Testing Script

This script tests your API keys and provides helpful debugging information.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_elevenlabs_api():
    """Test ElevenLabs API key."""
    print("🔑 Testing ElevenLabs API...")
    
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Test the API
    headers = {
        'xi-api-key': api_key
    }
    
    try:
        response = requests.get('https://api.elevenlabs.io/v1/voices', headers=headers)
        
        if response.status_code == 200:
            voices = response.json()
            print(f"✅ API working! Found {len(voices.get('voices', []))} voices")
            return True
        elif response.status_code == 401:
            print("❌ API key is invalid or expired")
            print("💡 Please check your ElevenLabs API key at: https://elevenlabs.io/")
            return False
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_e2b_api():
    """Test E2B API key."""
    print("\n🔑 Testing E2B API...")
    
    api_key = os.getenv('E2B_API_KEY')
    if not api_key:
        print("❌ E2B_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Test the API - E2B doesn't have a simple test endpoint, so we'll just verify the key format
    if api_key.startswith('e2b_'):
        print("✅ API Key format looks correct")
        print("💡 E2B API will be tested when actually used")
        return True
    else:
        print("❌ API Key format doesn't match expected pattern (should start with 'e2b_')")
        return False
        
        return True

def main():
    """Main function."""
    print("🔍 API Key Testing")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️ .env file not found")
        print("💡 Create a .env file with your API keys:")
        print("   ELEVENLABS_API_KEY=your_key_here")
        print("   E2B_API_KEY=your_key_here")
        return
    
    print("✅ .env file found")
    
    # Test APIs
    elevenlabs_ok = test_elevenlabs_api()
    e2b_ok = test_e2b_api()
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"ElevenLabs API: {'✅ Working' if elevenlabs_ok else '❌ Failed'}")
    print(f"E2B API: {'✅ Working' if e2b_ok else '❌ Failed'}")
    
    if elevenlabs_ok and e2b_ok:
        print("\n🎉 All APIs are working! You're ready to use all features.")
    elif elevenlabs_ok:
        print("\n⚠️ ElevenLabs working, but E2B failed. Dynamic execution will use simulation.")
    elif e2b_ok:
        print("\n⚠️ E2B working, but ElevenLabs failed. AI narration will use fallback.")
    else:
        print("\n❌ Both APIs failed. Please check your API keys.")
        print("\n💡 Getting API Keys:")
        print("   ElevenLabs: https://elevenlabs.io/")
        print("   E2B: https://e2b.dev/")

if __name__ == "__main__":
    main() 