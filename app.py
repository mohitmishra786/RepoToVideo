"""
RepoToVideo - Main Streamlit Application

A complete web application that converts GitHub repository URLs into animated
step-by-step video walkthroughs using Streamlit as the frontend framework.
"""

import streamlit as st
import os
import sys
import time
import tempfile
import logging
from typing import Optional, List
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('repotovideo.log')
    ]
)
logger = logging.getLogger(__name__)

# Import our custom modules
from repo_fetcher import RepoFetcher
from step_generator import StepGenerator
from voice_generator import VoiceGenerator
from video_generator import VideoGenerator


def main():
    """Main Streamlit application."""
    
    logger.info("Starting RepoToVideo application")
    
    # Configure page
    st.set_page_config(
        page_title="RepoToVideo",
        page_icon="🎥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🎥 RepoToVideo</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Convert GitHub repositories into animated video walkthroughs</p>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # GitHub token input
        default_token = os.getenv('GITHUB_TOKEN', '')
        github_token = st.text_input(
            "GitHub Token (Optional)",
            value=default_token,
            type="password",
            help="Enter your GitHub personal access token for higher rate limits and private repo access"
        )
        
        # Voice settings
        st.subheader("🎤 Voice Settings")
        voice_language = st.selectbox(
            "Language",
            ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
            help="Select the language for text-to-speech"
        )
        
        voice_speed = st.selectbox(
            "Speech Speed",
            ["Normal", "Slow"],
            help="Select speech speed for narration"
        )
        
        # Video settings
        st.subheader("🎬 Video Settings")
        video_quality = st.selectbox(
            "Video Quality",
            ["1080p", "720p", "480p"],
            help="Select video resolution"
        )
        
        # Example repositories
        st.subheader("📚 Example Repositories")
        example_repos = [
            "https://github.com/scikit-learn/scikit-learn",
            "https://github.com/pandas-dev/pandas",
            "https://github.com/numpy/numpy",
            "https://github.com/matplotlib/matplotlib",
            "https://github.com/streamlit/streamlit"
        ]
        
        selected_example = st.selectbox(
            "Try with example:",
            ["Select an example..."] + example_repos
        )
        
        if selected_example != "Select an example...":
            st.session_state.github_url = selected_example
    
    # Main content area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # URL input
        st.header("🔗 Enter GitHub Repository URL")
        
        github_url = st.text_input(
            "GitHub Repository URL",
            value=st.session_state.get('github_url', ''),
            placeholder="https://github.com/username/repository",
            help="Enter a valid GitHub repository URL"
        )
        
        # Generate button
        generate_button = st.button(
            "🎬 Generate Video Walkthrough",
            type="primary",
            use_container_width=True
        )
        
        # Progress tracking
        if 'progress' not in st.session_state:
            st.session_state.progress = 0
        if 'current_step' not in st.session_state:
            st.session_state.current_step = ""
        if 'video_path' not in st.session_state:
            st.session_state.video_path = None
        
        # Progress bar
        if st.session_state.progress > 0:
            st.progress(st.session_state.progress / 100)
            st.info(f"🔄 {st.session_state.current_step}")
            
            # Debug information
            if st.checkbox("Show Debug Info"):
                st.write("Debug Information:")
                st.write(f"Progress: {st.session_state.progress}")
                st.write(f"Current Step: {st.session_state.current_step}")
                st.write(f"Session State Keys: {list(st.session_state.keys())}")
                if 'repo_analysis' in st.session_state:
                    st.write(f"Repo Analysis Keys: {list(st.session_state.repo_analysis.keys())}")
                if 'steps' in st.session_state:
                    st.write(f"Number of Steps: {len(st.session_state.steps)}")
        
        # Main processing logic
        if generate_button and github_url:
            try:
                logger.info(f"Starting video generation for repository: {github_url}")
                
                # Validate URL
                if not github_url.startswith("https://github.com/"):
                    logger.error(f"Invalid GitHub URL: {github_url}")
                    st.error("❌ Please enter a valid GitHub repository URL")
                    return
                
                logger.info("URL validation passed")
                
                # Initialize components
                with st.spinner("🔄 Initializing components..."):
                    logger.info("Initializing RepoFetcher")
                    if github_token:
                        logger.info("Using GitHub token for authentication")
                    else:
                        logger.warning("No GitHub token provided - using anonymous access (limited rate)")
                    repo_fetcher = RepoFetcher(github_token if github_token else None)
                    
                    logger.info("Initializing StepGenerator")
                    step_generator = StepGenerator()
                    
                    logger.info("Initializing VoiceGenerator")
                    voice_generator = VoiceGenerator(
                        language=voice_language,
                        slow=(voice_speed == "Slow")
                    )
                    
                    # Set video quality
                    quality_map = {"1080p": (1920, 1080), "720p": (1280, 720), "480p": (854, 480)}
                    logger.info(f"Setting video quality: {video_quality}")
                    video_generator = VideoGenerator("walkthrough.mp4")
                    video_generator.resolution = quality_map[video_quality]
                
                logger.info("All components initialized successfully")
                st.session_state.progress = 10
                st.session_state.current_step = "Fetching repository..."
                st.session_state.repo_fetcher = repo_fetcher
                st.session_state.step_generator = step_generator
                st.session_state.voice_generator = voice_generator
                st.session_state.video_generator = video_generator
                st.session_state.github_url = github_url
                
            except Exception as e:
                logger.error(f"Error during initialization: {str(e)}")
                st.error(f"❌ Error initializing: {str(e)}")
                return
        
        # Process if we have components initialized
        if st.session_state.progress > 0 and 'repo_fetcher' in st.session_state:
            logger.info(f"Processing step with progress: {st.session_state.progress}")
            logger.info(f"Current step message: {st.session_state.current_step}")
            try:
                # Step 1: Fetch repository
                if st.session_state.progress == 10:
                    with st.spinner("📥 Fetching repository data..."):
                        logger.info("Starting repository fetch")
                        try:
                            repo = st.session_state.repo_fetcher.fetch_repo(st.session_state.github_url)
                            logger.info(f"Repository fetched successfully: {repo.name}")
                            
                            logger.info("Starting repository analysis")
                            repo_analysis = st.session_state.repo_fetcher.analyze_repo(repo)
                            logger.info(f"Repository analysis completed. Files found: {repo_analysis['structure']['total_files']}")
                            
                            st.session_state.repo_analysis = repo_analysis
                            st.session_state.progress = 25
                            st.session_state.current_step = "Analyzing repository structure..."
                            logger.info("Repository analysis phase completed, progress set to 25")
                            
                            # Force immediate processing of next step
                            logger.info("Forcing immediate step generation...")
                            try:
                                steps = st.session_state.step_generator.generate_steps(repo_analysis)
                                logger.info(f"Step generation completed. Generated {len(steps)} steps")
                                
                                # Log step details
                                for i, step in enumerate(steps):
                                    logger.info(f"Step {i+1}: {step.get('title', 'No title')} - Type: {step.get('type', 'Unknown')}")
                                
                                st.session_state.steps = steps
                                st.session_state.progress = 40
                                st.session_state.current_step = "Generating voice narration..."
                                logger.info("Step generation phase completed, moving to voice generation")
                                
                                # Continue with voice generation
                                logger.info("Starting voice generation immediately...")
                                audio_files = []
                                for i, step in enumerate(steps):
                                    logger.info(f"Generating voice for step {i+1}: {step.get('title', 'No title')}")
                                    logger.info(f"Step {i+1} voice script length: {len(step.get('voice_script', ''))}")
                                    
                                    audio_file = st.session_state.voice_generator.generate_step_voice(step, i + 1)
                                    logger.info(f"Step {i+1} audio file generated: {audio_file}")
                                    audio_files.append(audio_file)
                                
                                logger.info(f"Voice generation completed. Generated {len(audio_files)} audio files")
                                logger.info(f"Audio files: {audio_files}")
                                st.session_state.audio_files = audio_files
                                st.session_state.progress = 60
                                st.session_state.current_step = "Creating video content..."
                                logger.info("Voice generation phase completed, moving to video generation")
                                
                                # Continue with video generation
                                logger.info("Starting video generation immediately...")
                                video_path = st.session_state.video_generator.create_video(steps, audio_files)
                                
                                if video_path and os.path.exists(video_path):
                                    logger.info(f"Video generated successfully: {video_path}")
                                    st.session_state.video_path = video_path
                                    st.session_state.progress = 100
                                    st.session_state.current_step = "Video generation complete!"
                                    logger.info("Video generation completed successfully!")
                                else:
                                    logger.error("Video generation failed - no output file")
                                    st.error("Failed to generate video")
                                    st.session_state.progress = 0
                                    
                            except Exception as e:
                                logger.error(f"Error during immediate processing: {str(e)}")
                                logger.error(f"Full traceback: {traceback.format_exc()}")
                                st.error(f"Error during processing: {str(e)}")
                                st.session_state.progress = 0
                        except Exception as e:
                            logger.error(f"Error during repository fetch/analysis: {str(e)}")
                            st.error(f"❌ Error fetching repository: {str(e)}")
                            st.session_state.progress = 0
                            st.session_state.current_step = ""
                
                # Step 2: Generate steps
                elif st.session_state.progress == 25:
                    with st.spinner("📋 Generating step-by-step analysis..."):
                        logger.info("Starting step generation")
                        logger.info(f"Repository analysis data keys: {list(st.session_state.repo_analysis.keys())}")
                        logger.info(f"Repository name: {st.session_state.repo_analysis.get('name', 'Unknown')}")
                        logger.info(f"Repository language: {st.session_state.repo_analysis.get('language', 'Unknown')}")
                        logger.info(f"Total files: {st.session_state.repo_analysis.get('structure', {}).get('total_files', 0)}")
                        
                        try:
                            logger.info("Calling step generator...")
                            steps = st.session_state.step_generator.generate_steps(st.session_state.repo_analysis)
                            logger.info(f"Step generation completed. Generated {len(steps)} steps")
                            
                            # Log step details
                            for i, step in enumerate(steps):
                                logger.info(f"Step {i+1}: {step.get('title', 'No title')} - Type: {step.get('type', 'Unknown')}")
                            
                            st.session_state.steps = steps
                            st.session_state.progress = 40
                            st.session_state.current_step = "Generating voice narration..."
                            logger.info("Step generation phase completed, moving to voice generation")
                        except Exception as e:
                            logger.error(f"Error during step generation: {str(e)}")
                            logger.error(f"Full traceback: {traceback.format_exc()}")
                            st.error(f"❌ Error generating steps: {str(e)}")
                            st.session_state.progress = 0
                            st.session_state.current_step = ""
                
                # Step 3: Generate voice
                elif st.session_state.progress == 40:
                    with st.spinner("🎤 Generating voice narration..."):
                        logger.info("Starting voice generation")
                        logger.info(f"Number of steps to process: {len(st.session_state.steps)}")
                        
                        try:
                            audio_files = []
                            for i, step in enumerate(st.session_state.steps):
                                logger.info(f"Generating voice for step {i+1}: {step.get('title', 'No title')}")
                                logger.info(f"Step {i+1} voice script length: {len(step.get('voice_script', ''))}")
                                
                                audio_file = st.session_state.voice_generator.generate_step_voice(step, i + 1)
                                logger.info(f"Step {i+1} audio file generated: {audio_file}")
                                audio_files.append(audio_file)
                            
                            logger.info(f"Voice generation completed. Generated {len(audio_files)} audio files")
                            logger.info(f"Audio files: {audio_files}")
                            st.session_state.audio_files = audio_files
                            st.session_state.progress = 60
                            st.session_state.current_step = "Creating video content..."
                            logger.info("Voice generation phase completed, moving to video generation")
                        except Exception as e:
                            logger.error(f"Error during voice generation: {str(e)}")
                            logger.error(f"Full traceback: {traceback.format_exc()}")
                            st.error(f"❌ Error generating voice: {str(e)}")
                            st.session_state.progress = 0
                            st.session_state.current_step = ""
                
                # Step 4: Generate video
                elif st.session_state.progress == 60:
                    with st.spinner("🎬 Creating video walkthrough..."):
                        logger.info("Starting video generation")
                        try:
                            video_path = st.session_state.video_generator.create_video(
                                st.session_state.steps,
                                st.session_state.audio_files
                            )
                            
                            if video_path and os.path.exists(video_path):
                                logger.info(f"Video generated successfully: {video_path}")
                                st.session_state.video_path = video_path
                                st.session_state.progress = 100
                                st.session_state.current_step = "Video generation complete!"
                            else:
                                logger.error("Video generation failed - no output file")
                                st.error("❌ Failed to generate video")
                                st.session_state.progress = 0
                        except Exception as e:
                            logger.error(f"Error during video generation: {str(e)}")
                            st.error(f"❌ Error generating video: {str(e)}")
                            st.session_state.progress = 0
                            st.session_state.current_step = ""
                
                # Step 5: Display results
                elif st.session_state.progress == 100:
                    st.success("✅ Video generation complete!")
                    
                    # Display repository info
                    repo_analysis = st.session_state.repo_analysis
                    st.subheader("📊 Repository Information")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Repository", repo_analysis['name'])
                        st.metric("Owner", repo_analysis['owner'])
                    with col2:
                        st.metric("Language", repo_analysis['language'] or "Unknown")
                        st.metric("Stars", repo_analysis['stars'])
                    with col3:
                        st.metric("Forks", repo_analysis['forks'])
                        st.metric("Files", repo_analysis['structure']['total_files'])
                    
                    # Display steps summary
                    st.subheader("📋 Generated Steps")
                    steps = st.session_state.steps
                    for i, step in enumerate(steps):
                        st.write(f"**Step {i+1}:** {step['title']} ({step['duration']}s)")
                    
                    # Video download
                    st.subheader("🎥 Download Video")
                    if st.session_state.video_path:
                        with open(st.session_state.video_path, "rb") as file:
                            st.download_button(
                                label="📥 Download MP4 Video",
                                data=file.read(),
                                file_name="walkthrough.mp4",
                                mime="video/mp4",
                                use_container_width=True
                            )
                        
                        # Display video info
                        file_size = os.path.getsize(st.session_state.video_path) / (1024 * 1024)  # MB
                        st.info(f"📊 Video size: {file_size:.1f} MB")
                    
                    # Reset button
                    if st.button("🔄 Generate Another Video", use_container_width=True):
                        st.session_state.progress = 0
                        st.session_state.current_step = ""
                        st.session_state.video_path = None
                        # Clear all session state variables
                        for key in ['repo_fetcher', 'step_generator', 'voice_generator', 'video_generator', 'github_url', 'repo_analysis', 'steps', 'audio_files']:
                            if key in st.session_state:
                                del st.session_state[key]
                
            except Exception as e:
                st.error(f"❌ Error during processing: {str(e)}")
                st.error(f"Details: {traceback.format_exc()}")
                st.session_state.progress = 0
                st.session_state.current_step = ""
                # Clear all session state variables
                for key in ['repo_fetcher', 'step_generator', 'voice_generator', 'video_generator', 'github_url', 'repo_analysis', 'steps', 'audio_files']:
                    if key in st.session_state:
                        del st.session_state[key]
        
        # Information section
        if not generate_button or st.session_state.progress == 0:
            st.markdown("---")
            st.subheader("ℹ️ How it works")
            
            st.markdown("""
            <div class="info-box">
            <h4>🔍 Repository Analysis</h4>
            <p>The app fetches your GitHub repository and analyzes its structure, 
            including code files, documentation, and project metadata.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="info-box">
            <h4>📋 Step Generation</h4>
            <p>Based on the analysis, it creates a step-by-step walkthrough covering 
            the repository overview, code structure, and key features.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="info-box">
            <h4>🎤 Voice Narration</h4>
            <p>Each step is narrated using text-to-speech technology, explaining 
            the code and concepts in natural language.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="info-box">
            <h4>🎬 Video Creation</h4>
            <p>The final video combines visual content, voice narration, and 
            animations to create an engaging walkthrough experience.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Features
            st.subheader("✨ Features")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("✅ **Multi-language support**")
                st.write("✅ **1080p video quality**")
                st.write("✅ **Voice narration**")
                st.write("✅ **Code highlighting**")
            
            with col2:
                st.write("✅ **Error simulation**")
                st.write("✅ **Step-by-step analysis**")
                st.write("✅ **Repository statistics**")
                st.write("✅ **Downloadable MP4**")
            
            # Supported languages
            st.subheader("🔧 Supported Languages")
            st.write("Currently optimized for Python repositories, with support for:")
            st.write("• Python (.py)")
            st.write("• JavaScript (.js)")
            st.write("• TypeScript (.ts)")
            st.write("• Java (.java)")
            st.write("• And many more...")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>Made with ❤️ using Streamlit, PyGitHub, gTTS, and MoviePy</p>",
        unsafe_allow_html=True
    )


def validate_github_url(url: str) -> bool:
    """
    Validate if the URL is a valid GitHub repository URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r'https://github\.com/[^/]+/[^/]+'
    return bool(re.match(pattern, url))


if __name__ == "__main__":
    main() 