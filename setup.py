#!/usr/bin/env python3
"""
Setup script for RepoToVideo

This script helps users install and configure the RepoToVideo application.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        # Install from requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def check_system_requirements():
    """Check system requirements."""
    print("🔍 Checking system requirements...")
    
    # Check available disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (1024**3)
        if free_gb < 1:
            print(f"⚠️  Warning: Low disk space ({free_gb} GB free). At least 1 GB recommended.")
        else:
            print(f"✅ Disk space: {free_gb} GB free")
    except Exception as e:
        print(f"⚠️  Could not check disk space: {e}")
    
    # Check internet connectivity
    try:
        import urllib.request
        urllib.request.urlopen("https://www.google.com", timeout=5)
        print("✅ Internet connection available")
    except Exception:
        print("⚠️  Warning: No internet connection detected. Required for TTS and GitHub API.")
    
    return True


def create_config_file():
    """Create a basic configuration file."""
    config_content = """# RepoToVideo Configuration

# GitHub Settings
GITHUB_TOKEN=your_github_token_here

# Video Settings
DEFAULT_VIDEO_QUALITY=1080p
DEFAULT_LANGUAGE=en

# Output Settings
OUTPUT_DIR=./output
TEMP_DIR=./temp

# Voice Settings
TTS_LANGUAGE=en
TTS_SPEED=normal
"""
    
    config_path = Path("config.env")
    if not config_path.exists():
        with open(config_path, "w") as f:
            f.write(config_content)
        print("✅ Created config.env file")
        print("📝 Please edit config.env with your settings")
    else:
        print("ℹ️  config.env already exists")


def create_directories():
    """Create necessary directories."""
    directories = ["output", "temp", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Created necessary directories")


def test_installation():
    """Test the installation."""
    print("🧪 Testing installation...")
    
    try:
        # Test imports
        import streamlit
        import PyGithub
        import gtts
        import moviepy
        import markdown
        print("✅ All modules imported successfully")
        
        # Test Streamlit
        result = subprocess.run([sys.executable, "-m", "streamlit", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Streamlit version: {result.stdout.strip()}")
        else:
            print("❌ Streamlit test failed")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def show_next_steps():
    """Show next steps for the user."""
    print("\n" + "="*50)
    print("🎉 Installation complete!")
    print("="*50)
    
    print("\n📋 Next steps:")
    print("1. Run the application:")
    print("   streamlit run app.py")
    print("\n2. Open your browser to: http://localhost:8501")
    print("\n3. Enter a GitHub repository URL to get started")
    print("\n4. Try an example repository:")
    print("   https://github.com/scikit-learn/scikit-learn")
    
    print("\n📚 Documentation:")
    print("- README.md: Complete documentation")
    print("- GitHub Issues: Report bugs and request features")
    
    print("\n🔧 Configuration:")
    print("- Edit config.env for custom settings")
    print("- Add GitHub token for private repositories")
    
    print("\n💡 Tips:")
    print("- Start with small repositories for faster processing")
    print("- Use 720p quality for faster video generation")
    print("- Ensure stable internet connection for TTS services")


def main():
    """Main setup function."""
    print("🎥 RepoToVideo Setup")
    print("="*30)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check system requirements
    check_system_requirements()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create config file
    create_config_file()
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    # Show next steps
    show_next_steps()


if __name__ == "__main__":
    main() 