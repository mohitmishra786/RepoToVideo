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
    VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip,
    ColorClip, concatenate_videoclips
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
        
    def create_step_visualization(self, step: Dict, step_number: int) -> str:
        """
        Create a visual representation of the step using matplotlib.
        
        Args:
            step: Step information
            step_number: Step number
            
        Returns:
            Path to the generated image
        """
        try:
            fig, ax = plt.subplots(figsize=(16, 9))
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')
            
            # Title
            ax.text(0.5, 0.95, step['title'], fontsize=24, color='white', 
                    ha='center', va='top', weight='bold', transform=ax.transAxes)
            
            step_type = step.get('type', 'generic')
            content = step.get('content', {})
            
            if step_type == 'intro':
                # Introduction slide
                repo_name = content.get('repo_name', 'Repository')
                owner = content.get('owner', 'Unknown')
                ax.text(0.5, 0.7, f"Repository: {repo_name}", fontsize=20, color='white', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.text(0.5, 0.6, f"Owner: {owner}", fontsize=18, color='lightblue', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.text(0.5, 0.5, "RepoToVideo Walkthrough", fontsize=16, color='lightgray', 
                       ha='center', va='center', transform=ax.transAxes)
                        
            elif step_type == 'overview':
                # Overview slide
                ax.text(0.5, 0.7, "Repository Overview", fontsize=20, color='white', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.text(0.5, 0.6, "Understanding the project structure", fontsize=16, color='lightgray', 
                       ha='center', va='center', transform=ax.transAxes)
                        
            elif step_type == 'structure':
                # Structure slide
                ax.text(0.5, 0.7, "Repository Structure", fontsize=20, color='white', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.text(0.5, 0.6, "Analyzing file organization", fontsize=16, color='lightgray', 
                       ha='center', va='center', transform=ax.transAxes)
                        
            elif step_type == 'code_review':
                # Code review slide
                filename = content.get('filename', 'Code')
                ax.text(0.5, 0.7, f"Examining {filename}", fontsize=20, color='white', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.text(0.5, 0.6, "Code analysis and review", fontsize=16, color='lightgray', 
                       ha='center', va='center', transform=ax.transAxes)
                        
            elif step_type == 'error_simulation':
                # Error simulation slide
                ax.text(0.5, 0.7, "Error Handling and Debugging", fontsize=20, color='white', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.text(0.5, 0.6, "Common programming errors and solutions", fontsize=16, color='lightgray', 
                       ha='center', va='center', transform=ax.transAxes)
                           
            elif step_type == 'summary':
                # Summary slide
                ax.text(0.5, 0.7, "Summary and Key Takeaways", fontsize=20, color='white', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.text(0.5, 0.6, "What we've learned from this repository", fontsize=16, color='lightgray', 
                       ha='center', va='center', transform=ax.transAxes)
            
            else:
                # Generic slide
                ax.text(0.5, 0.7, step.get('title', 'Analysis'), fontsize=20, color='white', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.text(0.5, 0.6, "Step-by-step analysis", fontsize=16, color='lightgray', 
                       ha='center', va='center', transform=ax.transAxes)
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Save image
            image_path = os.path.join(self.temp_dir, f"step_{step_number}.png")
            plt.savefig(image_path, dpi=150, bbox_inches='tight', 
                       facecolor='#1e1e1e', edgecolor='none')
            plt.close()
            
            return image_path
            
        except Exception as e:
            print(f"Warning: Error creating visualization for step {step_number}: {str(e)}")
            # Create a simple fallback image
            try:
                fig, ax = plt.subplots(figsize=(16, 9))
                fig.patch.set_facecolor('#1e1e1e')
                ax.set_facecolor('#1e1e1e')
                ax.text(0.5, 0.5, f"Step {step_number + 1}: {step.get('title', 'Unknown')}", 
                       fontsize=24, color='white', ha='center', va='center', transform=ax.transAxes)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                
                image_path = os.path.join(self.temp_dir, f"step_{step_number}_fallback.png")
                plt.savefig(image_path, dpi=150, bbox_inches='tight', 
                           facecolor='#1e1e1e', edgecolor='none')
                plt.close()
                return image_path
            except:
                # Ultimate fallback - create a simple file
                image_path = os.path.join(self.temp_dir, f"step_{step_number}_simple.png")
                img = Image.new('RGB', (1920, 1080), color=(30, 30, 30))
                img.save(image_path)
                return image_path
    
    def create_video_clip(self, image_path: str, audio_path: Optional[str], duration: float):
        """
        Create a video clip from image and audio.
        
        Args:
            image_path: Path to the image
            audio_path: Path to the audio file (optional)
            duration: Duration of the clip
            
        Returns:
            VideoFileClip object
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Creating video clip from image: {image_path}")
            logger.info(f"Audio path: {audio_path}")
            logger.info(f"Duration: {duration}")
            
            # Create video from image
            video_clip = ImageClip(image_path, duration=duration)
            logger.info(f"ImageClip created successfully, type: {type(video_clip)}")
            logger.info(f"ImageClip methods: {[method for method in dir(video_clip) if not method.startswith('_')]}")
            
            # Add audio if available
            if audio_path and os.path.exists(audio_path):
                logger.info(f"Audio file exists, attempting to add audio")
                try:
                    audio_clip = AudioFileClip(audio_path)
                    logger.info(f"AudioClip created successfully, duration: {audio_clip.duration}")
                    
                    # Adjust duration to match audio if needed
                    if audio_clip.duration > duration:
                        duration = min(audio_clip.duration, 30 * 2)
                        video_clip = video_clip.set_duration(duration)
                        logger.info(f"Adjusted duration to: {duration}")
                    
                    # Try different methods to add audio
                    logger.info("Attempting Method 1: with_audio")
                    try:
                        # Method 1: Use with_audio (correct method name)
                        video_clip = video_clip.with_audio(audio_clip)
                        logger.info("Method 1 successful: with_audio worked")
                    except Exception as e:
                        logger.warning(f"Method 1 failed: {str(e)}")
                        logger.info("Attempting Method 2: CompositeVideoClip with with_audio")
                        try:
                            # Method 2: Use CompositeVideoClip with with_audio
                            video_clip = CompositeVideoClip([video_clip]).with_audio(audio_clip)
                            logger.info("Method 2 successful: CompositeVideoClip with with_audio worked")
                        except Exception as e2:
                            logger.warning(f"Method 2 failed: {str(e2)}")
                            logger.info("Attempting Method 3: Create new ImageClip with with_audio")
                            try:
                                # Method 3: Create new clip with audio
                                video_clip = ImageClip(image_path, duration=duration).with_audio(audio_clip)
                                logger.info("Method 3 successful: New ImageClip with with_audio worked")
                            except Exception as e3:
                                logger.error(f"Method 3 failed: {str(e3)}")
                                logger.info("All audio methods failed, continuing without audio")
                                
                except Exception as e:
                    logger.error(f"Error creating AudioClip: {str(e)}")
                    logger.info("Continuing without audio")
            else:
                logger.info("No audio file provided or file doesn't exist")
            
            logger.info(f"Final video clip type: {type(video_clip)}")
            return video_clip
            
        except Exception as e:
            # Fallback: create a simple colored clip if image fails
            logger.error(f"Error creating video from image: {str(e)}")
            logger.info("Creating fallback ColorClip")
            return ColorClip(size=self.resolution, color=(30, 30, 30), duration=duration)
        
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
                    # Get corresponding audio
                    audio_clip = None
                    if i < len(audio_files) and audio_files[i]:
                        try:
                            logger.info(f"Loading audio file: {audio_files[i]}")
                            audio_clip = AudioFileClip(audio_files[i])
                            logger.info(f"Audio clip loaded for step {i+1}, duration: {audio_clip.duration}")
                        except Exception as e:
                            logger.error(f"Error loading audio file {audio_files[i]}: {str(e)}")
                    
                    # Create visualization
                    image_path = self.create_step_visualization(step, i)
                    logger.info(f"Visualization created for step {i+1}")
                    
                    # Determine duration
                    if audio_clip:
                        duration = max(audio_clip.duration, 5)  # Minimum 5 seconds
                        audio_clip.close()  # Close to free memory
                    else:
                        duration = 10  # Default duration
                    
                    # Create video clip
                    clip = self.create_video_clip(image_path, audio_files[i] if i < len(audio_files) else None, duration)
                    video_clips.append(clip)
                    logger.info(f"Step {i+1} clip added to video clips list")
                    
                except Exception as e:
                    logger.error(f"Error creating visual for step {i+1}: {str(e)}")
                    import traceback
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                    # Create a simple error clip instead
                    fallback_clip = ColorClip(size=self.resolution, color=(100, 25, 25), duration=10)
                    video_clips.append(fallback_clip)
            
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
                
    def cleanup(self):
        """Clean up temporary files."""
        try:
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Warning: Could not clean up temp directory: {str(e)}")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.cleanup() 