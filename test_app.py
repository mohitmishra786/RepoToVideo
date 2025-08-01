#!/usr/bin/env python3
"""
Test script for RepoToVideo

This script tests all components of the RepoToVideo application to ensure
everything is working correctly.
"""

import sys
import os
import tempfile
import time
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        from github import Github
        print("✅ PyGitHub imported")
    except ImportError as e:
        print(f"❌ PyGitHub import failed: {e}")
        return False
    
    try:
        from gtts import gTTS
        print("✅ gTTS imported")
    except ImportError as e:
        print(f"❌ gTTS import failed: {e}")
        return False
    
    try:
        from moviepy import VideoFileClip
        print("✅ MoviePy imported")
    except ImportError as e:
        print(f"❌ MoviePy import failed: {e}")
        return False
    
    try:
        import markdown
        print("✅ Markdown imported")
    except ImportError as e:
        print(f"❌ Markdown import failed: {e}")
        return False
    
    try:
        import matplotlib
        print("✅ Matplotlib imported")
    except ImportError as e:
        print(f"❌ Matplotlib import failed: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow imported")
    except ImportError as e:
        print(f"❌ Pillow import failed: {e}")
        return False
    
    return True


def test_repo_fetcher():
    """Test the repository fetcher module."""
    print("\n🔍 Testing repository fetcher...")
    
    try:
        from repo_fetcher import RepoFetcher
        
        # Test URL validation
        fetcher = RepoFetcher()
        is_valid, owner, repo = fetcher.validate_github_url("https://github.com/scikit-learn/scikit-learn")
        
        if is_valid and owner == "scikit-learn" and repo == "scikit-learn":
            print("✅ URL validation working")
        else:
            print("❌ URL validation failed")
            return False
        
        # Test rate limit info
        rate_info = fetcher.get_rate_limit_info()
        if isinstance(rate_info, dict) and 'limit' in rate_info:
            print("✅ Rate limit info working")
        else:
            print("❌ Rate limit info failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Repository fetcher test failed: {e}")
        return False


def test_step_generator():
    """Test the step generator module."""
    print("\n🔍 Testing step generator...")
    
    try:
        from step_generator import StepGenerator
        
        generator = StepGenerator()
        
        # Test with mock repository data
        mock_repo = {
            'name': 'test-repo',
            'owner': 'test-user',
            'description': 'A test repository',
            'language': 'Python',
            'stars': 100,
            'forks': 50,
            'files': [],
            'readme': None,
            'main_files': [],
            'structure': {
                'total_files': 10,
                'code_files': 5,
                'doc_files': 2,
                'languages': {'.py': 3},
                'directories': ['src', 'tests']
            }
        }
        
        steps = generator.generate_steps(mock_repo)
        
        if isinstance(steps, list) and len(steps) > 0:
            print(f"✅ Step generation working ({len(steps)} steps created)")
        else:
            print("❌ Step generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Step generator test failed: {e}")
        return False


def test_voice_generator():
    """Test the voice generator module."""
    print("\n🔍 Testing voice generator...")
    
    try:
        from voice_generator import VoiceGenerator
        
        generator = VoiceGenerator()
        
        # Test text cleaning
        test_text = "def hello_world(): print('Hello, World!')"
        cleaned = generator._clean_text(test_text)
        
        if cleaned and len(cleaned) > 0:
            print("✅ Text cleaning working")
        else:
            print("❌ Text cleaning failed")
            return False
        
        # Test available languages
        languages = generator.get_available_languages()
        if isinstance(languages, dict) and len(languages) > 0:
            print(f"✅ Language detection working ({len(languages)} languages available)")
        else:
            print("❌ Language detection failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Voice generator test failed: {e}")
        return False


def test_video_generator():
    """Test the video generator module."""
    print("\n🔍 Testing video generator...")
    
    try:
        from video_generator import VideoGenerator
        
        generator = VideoGenerator()
        
        # Test resolution setting
        if generator.resolution == (1920, 1080):
            print("✅ Default resolution set correctly")
        else:
            print("❌ Default resolution not set correctly")
            return False
        
        # Test background color
        if generator.background_color == (25, 25, 35):
            print("✅ Background color set correctly")
        else:
            print("❌ Background color not set correctly")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Video generator test failed: {e}")
        return False


def test_github_api():
    """Test GitHub API connectivity."""
    print("\n🔍 Testing GitHub API...")
    
    try:
        from github import Github
        
        # Test anonymous access
        g = Github()
        rate_limit = g.get_rate_limit()
        
        if rate_limit.rate.remaining > 0:
            print(f"✅ GitHub API accessible (remaining requests: {rate_limit.rate.remaining})")
        else:
            print("⚠️  GitHub API rate limit reached")
        
        return True
        
    except Exception as e:
        print(f"❌ GitHub API test failed: {e}")
        return False


def test_tts_service():
    """Test text-to-speech service."""
    print("\n🔍 Testing TTS service...")
    
    try:
        from gtts import gTTS
        
        # Test TTS creation (without saving)
        tts = gTTS(text="Test", lang='en')
        print("✅ TTS service accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ TTS service test failed: {e}")
        return False


def test_moviepy():
    """Test MoviePy functionality."""
    print("\n🔍 Testing MoviePy...")
    
    try:
        from moviepy import ColorClip
        
        # Test basic clip creation
        clip = ColorClip(size=(100, 100), color=(255, 0, 0))
        print("✅ MoviePy basic functionality working")
        
        return True
        
    except Exception as e:
        print(f"❌ MoviePy test failed: {e}")
        return False


def test_file_permissions():
    """Test file and directory permissions."""
    print("\n🔍 Testing file permissions...")
    
    try:
        # Test creating temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test")
            
            if test_file.exists():
                print("✅ File creation and writing working")
            else:
                print("❌ File creation failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ File permissions test failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("🧪 RepoToVideo Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Tests", test_imports),
        ("Repository Fetcher", test_repo_fetcher),
        ("Step Generator", test_step_generator),
        ("Voice Generator", test_voice_generator),
        ("Video Generator", test_video_generator),
        ("GitHub API", test_github_api),
        ("TTS Service", test_tts_service),
        ("MoviePy", test_moviepy),
        ("File Permissions", test_file_permissions),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RepoToVideo is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 