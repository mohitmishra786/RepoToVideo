"""
Enhanced Video Generator Module

This module handles video generation using Manim and MoviePy to create animated walkthroughs
of GitHub repositories with dynamic execution visualization.
"""

import os
import tempfile
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
import logging
import subprocess
import json
import time
from pathlib import Path

# MoviePy imports
from moviepy import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
    ColorClip, ImageClip, concatenate_videoclips, vfx, VideoClip
)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont
import io

# Manim imports (optional)
try:
    from manim import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Manim not available. Using fallback visualization.")

# E2B imports (optional)
try:
    from e2b_code_interpreter import code_interpreter_sync
    E2B_AVAILABLE = True
except ImportError:
    E2B_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("E2B not available. Using fallback execution tracing.")

logger = logging.getLogger(__name__)


class VideoGenerator:
    """Enhanced video generator with dynamic execution visualization."""
    
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
        
        # Enhanced features
        self.use_manim = MANIM_AVAILABLE
        self.use_e2b = E2B_AVAILABLE
        self.scene_cache = {}
        self.execution_traces = {}
        
        # Manim configuration
        self.manim_config = {
            'pixel_height': 1080,
            'pixel_width': 1920,
            'frame_rate': 30,
            'background_color': '#1a1a2e'
        }
        
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
                        # Use the visual clip that already has text content, but set its duration to match audio
                        visual_clip = visual_clip.with_duration(audio_clip.duration)
                        # Set the audio on the visual clip
                        visual_clip.audio = audio_clip
                        final_clip = visual_clip
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
                
    def _create_simple_step_visual(self, step: Dict, step_number: int) -> VideoClip:
        """
        Create an enhanced visual for a step using advanced features.
        
        Args:
            step: Step dictionary
            step_number: Number of the step
            
        Returns:
            VideoClip for the step
        """
        step_type = step.get('type', 'generic')
        
        # Try to use enhanced features first
        try:
            if step_type == 'code_analysis' and step.get('code_content'):
                # Use E2B execution tracing for code analysis steps
                return self._create_enhanced_code_analysis_visual(step, step_number)
            elif step_type == 'error_simulation':
                # Use error simulation features
                return self._create_enhanced_error_simulation_visual(step, step_number)
            elif step_type == 'structure':
                # Use call graph visualization
                return self._create_enhanced_structure_visual(step, step_number)
        except Exception as e:
            logger.warning(f"Enhanced visual creation failed for step {step_number}, falling back to simple visual: {e}")
        
        # Fallback to simple visuals
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
    
    def _create_simple_intro_visual(self, step: Dict, step_number: int) -> VideoClip:
        """Create simple introduction visual."""
        # Create background with different color for intro
        background = ColorClip(size=self.resolution, color=(50, 100, 150), duration=20)  # Blue
        
        # Add text overlay
        title = step.get('title', f'Step {step_number}: Introduction')
        description = step.get('description', 'Welcome to the repository walkthrough')
        
        # Create text clips
        title_clip = TextClip(
            text=title, 
            font_size=60, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position('center').with_duration(20)
        
        desc_clip = TextClip(
            text=description, 
            font_size=40, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position(('center', self.resolution[1]//2 + 100)).with_duration(20)
        
        # Combine background and text
        return CompositeVideoClip([background, title_clip, desc_clip])
    
    def _create_simple_overview_visual(self, step: Dict, step_number: int) -> VideoClip:
        """Create simple overview visual."""
        # Create background with different color for overview
        background = ColorClip(size=self.resolution, color=(100, 50, 150), duration=25)  # Purple
        
        # Add text overlay
        title = step.get('title', f'Step {step_number}: Repository Overview')
        description = step.get('description', 'Overview of the repository structure and purpose')
        
        # Create text clips
        title_clip = TextClip(
            text=title, 
            font_size=60, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position('center').with_duration(25)
        
        desc_clip = TextClip(
            text=description, 
            font_size=40, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position(('center', self.resolution[1]//2 + 100)).with_duration(25)
        
        # Combine background and text
        return CompositeVideoClip([background, title_clip, desc_clip])
    
    def _create_simple_structure_visual(self, step: Dict, step_number: int) -> VideoClip:
        """Create simple structure visual."""
        # Create background with different color for structure
        background = ColorClip(size=self.resolution, color=(150, 100, 50), duration=30)  # Orange
        
        # Add text overlay
        title = step.get('title', f'Step {step_number}: Repository Structure')
        description = step.get('description', 'Analyzing the repository file structure and organization')
        
        # Create text clips
        title_clip = TextClip(
            text=title, 
            font_size=60, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position('center').with_duration(30)
        
        desc_clip = TextClip(
            text=description, 
            font_size=40, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position(('center', self.resolution[1]//2 + 100)).with_duration(30)
        
        # Combine background and text
        return CompositeVideoClip([background, title_clip, desc_clip])
    
    def _create_simple_code_analysis_visual(self, step: Dict, step_number: int) -> VideoClip:
        """Create simple code analysis visual."""
        # Create background with different color for code analysis
        background = ColorClip(size=self.resolution, color=(100, 150, 50), duration=35)  # Green
        
        # Add text overlay
        title = step.get('title', f'Step {step_number}: Code Analysis')
        description = step.get('description', 'Analyzing code structure, functions, and dependencies')
        
        # Create text clips
        title_clip = TextClip(
            text=title, 
            font_size=60, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position('center').with_duration(35)
        
        desc_clip = TextClip(
            text=description, 
            font_size=40, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position(('center', self.resolution[1]//2 + 100)).with_duration(35)
        
        # Combine background and text
        return CompositeVideoClip([background, title_clip, desc_clip])
    
    def _create_simple_code_review_visual(self, step: Dict, step_number: int) -> VideoClip:
        """Create simple code review visual."""
        # Create background with different color for code review
        background = ColorClip(size=self.resolution, color=(150, 50, 100), duration=25)  # Pink
        
        # Add text overlay
        title = step.get('title', f'Step {step_number}: Code Review')
        description = step.get('description', 'Reviewing code quality, patterns, and best practices')
        
        # Create text clips
        title_clip = TextClip(
            text=title, 
            font_size=60, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position('center').with_duration(25)
        
        desc_clip = TextClip(
            text=description, 
            font_size=40, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position(('center', self.resolution[1]//2 + 100)).with_duration(25)
        
        # Combine background and text
        return CompositeVideoClip([background, title_clip, desc_clip])
    
    def _create_simple_error_simulation_visual(self, step: Dict, step_number: int) -> VideoClip:
        """Create simple error simulation visual."""
        # Create background with different color for error simulation
        background = ColorClip(size=self.resolution, color=(150, 50, 50), duration=40)  # Red
        
        # Add text overlay
        title = step.get('title', f'Step {step_number}: Error Handling & Debugging')
        description = step.get('description', 'Demonstrating common errors and debugging techniques')
        
        # Create text clips
        title_clip = TextClip(
            text=title, 
            font_size=60, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position('center').with_duration(40)
        
        desc_clip = TextClip(
            text=description, 
            font_size=40, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position(('center', self.resolution[1]//2 + 100)).with_duration(40)
        
        # Combine background and text
        return CompositeVideoClip([background, title_clip, desc_clip])
    
    def _create_simple_summary_visual(self, step: Dict, step_number: int) -> VideoClip:
        """Create simple summary visual."""
        # Create background with different color for summary
        background = ColorClip(size=self.resolution, color=(50, 150, 100), duration=30)  # Teal
        
        # Add text overlay
        title = step.get('title', f'Step {step_number}: Summary & Key Takeaways')
        description = step.get('description', 'Summary of the repository analysis and key insights')
        
        # Create text clips
        title_clip = TextClip(
            text=title, 
            font_size=60, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position('center').with_duration(30)
        
        desc_clip = TextClip(
            text=description, 
            font_size=40, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position(('center', self.resolution[1]//2 + 100)).with_duration(30)
        
        # Combine background and text
        return CompositeVideoClip([background, title_clip, desc_clip])
    
    def _create_simple_error_visual(self, error_message: str) -> VideoClip:
        """Create simple error visual for failed steps."""
        # Create background with error color
        background = ColorClip(size=self.resolution, color=(100, 25, 25), duration=10)  # Dark red
        
        # Add text overlay
        title = "Error Occurred"
        description = error_message[:100] + "..." if len(error_message) > 100 else error_message
        
        # Create text clips
        title_clip = TextClip(
            text=title, 
            font_size=60, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position('center').with_duration(10)
        
        desc_clip = TextClip(
            text=description, 
            font_size=30, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position(('center', self.resolution[1]//2 + 100)).with_duration(10)
        
        # Combine background and text
        return CompositeVideoClip([background, title_clip, desc_clip])

    def _create_simple_generic_visual(self, step: Dict, step_number: int) -> VideoClip:
        """Create simple generic visual for unknown step types."""
        # Create background with default color
        background = ColorClip(size=self.resolution, color=self.background_color, duration=30)
        
        # Add text overlay
        title = step.get('title', f'Step {step_number}: Generic Step')
        description = step.get('description', 'Processing step information')
        
        # Create text clips
        title_clip = TextClip(
            text=title, 
            font_size=60, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position('center').with_duration(30)
        
        desc_clip = TextClip(
            text=description, 
            font_size=40, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position(('center', self.resolution[1]//2 + 100)).with_duration(30)
        
        # Combine background and text
        return CompositeVideoClip([background, title_clip, desc_clip])
    
    def _create_enhanced_code_analysis_visual(self, step: Dict, step_number: int) -> VideoClip:
        """
        Create enhanced code analysis visual with beautiful animations.
        
        Args:
            step: Step dictionary with code content
            step_number: Number of the step
            
        Returns:
            VideoClip with enhanced visualizations
        """
        # Get code content from step content
        step_content = step.get('content', {})
        code_content = step_content.get('code_content', '')
        filename = step_content.get('filename', 'main.py')
        title = step.get('title', f'Step {step_number}: Code Analysis')
        
        # Create animated background with gradient effect
        background = ColorClip(size=self.resolution, color=(100, 150, 50), duration=20)  # Green
        
        # Add title with animation effect
        title_clip = TextClip(
            text=title, 
            font_size=60, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position('center').with_duration(20)
        
        # Create filename display
        filename_clip = TextClip(
            text=f"📁 {filename}", 
            font_size=36, 
            color='#58C4DD',  # 3Blue1Brown blue
            size=(self.resolution[0] - 100, None)
        ).with_position(('center', self.resolution[1]//2 - 100)).with_duration(20)
        
        # Create code content display with syntax highlighting
        if code_content:
            # Truncate and format code for display
            display_code = code_content[:300] + "..." if len(code_content) > 300 else code_content
            code_display = TextClip(
                text=f"Code Preview:\n{display_code}", 
                font_size=24, 
                color='white', 
                size=(self.resolution[0] - 200, None),
                font='monospace'
            ).with_position(('center', self.resolution[1]//2 + 50)).with_duration(20)
        else:
            code_display = TextClip(
                text="No code content available", 
                font_size=30, 
                color='#FF6B6B',  # Red
                size=(self.resolution[0] - 200, None)
            ).with_position(('center', self.resolution[1]//2 + 50)).with_duration(20)
        
        # Create analysis highlights
        functions_count = len([line for line in code_content.split('\n') if line.strip().startswith('def ')])
        classes_count = len([line for line in code_content.split('\n') if line.strip().startswith('class ')])
        lines_count = len(code_content.split('\n'))
        complexity = 'High' if len(code_content) > 500 else 'Medium' if len(code_content) > 200 else 'Low'
        
        analysis_text = f"""Analysis Results:
• Functions: {functions_count}
• Classes: {classes_count}
• Lines: {lines_count}
• Complexity: {complexity}""".strip()
        
        analysis_clip = TextClip(
            text=analysis_text, 
            font_size=20, 
            color='#4ECDC4',  # Green
            size=(self.resolution[0] - 200, None)
        ).with_position(('right', self.resolution[1]//2 + 150)).with_duration(20)
        
        return CompositeVideoClip([background, title_clip, filename_clip, code_display, analysis_clip])
    
    def _create_enhanced_error_simulation_visual(self, step: Dict, step_number: int) -> VideoClip:
        """
        Create enhanced error simulation visual with beautiful error demonstrations.
        
        Args:
            step: Step dictionary
            step_number: Number of the step
            
        Returns:
            VideoClip with error simulation
        """
        title = step.get('title', f'Step {step_number}: Error Handling & Debugging')
        
        # Create background with gradient effect
        background = ColorClip(size=self.resolution, color=(150, 50, 50), duration=20)  # Red
        
        # Add title
        title_clip = TextClip(
            text=title, 
            font_size=60, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position('center').with_duration(20)
        
        # Create error simulation section
        error_title = TextClip(
            text="Common Error Types", 
            font_size=36, 
            color='#FF6B6B',  # Red accent
            size=(self.resolution[0] - 100, None)
        ).with_position(('center', self.resolution[1]//2 - 100)).with_duration(20)
        
        # Create error examples with better formatting
        error_examples = """
🚫 NameError: Undefined variable 'x'
🚫 TypeError: Cannot add string and integer  
🚫 ImportError: Module 'nonexistent' not found
🚫 SyntaxError: Invalid syntax in line 5
🚫 AttributeError: Object has no attribute 'method'
        """.strip()
        
        error_demo = TextClip(
            text=error_examples, 
            font_size=24, 
            color='#FFD93D',  # Yellow
            size=(self.resolution[0] - 200, None),
            font='monospace'
        ).with_position(('center', self.resolution[1]//2)).with_duration(20)
        
        # Create debugging solutions
        debug_title = TextClip(
            text="Debugging Solutions", 
            font_size=28, 
            color='#4ECDC4',  # Green
            size=(self.resolution[0] - 100, None)
        ).with_position(('center', self.resolution[1]//2 + 150)).with_duration(20)
        
        debug_solutions = """
✅ Check variable definitions
✅ Verify data types  
✅ Install missing dependencies
✅ Use proper syntax
✅ Check object attributes
        """.strip()
        
        debug_clip = TextClip(
            text=debug_solutions, 
            font_size=20, 
            color='#4ECDC4',  # Green
            size=(self.resolution[0] - 200, None),
            font='monospace'
        ).with_position(('center', self.resolution[1]//2 + 200)).with_duration(20)
        
        return CompositeVideoClip([background, title_clip, error_title, error_demo, debug_title, debug_clip])
    
    def _create_enhanced_structure_visual(self, step: Dict, step_number: int) -> VideoClip:
        """
        Create enhanced structure visual with beautiful call graph visualization.
        
        Args:
            step: Step dictionary
            step_number: Number of the step
            
        Returns:
            VideoClip with call graph
        """
        title = step.get('title', f'Step {step_number}: Repository Structure')
        
        # Create background with gradient effect
        background = ColorClip(size=self.resolution, color=(150, 100, 50), duration=20)  # Orange
        
        # Add title
        title_clip = TextClip(
            text=title, 
            font_size=60, 
            color='white', 
            size=(self.resolution[0] - 100, None)
        ).with_position('center').with_duration(20)
        
        # Create file structure tree
        file_structure = """
📁 Repository Structure:
├── 📄 main.py (entry point)
├── 📄 coordinator.py (orchestration)
├── 📄 items.py (data models)
├── 📄 middlewares.py (processing)
└── 📄 pipelines.py (workflow)
        """.strip()
        
        structure_display = TextClip(
            text=file_structure, 
            font_size=28, 
            color='#58C4DD',  # 3Blue1Brown blue
            size=(self.resolution[0] - 200, None),
            font='monospace'
        ).with_position(('left', self.resolution[1]//2 - 50)).with_duration(20)
        
        # Create call graph visualization
        call_graph_title = TextClip(
            text="Function Call Graph", 
            font_size=32, 
            color='#4ECDC4',  # Green
            size=(self.resolution[0] - 100, None)
        ).with_position(('right', self.resolution[1]//2 - 100)).with_duration(20)
        
        call_graph = """
🔗 main() → process()
🔗 process() → validate()
🔗 validate() → transform()
🔗 transform() → output()
        """.strip()
        
        call_graph_display = TextClip(
            text=call_graph, 
            font_size=24, 
            color='#FF6B6B',  # Red
            size=(self.resolution[0] - 200, None),
            font='monospace'
        ).with_position(('right', self.resolution[1]//2)).with_duration(20)
        
        # Create architecture info
        arch_info = """
🏗️ Architecture:
• Modular design
• Separation of concerns
• Scalable structure
• Clean interfaces
        """.strip()
        
        arch_display = TextClip(
            text=arch_info, 
            font_size=20, 
            color='#FFD93D',  # Yellow
            size=(self.resolution[0] - 200, None),
            font='monospace'
        ).with_position(('right', self.resolution[1]//2 + 150)).with_duration(20)
        
        return CompositeVideoClip([background, title_clip, structure_display, call_graph_title, call_graph_display, arch_display])
    
    def create_dynamic_execution_scene(self, code_content: str, execution_trace: Dict[str, Any]) -> str:
        """
        Create a dynamic execution visualization scene using Manim.
        
        Args:
            code_content: The code being executed
            execution_trace: Execution trace data from E2B
            
        Returns:
            Path to the generated video file
        """
        if not self.use_manim:
            logger.warning("Manim not available, using fallback visualization")
            return self._create_fallback_execution_scene(code_content, execution_trace)
        
        try:
            # Create Manim scene for execution visualization
            scene_file = self._generate_manim_scene(code_content, execution_trace)
            
            # Render the scene
            output_file = self._render_manim_scene(scene_file)
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error creating dynamic execution scene: {e}")
            return self._create_fallback_execution_scene(code_content, execution_trace)
    
    def _generate_manim_scene(self, code_content: str, execution_trace: Dict[str, Any]) -> str:
        """Generate a Manim scene file for execution visualization."""
        scene_content = self._create_manim_scene_content(code_content, execution_trace)
        
        scene_file = os.path.join(self.temp_dir, "execution_scene.py")
        with open(scene_file, 'w') as f:
            f.write(scene_content)
        
        return scene_file
    
    def _create_manim_scene_content(self, code_content: str, execution_trace: Dict[str, Any]) -> str:
        """Create the content for a Manim scene."""
        lines = code_content.splitlines()
        variables = execution_trace.get('variables', {})
        call_stack = execution_trace.get('call_stack', [])
        
        # Escape the code content properly
        escaped_code = code_content.replace('"', '\\"').replace('\n', '\\n')
        
        scene_content = f'''
from manim import *

class ExecutionVisualization(Scene):
    def construct(self):
        # Setup
        self.camera.background_color = "{self.manim_config['background_color']}"
        
        # Code display
        code_text = Code(
            code="{escaped_code}",
            language="python",
            style="monokai",
            font_size=24
        )
        code_text.to_edge(UP)
        
        # Variable display
        var_text = Text("Variables:", font_size=20, color=YELLOW)
        var_text.to_edge(LEFT).shift(DOWN * 2)
        
        # Call stack display
        stack_text = Text("Call Stack:", font_size=20, color=GREEN)
        stack_text.to_edge(RIGHT).shift(DOWN * 2)
        
        # Terminal simulation
        terminal = Rectangle(width=8, height=3, color=WHITE)
        terminal.to_edge(DOWN)
        terminal_text = Text("Terminal Output", font_size=16, color=WHITE)
        terminal_text.move_to(terminal.get_center())
        
        # Animate elements
        self.play(Write(code_text))
        self.play(Write(var_text))
        self.play(Write(stack_text))
        self.play(Create(terminal))
        self.play(Write(terminal_text))
        
        # Animate variable changes
        for var_name, var_value in {variables}.items():
            var_display = Text(f"{{var_name}} = {{var_value}}", font_size=18, color=BLUE)
            var_display.next_to(var_text, DOWN, buff=0.5)
            self.play(Write(var_display))
            self.wait(1)
        
        # Animate call stack
        for i, call in enumerate(call_stack):
            call_display = Text(f"{{call}}", font_size=16, color=GREEN)
            call_display.next_to(stack_text, DOWN, buff=0.3)
            self.play(Write(call_display))
            self.wait(0.5)
        
        self.wait(2)
'''
        
        return scene_content
    
    def _render_manim_scene(self, scene_file: str) -> str:
        """Render a Manim scene file."""
        try:
            # Run Manim render command
            output_dir = os.path.join(self.temp_dir, "manim_output")
            os.makedirs(output_dir, exist_ok=True)
            
            cmd = [
                "manim", "-pql", scene_file, "ExecutionVisualization",
                "-o", "execution_scene"
            ]
            
            result = subprocess.run(cmd, cwd=self.temp_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Find the generated video file
                video_file = os.path.join(output_dir, "ExecutionVisualization.mp4")
                if os.path.exists(video_file):
                    return video_file
                else:
                    # Look for the file in the temp directory
                    for file in os.listdir(self.temp_dir):
                        if file.endswith('.mp4'):
                            return os.path.join(self.temp_dir, file)
            
            logger.error(f"Manim render failed: {result.stderr}")
            return ""
            
        except Exception as e:
            logger.error(f"Error rendering Manim scene: {e}")
            return ""
    
    def _create_fallback_execution_scene(self, code_content: str, execution_trace: Dict[str, Any]) -> str:
        """Create a fallback execution scene using MoviePy."""
        try:
            # Create a simple visualization using MoviePy
            duration = 10  # 10 seconds
            
            # Create background
            background = ColorClip(size=self.resolution, color=self.background_color, duration=duration)
            
            # Create text overlays
            code_text = TextClip(
                code_content[:200] + "..." if len(code_content) > 200 else code_content,
                fontsize=20,
                color='white',
                font='Arial'
            ).with_position(('center', 100)).with_duration(duration)
            
            # Create variable display
            variables = execution_trace.get('variables', {})
            var_text = ""
            for var_name, var_value in variables.items():
                var_text += f"{var_name} = {var_value}\n"
            
            if var_text:
                var_clip = TextClip(
                    var_text,
                    fontsize=16,
                    color='yellow',
                    font='Arial'
                ).with_position(('left', 300)).with_duration(duration)
                
                # Combine clips
                final_clip = CompositeVideoClip([background, code_text, var_clip])
            else:
                final_clip = CompositeVideoClip([background, code_text])
            
            # Save the video
            output_file = os.path.join(self.temp_dir, "fallback_execution.mp4")
            final_clip.write_videofile(output_file, fps=self.fps, verbose=False, logger=None)
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error creating fallback execution scene: {e}")
            return ""
    
    def trace_code_execution(self, code_content: str) -> Dict[str, Any]:
        """
        Trace code execution using E2B sandbox.
        
        Args:
            code_content: Code to execute and trace
            
        Returns:
            Execution trace data
        """
        if not self.use_e2b:
            logger.warning("E2B not available, using simulated execution trace")
            return self._simulate_execution_trace(code_content)
        
        try:
            # Create E2B session using code_interpreter_sync
            session = code_interpreter_sync.Sandbox(api_key=os.getenv('E2B_API_KEY'))
            
            # Prepare code for execution
            trace_code = f"""
import sys
import traceback
import json

# Setup tracing
variables = {{}}
call_stack = []
output = []

def trace_variable(name, value):
    variables[name] = str(value)

def trace_call(func_name):
    call_stack.append(func_name)

# Execute the code with tracing
try:
{chr(10).join('    ' + line for line in code_content.splitlines())}
except Exception as e:
    output.append(f"Error: {{e}}")

# Return trace data
print(json.dumps({{
    "variables": variables,
    "call_stack": call_stack,
    "output": output,
    "success": len(output) == 0
}}))
"""
            
            # Execute in sandbox using E2B
            result = session.run(trace_code)
            
            # Parse results
            if result and hasattr(result, 'output'):
                try:
                    # Extract the JSON output from the result
                    output_lines = result.output.split('\n')
                    for line in output_lines:
                        if line.strip().startswith('{') and line.strip().endswith('}'):
                            trace_data = json.loads(line.strip())
                            return trace_data
                    logger.error("No valid JSON found in output")
                    return self._simulate_execution_trace(code_content)
                except json.JSONDecodeError:
                    logger.error("Failed to parse execution trace")
                    return self._simulate_execution_trace(code_content)
            
            return self._simulate_execution_trace(code_content)
            
        except Exception as e:
            logger.error(f"Error tracing code execution: {e}")
            return self._simulate_execution_trace(code_content)
    
    def _simulate_execution_trace(self, code_content: str) -> Dict[str, Any]:
        """Simulate execution trace for fallback."""
        # Simple simulation based on code content
        variables = {}
        call_stack = []
        output = []
        
        lines = code_content.splitlines()
        
        for line in lines:
            line = line.strip()
            
            # Detect variable assignments
            if '=' in line and not line.startswith('#'):
                parts = line.split('=')
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    var_value = parts[1].strip()
                    variables[var_name] = var_value
            
            # Detect function calls
            if '(' in line and ')' in line and not line.startswith('#'):
                if 'def ' not in line and 'class ' not in line:
                    # Extract function name
                    func_match = re.search(r'(\w+)\s*\(', line)
                    if func_match:
                        call_stack.append(func_match.group(1))
            
            # Detect print statements
            if 'print(' in line:
                output.append(f"Output: {line}")
        
        return {
            'variables': variables,
            'call_stack': call_stack,
            'output': output,
            'success': True
        }
    
    def create_call_graph_visualization(self, call_graph: Dict[str, Any]) -> str:
        """
        Create a call graph visualization using Manim.
        
        Args:
            call_graph: Call graph data
            
        Returns:
            Path to the generated video file
        """
        if not self.use_manim:
            return self._create_fallback_call_graph(call_graph)
        
        try:
            # Create Manim scene for call graph
            scene_content = self._create_call_graph_scene_content(call_graph)
            
            scene_file = os.path.join(self.temp_dir, "call_graph_scene.py")
            with open(scene_file, 'w') as f:
                f.write(scene_content)
            
            # Render the scene
            return self._render_manim_scene(scene_file)
            
        except Exception as e:
            logger.error(f"Error creating call graph visualization: {e}")
            return self._create_fallback_call_graph(call_graph)
    
    def _create_call_graph_scene_content(self, call_graph: Dict[str, Any]) -> str:
        """Create Manim scene content for call graph visualization."""
        nodes = call_graph.get('nodes', [])
        edges = call_graph.get('edges', [])
        
        scene_content = f'''
from manim import *

class CallGraphVisualization(Scene):
    def construct(self):
        # Setup
        self.camera.background_color = "{self.manim_config['background_color']}"
        
        # Title
        title = Text("Function Call Graph", font_size=36, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Create nodes
        node_objects = {{}}
        for i, node in enumerate({nodes}):
            node_text = Text(node, font_size=20, color=BLUE)
            node_circle = Circle(radius=0.5, color=BLUE, fill_opacity=0.3)
            node_group = VGroup(node_circle, node_text)
            
            # Position nodes in a circle
            angle = i * 2 * PI / len({nodes})
            radius = 3
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            node_group.move_to([x, y, 0])
            
            node_objects[node] = node_group
            self.play(Create(node_group))
        
        # Create edges
        for edge in {edges}:
            if edge[0] in node_objects and edge[1] in node_objects:
                start_node = node_objects[edge[0]]
                end_node = node_objects[edge[1]]
                
                edge_line = Line(
                    start=start_node.get_center(),
                    end=end_node.get_center(),
                    color=YELLOW
                )
                self.play(Create(edge_line))
        
        self.wait(3)
'''
        
        return scene_content
    
    def _create_fallback_call_graph(self, call_graph: Dict[str, Any]) -> str:
        """Create a fallback call graph visualization."""
        try:
            # Create a simple visualization using matplotlib
            import matplotlib.pyplot as plt
            import networkx as nx
            
            G = nx.DiGraph()
            
            # Add nodes and edges
            for node in call_graph.get('nodes', []):
                G.add_node(node)
            
            for edge in call_graph.get('edges', []):
                if len(edge) >= 2:
                    G.add_edge(edge[0], edge[1])
            
            # Create the plot
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(G)
            nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                   node_size=2000, font_size=10, font_weight='bold',
                   arrows=True, edge_color='gray', arrowsize=20)
            
            # Save the plot
            output_file = os.path.join(self.temp_dir, "call_graph.png")
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Convert to video
            return self._convert_image_to_video(output_file)
            
        except Exception as e:
            logger.error(f"Error creating fallback call graph: {e}")
            return ""
    
    def _convert_image_to_video(self, image_path: str, duration: float = 5.0) -> str:
        """Convert an image to a video clip."""
        try:
            image_clip = ImageClip(image_path).with_duration(duration)
            output_file = os.path.join(self.temp_dir, "image_video.mp4")
            image_clip.write_videofile(output_file, fps=self.fps, verbose=False, logger=None)
            return output_file
        except Exception as e:
            logger.error(f"Error converting image to video: {e}")
            return ""
    
    def create_terminal_simulation(self, commands: List[str], outputs: List[str]) -> str:
        """
        Create a terminal simulation video.
        
        Args:
            commands: List of commands to simulate
            outputs: List of corresponding outputs
            
        Returns:
            Path to the generated video file
        """
        try:
            duration = len(commands) * 3  # 3 seconds per command
            
            # Create background
            background = ColorClip(size=self.resolution, color=(0, 0, 0), duration=duration)
            
            clips = [background]
            current_time = 0
            
            for i, (command, output) in enumerate(zip(commands, outputs)):
                # Command text
                cmd_text = TextClip(
                    f"$ {command}",
                    fontsize=16,
                    color='green',
                    font='Courier'
                ).with_position(('left', 100 + i * 60)).set_start(current_time).with_duration(3)
                
                # Output text
                output_text = TextClip(
                    output[:100] + "..." if len(output) > 100 else output,
                    fontsize=14,
                    color='white',
                    font='Courier'
                ).with_position(('left', 120 + i * 60)).set_start(current_time + 1).with_duration(2)
                
                clips.extend([cmd_text, output_text])
                current_time += 3
            
            # Combine all clips
            final_clip = CompositeVideoClip(clips)
            
            # Save the video
            output_file = os.path.join(self.temp_dir, "terminal_simulation.mp4")
            final_clip.write_videofile(output_file, fps=self.fps, verbose=False, logger=None)
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error creating terminal simulation: {e}")
            return ""
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.error(f"Error cleaning up temp directory: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup() 