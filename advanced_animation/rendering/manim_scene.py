"""
ManimGL Scene Renderer

This module handles the creation and rendering of ManimGL scenes for
3Blue1Brown-style animations.
"""

import os
import sys
import logging
import numpy as np
import tempfile
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import time

from ..core.data_structures import StoryboardScene, VisualElement, AnimationStep, CameraMovement
from ..visualizations.visual_metaphors import VisualMetaphorLibrary

# ManimGL imports (3Blue1Brown's original version)
try:
    from manimlib import *
    MANIMGL_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("ManimGL successfully imported")
except (ImportError, TypeError, AttributeError) as e:
    MANIMGL_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.error(f"ManimGL import failed: {e}")
    
    # Try regular Manim as fallback
    try:
        from manim import *
        MANIM_AVAILABLE = True
        logger.info("Using Manim Community Edition as fallback")
    except (ImportError, TypeError, AttributeError) as e2:
        MANIM_AVAILABLE = False
        logger.error(f"Manim Community Edition also failed: {e2}")
    
    # Create dummy classes for when Manim is not available
    class Scene:
        def __init__(self):
            pass
        
        def add(self, obj):
            pass
        
        def play(self, animation, run_time=1):
            pass
        
        def wait(self, duration):
            pass
    
    class FadeIn:
        def __init__(self, target, run_time=1):
            self.target = target
            self.run_time = run_time
    
    class FadeOut:
        def __init__(self, target, run_time=1):
            self.target = target
            self.run_time = run_time
    
    class Create:
        def __init__(self, target, run_time=1):
            self.target = target
            self.run_time = run_time
    
    class Scale:
        def __init__(self, target, scale_factor=1.2, run_time=1):
            self.target = target
            self.scale_factor = scale_factor
            self.run_time = run_time
    
    class Indicate:
        def __init__(self, target, run_time=1, **kwargs):
            self.target = target
            self.run_time = run_time
            self.kwargs = kwargs
    
    class Circumscribe:
        def __init__(self, target, run_time=1):
            self.target = target
            self.run_time = run_time

logger = logging.getLogger(__name__)

class AdvancedManimScene(Scene):
    """Advanced ManimGL scene with 3Blue1Brown-style animations."""
    
    def __init__(self, storyboard_scene: StoryboardScene):
        """
        Initialize the advanced scene.
        
        Args:
            storyboard_scene: Scene specification from storyboard
        """
        super().__init__()
        self.storyboard_scene = storyboard_scene
        self.visual_library = VisualMetaphorLibrary()
        self.visual_elements = {}
        self.animations = []
        
        logger.info(f"AdvancedManimScene initialized for scene {storyboard_scene.id}")
    
    def construct(self):
        """Construct the scene with animations."""
        try:
            logger.info(f"Starting scene construction for scene {self.storyboard_scene.id}")
            
            # Create visual elements
            self.create_visual_elements()
            
            # Execute animation sequence
            self.execute_animation_sequence()
            
            # Add narration timing
            self.add_narration_timing()
            
            logger.info(f"Scene {self.storyboard_scene.id} construction completed")
            
        except Exception as e:
            logger.error(f"Error in scene construction: {e}")
            self.create_error_scene()
    
    def create_visual_elements(self):
        """Create all visual elements for the scene."""
        try:
            for element in self.storyboard_scene.visual_elements:
                visual_obj = self.visual_library.create_visual_element(element)
                
                # Position the element
                pos = element.position
                visual_obj.move_to([pos.get('x', 0), pos.get('y', 0), pos.get('z', 0)])
                
                # Scale if needed
                if element.size != 1.0:
                    visual_obj.scale(element.size)
                
                self.visual_elements[element.type] = visual_obj
                self.add(visual_obj)
                
                logger.info(f"Created visual element: {element.type}")
                
        except Exception as e:
            logger.error(f"Error creating visual elements: {e}")
    
    def execute_animation_sequence(self):
        """Execute the animation sequence for the scene."""
        try:
            for animation_step in self.storyboard_scene.animation_sequence:
                animation = self.create_animation(animation_step)
                if animation:
                    self.play(animation, run_time=animation_step.duration)
                    logger.info(f"Executed animation: {animation_step.action}")
                
        except Exception as e:
            logger.error(f"Error executing animation sequence: {e}")
    
    def create_animation(self, animation_step: AnimationStep) -> Optional[Any]:
        """Create an animation from animation step specification."""
        try:
            target = self.visual_elements.get(animation_step.target)
            if not target:
                logger.warning(f"Target {animation_step.target} not found in visual elements")
                return None
            
            action = animation_step.action
            duration = animation_step.duration
            parameters = animation_step.parameters or {}
            
            if action == "FadeIn":
                return FadeIn(target, run_time=duration)
            elif action == "FadeOut":
                return FadeOut(target, run_time=duration)
            elif action == "Create":
                return Create(target, run_time=duration)
            elif action == "Scale":
                scale_factor = parameters.get("scale", 1.2)
                return Scale(target, scale_factor=scale_factor, run_time=duration)
            elif action == "Move":
                direction = parameters.get("direction", UP)
                distance = parameters.get("distance", 1.0)
                return target.animate.shift(direction * distance)
            elif action == "Rotate":
                angle = parameters.get("angle", PI/4)
                return target.animate.rotate(angle)
            elif action == "Indicate":
                return Indicate(target, run_time=duration)
            elif action == "Circumscribe":
                return Circumscribe(target, run_time=duration)
            else:
                logger.warning(f"Unknown animation action: {action}")
                return FadeIn(target, run_time=duration)
                
        except Exception as e:
            logger.error(f"Error creating animation {animation_step.action}: {e}")
            return None
    
    def add_narration_timing(self):
        """Add timing for narration synchronization."""
        try:
            # Wait for the specified scene duration
            self.wait(self.storyboard_scene.duration)
            logger.info(f"Added narration timing for {self.storyboard_scene.duration} seconds")
            
        except Exception as e:
            logger.error(f"Error adding narration timing: {e}")
    
    def create_error_scene(self):
        """Create a fallback error scene."""
        try:
            error_text = Text(
                "Animation Error",
                font_size=48,
                color=RED
            )
            
            self.play(FadeIn(error_text))
            self.wait(2)
            self.play(FadeOut(error_text))
            
            logger.info("Created error scene as fallback")
            
        except Exception as e:
            logger.error(f"Error creating error scene: {e}")

