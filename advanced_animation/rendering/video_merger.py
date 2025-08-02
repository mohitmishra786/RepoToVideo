"""
Video Merger Module for Advanced Animation System

This module handles merging multiple scene videos into a single comprehensive video.
"""

import logging
from pathlib import Path
from typing import List, Optional
import subprocess
import json

logger = logging.getLogger(__name__)

try:
    import moviepy.editor as mpy
    from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logger.warning("MoviePy not available for video merging")

class VideoMerger:
    """Merges multiple scene videos into a single comprehensive video."""
    
    def __init__(self, output_dir: str = "final_video"):
        """
        Initialize the video merger.
        
        Args:
            output_dir: Directory for final video output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"VideoMerger initialized with output directory: {output_dir}")
    
    def merge_scenes(self, video_files: List[str], storyboard_path: Optional[str] = None) -> str:
        """
        Merge multiple scene videos into a single comprehensive video.
        
        Args:
            video_files: List of paths to scene video files
            storyboard_path: Optional path to storyboard JSON for metadata
            
        Returns:
            Path to the merged video file
        """
        try:
            if not MOVIEPY_AVAILABLE:
                logger.error("MoviePy not available for video merging")
                return self.create_fallback_merge(video_files)
            
            logger.info(f"Merging {len(video_files)} scene videos")
            
            # Load storyboard metadata if available
            metadata = self.load_storyboard_metadata(storyboard_path) if storyboard_path else {}
            
            # Create video clips
            clips = []
            for i, video_file in enumerate(video_files):
                if Path(video_file).exists():
                    clip = VideoFileClip(video_file)
                    clips.append(clip)
                    logger.info(f"Added scene {i+1}: {video_file}")
                else:
                    logger.warning(f"Video file not found: {video_file}")
            
            if not clips:
                logger.error("No valid video clips found")
                return self.create_fallback_merge(video_files)
            
            # Concatenate clips
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Add title and metadata
            final_video = self.add_title_and_metadata(final_video, metadata)
            
            # Save the merged video
            output_path = self.output_dir / "final_comprehensive_analysis.mp4"
            final_video.write_videofile(
                str(output_path),
                fps=24,
                codec='libx264',
                audio_codec='aac'
            )
            
            # Clean up
            for clip in clips:
                clip.close()
            final_video.close()
            
            logger.info(f"Successfully merged videos to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error merging videos: {e}")
            return self.create_fallback_merge(video_files)
    
    def load_storyboard_metadata(self, storyboard_path: str) -> dict:
        """Load metadata from storyboard JSON file."""
        try:
            with open(storyboard_path, 'r') as f:
                storyboard = json.load(f)
            
            return {
                'title': storyboard.get('title', 'Code Repository Analysis'),
                'description': storyboard.get('description', ''),
                'total_duration': storyboard.get('total_duration', 0),
                'scene_count': len(storyboard.get('scenes', []))
            }
        except Exception as e:
            logger.error(f"Error loading storyboard metadata: {e}")
            return {}
    
    def add_title_and_metadata(self, video_clip, metadata: dict):
        """Add title and metadata overlay to the video."""
        try:
            # Create title text
            title = metadata.get('title', 'Code Repository Analysis')
            title_clip = TextClip(
                title,
                fontsize=48,
                color='white',
                font='Arial-Bold'
            ).set_position(('center', 50)).set_duration(3)
            
            # Create subtitle with metadata
            subtitle_text = f"Duration: {metadata.get('total_duration', 0):.1f}s | Scenes: {metadata.get('scene_count', 0)}"
            subtitle_clip = TextClip(
                subtitle_text,
                fontsize=24,
                color='gray',
                font='Arial'
            ).set_position(('center', 100)).set_duration(3)
            
            # Composite the video
            final_clip = CompositeVideoClip([video_clip, title_clip, subtitle_clip])
            
            return final_clip
            
        except Exception as e:
            logger.error(f"Error adding title and metadata: {e}")
            return video_clip
    
    def create_fallback_merge(self, video_files: List[str]) -> str:
        """Create a fallback merged video using ffmpeg."""
        try:
            # Create a file list for ffmpeg
            file_list_path = self.output_dir / "video_list.txt"
            with open(file_list_path, 'w') as f:
                for video_file in video_files:
                    video_path = Path(video_file)
                    if video_path.exists():
                        # Use absolute path to avoid path issues
                        f.write(f"file '{video_path.absolute()}'\n")
                    else:
                        logger.warning(f"Video file not found: {video_file}")
            
            # Use ffmpeg to concatenate
            output_path = self.output_dir / "final_comprehensive_analysis.mp4"
            
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(file_list_path),
                '-c', 'copy',
                str(output_path),
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Fallback merge successful: {output_path}")
                return str(output_path)
            else:
                logger.error(f"Fallback merge failed: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"Error in fallback merge: {e}")
            return ""
    
    def create_scene_transitions(self, clips: List) -> List:
        """Add smooth transitions between scenes."""
        try:
            transitioned_clips = []
            
            for i, clip in enumerate(clips):
                # Add fade in/out effects
                if i == 0:  # First clip
                    clip = clip.fadein(0.5)
                if i == len(clips) - 1:  # Last clip
                    clip = clip.fadeout(0.5)
                else:  # Middle clips
                    clip = clip.fadein(0.3).fadeout(0.3)
                
                transitioned_clips.append(clip)
            
            return transitioned_clips
            
        except Exception as e:
            logger.error(f"Error creating transitions: {e}")
            return clips 