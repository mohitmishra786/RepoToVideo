#!/usr/bin/env python3
"""
Test script for audio generation functionality using ElevenLabs API.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_audio_generation():
    """Test the audio generation functionality."""
    try:
        from advanced_animation.audio.audio_generator import AudioGenerator
        
        # Initialize audio generator
        audio_gen = AudioGenerator()
        
        if not audio_gen.available:
            logger.error("Audio generation not available - check ELEVENLABS_API_KEY in .env file")
            return False
        
        # Test connection
        logger.info("Testing ElevenLabs API connection...")
        if not audio_gen.test_connection():
            logger.error("Failed to connect to ElevenLabs API")
            return False
        
        logger.info("✅ ElevenLabs API connection successful")
        
        # Test audio generation
        test_text = "Hello! This is a test of the audio generation system. We're creating voice narration for educational videos."
        output_path = "test_audio_output.mp3"
        
        logger.info(f"Generating test audio: {test_text}")
        success = audio_gen.generate_audio(test_text, output_path)
        
        if success:
            logger.info(f"✅ Audio generated successfully: {output_path}")
            
            # Check if file exists and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"✅ Audio file created: {os.path.getsize(output_path)} bytes")
                return True
            else:
                logger.error("❌ Audio file was not created or is empty")
                return False
        else:
            logger.error("❌ Failed to generate audio")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Failed to import audio generator: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing audio generation: {e}")
        return False

def test_available_voices():
    """Test getting available voices from ElevenLabs."""
    try:
        from advanced_animation.audio.audio_generator import AudioGenerator
        
        audio_gen = AudioGenerator()
        
        if not audio_gen.available:
            logger.error("Audio generation not available")
            return False
        
        voices = audio_gen.get_available_voices()
        
        if voices:
            logger.info(f"✅ Found {len(voices)} available voices:")
            for i, voice in enumerate(voices[:5]):  # Show first 5 voices
                logger.info(f"  {i+1}. {voice.get('name', 'Unknown')} (ID: {voice.get('voice_id', 'Unknown')})")
            return True
        else:
            logger.error("❌ No voices found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing available voices: {e}")
        return False

def main():
    """Main test function."""
    logger.info("🎵 Testing Audio Generation System")
    logger.info("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        logger.error("❌ ELEVENLABS_API_KEY not found in .env file")
        logger.info("Please add your ElevenLabs API key to the .env file:")
        logger.info("ELEVENLABS_API_KEY=your_api_key_here")
        return False
    
    logger.info("✅ ELEVENLABS_API_KEY found in .env file")
    
    # Test available voices
    logger.info("\n🔊 Testing available voices...")
    if not test_available_voices():
        logger.error("Voice test failed")
        return False
    
    # Test audio generation
    logger.info("\n🎤 Testing audio generation...")
    if not test_audio_generation():
        logger.error("Audio generation test failed")
        return False
    
    logger.info("\n🎉 All audio generation tests passed!")
    logger.info("The audio generation system is working correctly.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 