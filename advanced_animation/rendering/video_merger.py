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
    
"""
    Performs __init__ operation. Function has side effects. Takes self and output_dir as input. Returns a object value.
    :param self: The self object.
    :param output_dir: The output_dir string.
    :return: Value of type object
"""
    def __init__(self, output_dir: str = "final_video"):
        """
        Initialize the video merger.
        
        Args:
            output_dir: Directory for final video output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"VideoMerger initialized with output directory: {output_dir}")
    
"""
    Merges the scenes based on self, video_files, storyboard_path. Function iterates over data, conditionally processes input, may return early, has side effects, performs arithmetic operations. Takes self, video_files and storyboard_path as input. Returns a string value.
    :param self: The self object.
    :param video_files: The video_files value of type List[str].
    :param storyboard_path: The storyboard_path value of type Optional[str].
    :return: String value
"""
    def merge_scenes(self, video_files: List[str], storyboard_path: Optional[str] = None) -> str:
        """
        Merge multiple scene videos into a single comprehensive video with audio.
        
        Args:
            video_files: List of paths to scene video files
            storyboard_path: Optional path to storyboard JSON for metadata
            
        Returns:
            Path to the merged video file
        """
        try:
            if not MOVIEPY_AVAILABLE:
                logger.error("MoviePy not available for video merging")
                return self.create_fallback_merge_with_audio(video_files)
            
            logger.info(f"Merging {len(video_files)} scene videos with audio")
            
            # Load storyboard metadata if available
            metadata = self.load_storyboard_metadata(storyboard_path) if storyboard_path else {}
            
            # Create video clips with audio
            clips = []
            audio_files = []
            
            for i, video_file in enumerate(video_files):
                if Path(video_file).exists():
                    # Load video clip
                    clip = VideoFileClip(video_file)
                    
                    # Look for corresponding audio file
                    video_path = Path(video_file)
                    # Audio files are in the main output directory, not in the video subdirectories
                    audio_file = self.output_dir / f"scene_{i+1}_narration.mp3"
                    
                    if audio_file.exists():
                        logger.info(f"Found audio file for scene {i+1}: {audio_file}")
                        # Load audio and set it to the video clip
                        audio_clip = mpy.AudioFileClip(str(audio_file))
                        clip = clip.set_audio(audio_clip)
                    else:
                        logger.warning(f"No audio file found for scene {i+1}: {audio_file}")
                    
                    clips.append(clip)
                    logger.info(f"Added scene {i+1}: {video_file}")
                else:
                    logger.warning(f"Video file not found: {video_file}")
            
            if not clips:
                logger.error("No valid video clips found")
                return self.create_fallback_merge_with_audio(video_files)
            
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
            
            logger.info(f"Successfully merged videos with audio to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error merging videos: {e}")
            return self.create_fallback_merge_with_audio(video_files)
    
"""
    Loads the storyboard based on self, storyboard_path. Function may return early, has side effects, performs file operations. Takes self and storyboard_path as input. Returns a dictionary of values.
    :param self: The self object.
    :param storyboard_path: The storyboard_path string.
    :return: Dictionary of values
"""
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
    
"""
    Adds the title to the collection. Function may return early, has side effects. Takes self, video_clip and metadata as input. Returns a object value.
    :param self: The self object.
    :param video_clip: The video_clip object.
    :param metadata: The metadata dictionary.
    :return: Value of type object
"""
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
    
"""
    Creates a new fallback instance. Function iterates over data, conditionally processes input, may return early, has side effects, performs arithmetic operations, performs file operations. Takes self and video_files as input. Returns a string value.
    :param self: The self object.
    :param video_files: The video_files value of type List[str].
    :return: String value
"""
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

"""
    Creates a new fallback instance. Function iterates over data, conditionally processes input, may return early, has side effects, performs arithmetic operations, performs file operations. Takes self and video_files as input. Returns a string value.
    :param self: The self object.
    :param video_files: The video_files value of type List[str].
    :return: String value
"""
    def create_fallback_merge_with_audio(self, video_files: List[str]) -> str:
        """Create a fallback merged video with audio using ffmpeg."""
        try:
            # Create a file list for ffmpeg
            file_list_path = self.output_dir / "video_list.txt"
            audio_list_path = self.output_dir / "audio_list.txt"
            
            with open(file_list_path, 'w') as f:
                for video_file in video_files:
                    video_path = Path(video_file)
                    if video_path.exists():
                        # Use absolute path to avoid path issues
                        f.write(f"file '{video_path.absolute()}'\n")
                    else:
                        logger.warning(f"Video file not found: {video_file}")
            
            # Create audio list
            with open(audio_list_path, 'w') as f:
                for i, video_file in enumerate(video_files):
                    # Audio files are in the main output directory
                    audio_file = self.output_dir / f"scene_{i+1}_narration.mp3"
                    if audio_file.exists():
                        f.write(f"file '{audio_file.absolute()}'\n")
                        logger.info(f"Found audio file for scene {i+1}: {audio_file}")
                    else:
                        logger.warning(f"No audio file found for scene {i+1}: {audio_file}")
            
            # Use ffmpeg to concatenate videos and audio separately, then combine
            temp_video_path = self.output_dir / "temp_video.mp4"
            temp_audio_path = self.output_dir / "temp_audio.mp3"
            output_path = self.output_dir / "final_comprehensive_analysis.mp4"
            
            # First concatenate videos
            video_cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(file_list_path),
                '-c', 'copy',
                str(temp_video_path),
                '-y'
            ]
            
            result = subprocess.run(video_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Video concatenation failed: {result.stderr}")
                return self.create_fallback_merge(video_files)  # Fall back to video-only
            
            # Then concatenate audio files
            audio_cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(audio_list_path),
                '-c', 'copy',
                str(temp_audio_path),
                '-y'
            ]
            
            result = subprocess.run(audio_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Audio concatenation failed: {result.stderr}")
                # If audio fails, just use the video
                temp_video_path.rename(output_path)
                return str(output_path)
            
            # Finally combine video and audio
            combine_cmd = [
                'ffmpeg',
                '-i', str(temp_video_path),
                '-i', str(temp_audio_path),
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                str(output_path),
                '-y'
            ]
            
            result = subprocess.run(combine_cmd, capture_output=True, text=True)
            
            # Clean up temp files
            if temp_video_path.exists():
                temp_video_path.unlink()
            if temp_audio_path.exists():
                temp_audio_path.unlink()
            
            if result.returncode == 0:
                logger.info(f"Fallback merge with audio successful: {output_path}")
                return str(output_path)
            else:
                logger.error(f"Audio-video combination failed: {result.stderr}")
                # If combination fails, just use the video
                if temp_video_path.exists():
                    temp_video_path.rename(output_path)
                    return str(output_path)
                return ""
                
        except Exception as e:
            logger.error(f"Error in fallback merge with audio: {e}")
            return self.create_fallback_merge(video_files)  # Fall back to video-only
    
"""
    Creates a new scene instance. Function iterates over data, conditionally processes input, may return early, has side effects, performs arithmetic operations. Takes self and clips as input. Returns a list of values.
    :param self: The self object.
    :param clips: The clips list.
    :return: List of values
"""
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