class ManimSceneRenderer:
    """Renderer for ManimGL scenes."""
    
    def __init__(self, output_dir: str = "manim_output"):
        """
        Initialize the scene renderer.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"ManimSceneRenderer initialized with output directory: {output_dir}")
    
    def render_scene(self, storyboard_scene: StoryboardScene) -> str:
        """
        Render a single scene to video.
        
        Args:
            storyboard_scene: Scene to render
            
        Returns:
            Path to the rendered video file
        """
        try:
            if not MANIMGL_AVAILABLE and not MANIM_AVAILABLE:
                logger.error("Neither ManimGL nor Manim available for rendering")
                return self.create_fallback_video(storyboard_scene)
            
            logger.info(f"Rendering scene {storyboard_scene.id}: {storyboard_scene.concept}")
            
            # Create scene file
            scene_file = self.create_scene_file(storyboard_scene)
            
            # Render the scene
            output_file = self.render_with_manim(scene_file)
            
            # Clean up
            scene_file.unlink()
            
            logger.info(f"Scene {storyboard_scene.id} rendered successfully: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error rendering scene {storyboard_scene.id}: {e}")
            return self.create_fallback_video(storyboard_scene)
    
    def create_scene_file(self, storyboard_scene: StoryboardScene) -> Path:
        """Create a temporary scene file for rendering."""
        try:
            scene_content = self.generate_scene_code(storyboard_scene)
            
            scene_file = self.output_dir / f"scene_{storyboard_scene.id}.py"
            
            with open(scene_file, 'w') as f:
                f.write(scene_content)
            
            logger.info(f"Created scene file: {scene_file}")
            return scene_file
            
        except Exception as e:
            logger.error(f"Error creating scene file: {e}")
            raise
    
    def generate_scene_code(self, storyboard_scene: StoryboardScene) -> str:
        """Generate Python code for the Manim scene."""
        try:
            scene_code = f'''
"""
Auto-generated Manim scene for storyboard scene {storyboard_scene.id}
"""

from manim import *

class Scene{storyboard_scene.id}(Scene):
    def construct(self):
        # Create title
        title = Text(
            "{storyboard_scene.concept}",
            font_size=48,
            color=WHITE
        ).move_to(UP * 2)
        
        # Create subtitle
        subtitle = Text(
            "Generated by Advanced Animation System",
            font_size=24,
            color=GRAY
        ).move_to(DOWN * 2)
        
        # Create visual elements
        elements = VGroup(title, subtitle)
        
        # Animate
        self.play(FadeIn(title))
        self.wait(1)
        self.play(FadeIn(subtitle))
        self.wait(2)
        
        # Add narration text
        narration = Text(
            "{storyboard_scene.narration[:50]}...",
            font_size=20,
            color=BLUE
        ).move_to(DOWN * 3)
        
        self.play(FadeIn(narration))
        self.wait(1)

if __name__ == "__main__":
    # This will be executed by Manim
    pass
'''
            return scene_code
            
        except Exception as e:
            logger.error(f"Error generating scene code: {e}")
            raise
    
    def _serialize_visual_elements(self, elements) -> str:
        """Serialize visual elements to string representation."""
        try:
            serialized = []
            for elem in elements:
                serialized.append(f'''
VisualElement(
    type="{elem.type}",
    properties={elem.properties},
    position={elem.position},
    color="{elem.color}",
    size={elem.size}
)''')
            return f"[{','.join(serialized)}]"
        except Exception as e:
            logger.error(f"Error serializing visual elements: {e}")
            return "[]"
    
    def _serialize_animation_sequence(self, sequence) -> str:
        """Serialize animation sequence to string representation."""
        try:
            serialized = []
            for anim in sequence:
                serialized.append(f'''
AnimationStep(
    action="{anim.action}",
    target="{anim.target}",
    duration={anim.duration},
    easing="{anim.easing}",
    parameters={anim.parameters}
)''')
            return f"[{','.join(serialized)}]"
        except Exception as e:
            logger.error(f"Error serializing animation sequence: {e}")
            return "[]"
    
    def render_with_manim(self, scene_file: Path) -> str:
        """Render the scene using ManimGL or Manim."""
        try:
            scene_name = f"Scene{scene_file.stem.split('_')[1]}"
            
            # Choose the appropriate command based on availability
            if MANIMGL_AVAILABLE:
                cmd = [
                    "manimgl",
                    scene_file.name,
                    scene_name,
                    "-o", "scene",  # Output filename
                    "-pql",  # Preview, quality low
                    "--format", "mp4"
                ]
                logger.info(f"Executing ManimGL command: {' '.join(cmd)}")
            else:
                cmd = [
                    "manim",
                    scene_file.name,
                    scene_name,
                    "-o", "scene",  # Output filename
                    "-pql",  # Preview, quality low
                    "--format", "mp4"
                ]
                logger.info(f"Executing Manim command: {' '.join(cmd)}")
            
            # Execute rendering
            result = subprocess.run(
                cmd,
                cwd=scene_file.parent,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Find the output file in the media directory
                media_dir = self.output_dir / "media" / "videos" / f"scene_{scene_file.stem.split('_')[1]}" / "480p15"
                if media_dir.exists():
                    output_files = list(media_dir.glob("*.mp4"))
                    if output_files:
                        return str(output_files[0])
                
                # Fallback: look in output directory
                output_files = list(self.output_dir.glob("*.mp4"))
                if output_files:
                    return str(output_files[0])
                else:
                    raise Exception("No output file found after successful rendering")
            else:
                logger.error(f"Rendering failed: {result.stderr}")
                raise Exception(f"Rendering failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Rendering timed out")
            raise Exception("Rendering timed out")
        except Exception as e:
            logger.error(f"Error in rendering: {e}")
            raise
    
    def create_fallback_video(self, storyboard_scene: StoryboardScene) -> str:
        """Create a fallback video when Manim is not available."""
        try:
            logger.info("Creating fallback video for scene")
            
            # Create a simple text-based video using MoviePy
            from moviepy.editor import TextClip, ColorClip, CompositeVideoClip
            
            # Create background
            background = ColorClip(
                size=(1920, 1080),
                color=(25, 25, 35),
                duration=storyboard_scene.duration
            )
            
            # Create text
            text_clip = TextClip(
                storyboard_scene.concept,
                fontsize=48,
                color='white',
                font='Arial-Bold'
            ).set_position('center').set_duration(storyboard_scene.duration)
            
            # Composite
            video = CompositeVideoClip([background, text_clip])
            
            # Save
            output_file = self.output_dir / f"fallback_scene_{storyboard_scene.id}.mp4"
            video.write_videofile(
                str(output_file),
                fps=30,
                codec='libx264',
                audio_codec='aac'
            )
            
            logger.info(f"Fallback video created: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error creating fallback video: {e}")
            raise 