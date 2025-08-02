"""
Advanced Animation System

A modular system for creating 3Blue1Brown-style educational animations
from code repositories using ManimGL and AI-powered storyboarding.
"""

import logging
import os
from typing import Dict, List, Any, Optional
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import main components
from .core.data_structures import (
    Storyboard, StoryboardScene, VisualElement, 
    AnimationStep, CameraMovement, ExecutionState, ExecutionTrace
)
from .core.storyboard_generator import StoryboardGenerator
from .core.execution_capture import RuntimeStateCapture
from .visualizations.visual_metaphors import VisualMetaphorLibrary
from .rendering.manim_scene import AdvancedManimScene, ManimSceneRenderer
from .rendering.video_merger import VideoMerger

class AdvancedAnimationSystem:
    """Main orchestrator for the advanced animation system."""
    
    def __init__(self, openai_api_key: Optional[str] = None, output_dir: str = "advanced_output"):
        """
        Initialize the advanced animation system.
        
        Args:
            openai_api_key: OpenAI API key for GPT-4 storyboard generation
            output_dir: Directory for output files
        """
        self.output_dir = output_dir
        self.storyboard_generator = StoryboardGenerator(openai_api_key)
        self.execution_capture = RuntimeStateCapture()
        self.scene_renderer = ManimSceneRenderer(output_dir)
        self.video_merger = VideoMerger(output_dir)
        self.visual_library = VisualMetaphorLibrary()
        
        logger.info("AdvancedAnimationSystem initialized")
    
    def create_animation_from_code(self, code_analysis: Dict[str, Any], 
                                 capture_execution: bool = True) -> str:
        """
        Create a complete animation from code analysis.
        
        Args:
            code_analysis: Code analysis results
            capture_execution: Whether to capture runtime execution
            
        Returns:
            Path to the final video file
        """
        try:
            logger.info("Starting animation creation from code analysis")
            
            # Generate storyboard
            storyboard = self.storyboard_generator.generate_storyboard(code_analysis)
            logger.info(f"Generated storyboard with {len(storyboard.scenes)} scenes")
            
            # Capture execution traces if requested
            if capture_execution:
                self._add_execution_traces_to_storyboard(storyboard, code_analysis)
            
            # Render all scenes
            video_files = []
            for scene in storyboard.scenes:
                video_file = self.scene_renderer.render_scene(scene)
                video_files.append(video_file)
                logger.info(f"Rendered scene {scene.id}: {video_file}")
            
            # Combine videos (simplified - in practice you'd use MoviePy)
            final_video = self._combine_videos(video_files)
            
            logger.info(f"Animation creation completed: {final_video}")
            return final_video
            
        except Exception as e:
            logger.error(f"Error creating animation: {e}")
            raise
    
    def _add_execution_traces_to_storyboard(self, storyboard: Storyboard, 
                                          code_analysis: Dict[str, Any]):
        """Add execution traces to storyboard scenes."""
        try:
            for scene in storyboard.scenes:
                if scene.code_snippet:
                    # Capture execution for this code snippet
                    execution_trace = self.execution_capture.capture_execution(
                        scene.code_snippet, 
                        code_analysis.get('language', 'python')
                    )
                    scene.execution_state = {
                        'trace': execution_trace,
                        'captured_at': time.time()
                    }
                    logger.info(f"Added execution trace to scene {scene.id}")
                    
        except Exception as e:
            logger.error(f"Error adding execution traces: {e}")
    
    def _combine_videos(self, video_files: List[str]) -> str:
        """Combine multiple video files into one using VideoMerger."""
        try:
            if not video_files:
                logger.warning("No video files to combine")
                return ""
            
            # Use the video merger to combine all scenes
            final_video_path = self.video_merger.merge_scenes(video_files)
            
            if final_video_path:
                logger.info(f"Successfully combined {len(video_files)} videos into: {final_video_path}")
                return final_video_path
            else:
                logger.error("Failed to combine videos")
                return video_files[0] if video_files else ""
                
        except Exception as e:
            logger.error(f"Error combining videos: {e}")
            return video_files[0] if video_files else ""
    
    def save_storyboard(self, storyboard: Storyboard, filename: str = "storyboard.json") -> str:
        """Save storyboard to file."""
        try:
            output_path = f"{self.output_dir}/{filename}"
            return self.storyboard_generator.save_storyboard(storyboard, output_path)
        except Exception as e:
            logger.error(f"Error saving storyboard: {e}")
            raise
    
    def load_storyboard(self, filepath: str) -> Storyboard:
        """Load storyboard from file."""
        try:
            return self.storyboard_generator.load_storyboard(filepath)
        except Exception as e:
            logger.error(f"Error loading storyboard: {e}")
            raise

# Convenience functions
def create_animation(code_analysis: Dict[str, Any], 
                   openai_api_key: Optional[str] = None,
                   output_dir: str = "advanced_output") -> str:
    """
    Convenience function to create an animation from code analysis.
    
    Args:
        code_analysis: Code analysis results
        openai_api_key: OpenAI API key for GPT-4
        output_dir: Output directory
        
    Returns:
        Path to the generated video file
    """
    system = AdvancedAnimationSystem(openai_api_key, output_dir)
    return system.create_animation_from_code(code_analysis)

def generate_storyboard(code_analysis: Dict[str, Any], 
                       openai_api_key: Optional[str] = None) -> Storyboard:
    """
    Convenience function to generate a storyboard from code analysis.
    
    Args:
        code_analysis: Code analysis results
        openai_api_key: OpenAI API key for GPT-4
        
    Returns:
        Storyboard object
    """
    generator = StoryboardGenerator(openai_api_key)
    return generator.generate_storyboard(code_analysis)

def capture_execution(code_content: str, language: str = "python") -> ExecutionTrace:
    """
    Convenience function to capture execution trace.
    
    Args:
        code_content: Source code to execute
        language: Programming language
        
    Returns:
        ExecutionTrace object
    """
    capture = RuntimeStateCapture()
    return capture.capture_execution(code_content, language)

# Version info
__version__ = "1.0.0"
__author__ = "Advanced Animation System"
__description__ = "3Blue1Brown-style educational animations from code repositories"

logger.info(f"Advanced Animation System v{__version__} loaded successfully") 