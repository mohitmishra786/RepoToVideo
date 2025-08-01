"""
Video Generator Module

This module handles video generation using MoviePy to create animated walkthroughs
of GitHub repositories.
"""

import os
import tempfile
import numpy as np
from typing import List, Dict, Optional, Tuple
from moviepy import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
    ColorClip, ImageClip, concatenate_videoclips, vfx
)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont
import io


class VideoGenerator:
    """Handles video generation for repository walkthroughs."""
    
    def __init__(self, output_path: str = "walkthrough.mp4"):
        """
        Initialize the VideoGenerator.
        
        Args:
            output_path: Path for the output video file
        """
        self.output_path = output_path
        self.temp_dir = tempfile.mkdtemp()
        self.clips = []
        self.resolution = (1920, 1080)  # 1080p
        self.fps = 30
        self.background_color = (25, 25, 35)  # Dark blue-gray
        
    def create_video(self, steps: List[Dict], audio_files: List[str]) -> str:
        """
        Create the complete video from steps and audio files.
        
        Args:
            steps: List of step dictionaries
            audio_files: List of audio file paths
            
        Returns:
            Path to the generated video file
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Starting video generation with {len(steps)} steps and {len(audio_files)} audio files")
            
            # Create video clips for each step
            video_clips = []
            
            for i, step in enumerate(steps):
                logger.info(f"Creating visual for step {i+1}: {step.get('title', 'Unknown')}")
                try:
                    # Create visual content for the step
                    visual_clip = self._create_simple_step_visual(step, i + 1)
                    logger.info(f"Visual clip created for step {i+1}")
                    
                    # Get corresponding audio
                    audio_clip = None
                    if i < len(audio_files) and audio_files[i]:
                        try:
                            logger.info(f"Loading audio file: {audio_files[i]}")
                            audio_clip = AudioFileClip(audio_files[i])
                            logger.info(f"Audio clip loaded for step {i+1}, duration: {audio_clip.duration}")
                        except Exception as e:
                            logger.error(f"Error loading audio file {audio_files[i]}: {str(e)}")
                    
                    # Combine visual and audio
                    if audio_clip:
                        # Create new ColorClip with audio duration - use the same color as the original clip
                        step_type = step.get('type', 'generic')
                        if step_type == 'intro':
                            color = (50, 100, 150)  # Blue
                        elif step_type == 'overview':
                            color = (100, 50, 150)  # Purple
                        elif step_type == 'structure':
                            color = (150, 100, 50)  # Orange
                        elif step_type == 'code_analysis':
                            color = (100, 150, 50)  # Green
                        elif step_type == 'code_review':
                            color = (150, 50, 100)  # Pink
                        elif step_type == 'error_simulation':
                            color = (150, 50, 50)  # Red
                        elif step_type == 'summary':
                            color = (50, 150, 100)  # Teal
                        else:
                            color = self.background_color
                        
                        final_clip = ColorClip(size=self.resolution, color=color, duration=audio_clip.duration).set_audio(audio_clip)
                        logger.info(f"Combined visual and audio for step {i+1}, duration: {audio_clip.duration}")
                    else:
                        # Use default duration if no audio
                        default_duration = step.get('duration', 30)
                        final_clip = visual_clip
                        logger.info(f"Using default duration for step {i+1}: {default_duration}")
                    
                    video_clips.append(final_clip)
                    logger.info(f"Step {i+1} clip added to video clips list")
                    
                except Exception as e:
                    logger.error(f"Error creating visual for step {i+1}: {str(e)}")
                    import traceback
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                    # Create a simple error clip instead
                    error_clip = self._create_simple_error_visual(f"Error in step {i+1}: {str(e)}")
                    video_clips.append(error_clip)
            
            logger.info(f"Created {len(video_clips)} video clips")
            
            # Concatenate all clips
            if video_clips:
                logger.info("Concatenating video clips...")
                final_video = concatenate_videoclips(video_clips, method="compose")
                logger.info("Video clips concatenated successfully")
                
                # Write the final video
                logger.info(f"Writing video to: {self.output_path}")
                final_video.write_videofile(
                    self.output_path,
                    fps=self.fps,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True
                )
                
                logger.info(f"Video written successfully to: {self.output_path}")
                
                # Clean up
                final_video.close()
                for clip in video_clips:
                    clip.close()
                
                # Verify file exists
                if os.path.exists(self.output_path):
                    file_size = os.path.getsize(self.output_path)
                    logger.info(f"Video file created successfully. Size: {file_size} bytes")
                    return self.output_path
                else:
                    logger.error(f"Video file was not created at: {self.output_path}")
                    raise FileNotFoundError(f"Video file not found at {self.output_path}")
            else:
                logger.error("No video clips were created")
                raise ValueError("No video clips were created")
                
        except Exception as e:
            logger.error(f"Error in create_video: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise
                
    def _create_simple_step_visual(self, step: Dict, step_number: int) -> VideoFileClip:
        """
        Create a simple visual for a step using basic ColorClip.
        
        Args:
            step: Step dictionary
            step_number: Number of the step
            
        Returns:
            VideoFileClip for the step
        """
        step_type = step.get('type', 'generic')
        
        if step_type == 'intro':
            return self._create_simple_intro_visual(step, step_number)
        elif step_type == 'overview':
            return self._create_simple_overview_visual(step, step_number)
        elif step_type == 'structure':
            return self._create_simple_structure_visual(step, step_number)
        elif step_type == 'code_analysis':
            return self._create_simple_code_analysis_visual(step, step_number)
        elif step_type == 'code_review':
            return self._create_simple_code_review_visual(step, step_number)
        elif step_type == 'error_simulation':
            return self._create_simple_error_simulation_visual(step, step_number)
        elif step_type == 'summary':
            return self._create_simple_summary_visual(step, step_number)
        else:
            return self._create_simple_generic_visual(step, step_number)
    
    def _create_simple_intro_visual(self, step: Dict, step_number: int) -> VideoFileClip:
        """Create simple introduction visual."""
        # Create background with different color for intro
        background = ColorClip(size=self.resolution, color=(50, 100, 150), duration=20)  # Blue
        return background
    
    def _create_simple_overview_visual(self, step: Dict, step_number: int) -> VideoFileClip:
        """Create simple overview visual."""
        # Create background with different color for overview
        background = ColorClip(size=self.resolution, color=(100, 50, 150), duration=25)  # Purple
        return background
    
    def _create_simple_structure_visual(self, step: Dict, step_number: int) -> VideoFileClip:
        """Create simple structure visual."""
        # Create background with different color for structure
        background = ColorClip(size=self.resolution, color=(150, 100, 50), duration=30)  # Orange
        return background
    
    def _create_simple_code_analysis_visual(self, step: Dict, step_number: int) -> VideoFileClip:
        """Create simple code analysis visual."""
        # Create background with different color for code analysis
        background = ColorClip(size=self.resolution, color=(100, 150, 50), duration=35)  # Green
        return background
    
    def _create_simple_code_review_visual(self, step: Dict, step_number: int) -> VideoFileClip:
        """Create simple code review visual."""
        # Create background with different color for code review
        background = ColorClip(size=self.resolution, color=(150, 50, 100), duration=25)  # Pink
        return background
    
    def _create_simple_error_simulation_visual(self, step: Dict, step_number: int) -> VideoFileClip:
        """Create simple error simulation visual."""
        # Create background with different color for error simulation
        background = ColorClip(size=self.resolution, color=(150, 50, 50), duration=40)  # Red
        return background
    
    def _create_simple_summary_visual(self, step: Dict, step_number: int) -> VideoFileClip:
        """Create simple summary visual."""
        # Create background with different color for summary
        background = ColorClip(size=self.resolution, color=(50, 150, 100), duration=30)  # Teal
        return background
    
    def _create_simple_error_visual(self, error_message: str) -> VideoFileClip:
        """Create simple error visual for failed steps."""
        # Create background with error color
        background = ColorClip(size=self.resolution, color=(100, 25, 25), duration=10)  # Dark red
        return background

    def _create_simple_generic_visual(self, step: Dict, step_number: int) -> VideoFileClip:
        """Create simple generic visual for unknown step types."""
        # Create background with default color
        background = ColorClip(size=self.resolution, color=self.background_color, duration=30)
        return background
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up temp directory: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup() 