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
        """Generate Python code for the Manim scene with rich content."""
        try:
            # Create rich content based on scene concept
            content_code = self._generate_rich_content(storyboard_scene)
            
            scene_code = f'''
"""
Auto-generated Manim scene for storyboard scene {storyboard_scene.id}
"""

from manim import *
import numpy as np

class Scene{storyboard_scene.id}(Scene):
    def construct(self):
        # Set background
        self.camera.background_color = BLACK
        
        # Create title with animation
        title = Text(
            "{storyboard_scene.concept}",
            font_size=48,
            color=WHITE
        ).move_to(UP * 3)
        
        # Create subtitle
        subtitle = Text(
            "Generated by Advanced Animation System",
            font_size=20,
            color=GRAY
        ).move_to(DOWN * 3.5)
        
        # Animate title
        self.play(Write(title), run_time=2)
        self.wait(0.5)
        self.play(FadeIn(subtitle))
        self.wait(1)
        
        # Add rich content based on scene type
        {content_code}
        
        # Add narration text
        narration_text = "{storyboard_scene.narration}"
        if len(narration_text) > 100:
            narration_text = narration_text[:100] + "..."
        
        narration = Text(
            narration_text,
            font_size=18,
            color=BLUE
        ).move_to(DOWN * 2.5)
        
        self.play(FadeIn(narration))
        self.wait(2)
        
        # Fade out everything
        self.play(
            FadeOut(title),
            FadeOut(subtitle),
            FadeOut(narration),
            run_time=1
        )

if __name__ == "__main__":
    # This will be executed by Manim
    pass
'''
            return scene_code
            
        except Exception as e:
            logger.error(f"Error generating scene code: {e}")
            raise
    
    def _generate_rich_content(self, storyboard_scene: StoryboardScene) -> str:
        """Generate rich content based on scene concept and actual repository data."""
        concept = storyboard_scene.concept.lower()
        
        # Extract data from storyboard scene's visual elements and narration
        repo_data = self._extract_repository_data(storyboard_scene)
        
        if "overview" in concept or "analysis" in concept:
            return self._generate_overview_content(storyboard_scene, repo_data)
        elif "structure" in concept:
            return self._generate_structure_content(storyboard_scene, repo_data)
        elif "language" in concept:
            return self._generate_language_content(storyboard_scene, repo_data)
        elif "complexity" in concept:
            return self._generate_complexity_content(storyboard_scene, repo_data)
        elif "function" in concept or "call" in concept:
            return self._generate_function_content(storyboard_scene, repo_data)
        elif "ast" in concept or "structure" in concept:
            return self._generate_ast_content(storyboard_scene, repo_data)
        elif "execution" in concept or "flow" in concept:
            return self._generate_execution_content(storyboard_scene, repo_data)
        elif "data structure" in concept:
            return self._generate_data_structure_content(storyboard_scene, repo_data)
        elif "performance" in concept:
            return self._generate_performance_content(storyboard_scene, repo_data)
        elif "summary" in concept:
            return self._generate_summary_content(storyboard_scene, repo_data)
        else:
            return self._generate_generic_content(storyboard_scene, repo_data)
    
    def _extract_repository_data(self, storyboard_scene: StoryboardScene) -> dict:
        """Extract repository data from storyboard scene."""
        data = {
            'files': 0,
            'languages': [],
            'lines_of_code': 0,
            'functions': 0,
            'classes': 0,
            'file_structure': [],
            'complexity': {'avg': 0, 'max': 0},
            'functions_list': [],
            'data_structures': []
        }
        
        # Parse narration for data
        narration = storyboard_scene.narration.lower()
        
        # Extract file count
        import re
        file_match = re.search(r'(\d+)\s*files?', narration)
        if file_match:
            data['files'] = int(file_match.group(1))
        
        # Extract lines of code
        loc_match = re.search(r'(\d+)\s*lines?\s*of\s*code', narration)
        if loc_match:
            data['lines_of_code'] = int(loc_match.group(1))
        
        # Extract function count
        func_match = re.search(r'(\d+)\s*functions?', narration)
        if func_match:
            data['functions'] = int(func_match.group(1))
        
        # Extract class count
        class_match = re.search(r'(\d+)\s*classes?', narration)
        if class_match:
            data['classes'] = int(class_match.group(1))
        
        # Extract languages
        lang_match = re.search(r'(\d+)\s*languages?', narration)
        if lang_match:
            lang_count = int(lang_match.group(1))
            # Default to Python if only one language
            if lang_count == 1:
                data['languages'] = ['Python']
            else:
                data['languages'] = ['Python', 'JavaScript', 'Java'][:lang_count]
        
        # Extract complexity
        complexity_match = re.search(r'complexity\s*of\s*([\d.]+)', narration)
        if complexity_match:
            data['complexity']['avg'] = float(complexity_match.group(1))
        
        # Extract function names from narration
        func_names = re.findall(r'(\w+)\s*\(\)', narration)
        if func_names:
            data['functions_list'] = func_names[:5]  # Limit to 5 functions
        
        return data
    
    def _generate_overview_content(self, storyboard_scene: StoryboardScene, repo_data: dict) -> str:
        """Generate overview scene content based on actual repository data."""
        files = repo_data.get('files', 0)
        languages = repo_data.get('languages', [])
        lines_of_code = repo_data.get('lines_of_code', 0)
        functions = repo_data.get('functions', 0)
        classes = repo_data.get('classes', 0)
        
        return f'''
        # Create overview metrics based on actual repository data
        metrics = VGroup()
        
        # File count
        file_count = Text("📁 {files} Files", font_size=32, color=GREEN).move_to(LEFT * 3 + UP * 0.5)
        metrics.add(file_count)
        
        # Language count
        lang_count = Text("💻 {len(languages)} Languages", font_size=32, color=BLUE).move_to(RIGHT * 3 + UP * 0.5)
        metrics.add(lang_count)
        
        # Lines of code
        loc_count = Text("📊 {lines_of_code:,} Lines", font_size=32, color=ORANGE).move_to(LEFT * 3 + DOWN * 0.5)
        metrics.add(loc_count)
        
        # Functions
        func_count = Text("🔧 {functions} Functions", font_size=32, color=PURPLE).move_to(RIGHT * 3 + DOWN * 0.5)
        metrics.add(func_count)
        
        # Animate metrics
        for metric in metrics:
            self.play(FadeIn(metric), run_time=0.5)
        
        self.wait(2)
        
        # Create connecting lines
        lines = VGroup()
        for i in range(len(metrics)):
            for j in range(i+1, len(metrics)):
                line = Line(metrics[i].get_center(), metrics[j].get_center(), color=GRAY, stroke_width=1)
                lines.add(line)
        
        self.play(Create(lines), run_time=2)
        self.wait(1)
        '''
    
    def _generate_structure_content(self, storyboard_scene: StoryboardScene, repo_data: dict) -> str:
        """Generate file structure content based on actual repository data."""
        files = repo_data.get('files', 0)
        languages = repo_data.get('languages', [])
        
        # Generate dynamic file structure based on repository data
        if files <= 5:
            # For small repositories, show individual files
            file_items = [
                "📄 main.py",
                "📄 utils.py", 
                "📄 config.py",
                "📄 README.md",
                "📄 requirements.txt"
            ][:files]
        else:
            # For larger repositories, show directory structure
            file_items = [
                "📁 src/",
                "📁 tests/",
                "📁 docs/",
                "📁 config/",
                "📁 scripts/"
            ][:min(5, files // 2)]
        
        file_items_str = ',\n            '.join([f'Text("{item}", font_size=24, color=BLUE)' for item in file_items])
        
        return f'''
        # Create dynamic file structure tree based on repository data
        root = Text("📁 /", font_size=28, color=GREEN).move_to(UP * 1)
        
        # Create file nodes based on actual repository structure
        files = [
            {file_items_str}
        ]
        
        for i, file in enumerate(files):
            file.move_to(UP * (0.5 - i * 0.3) + LEFT * 2)
        
        # Animate structure
        self.play(FadeIn(root))
        self.wait(0.5)
        
        for file in files:
            self.play(FadeIn(file), run_time=0.3)
        
        self.wait(2)
        '''
    
    def _generate_language_content(self, storyboard_scene: StoryboardScene, repo_data: dict) -> str:
        """Generate language distribution content based on actual repository data."""
        languages = repo_data.get('languages', ['Python'])
        
        if len(languages) == 1:
            # Single language - simple pie chart
            return f'''
            # Create pie chart representation for single language
            circle = Circle(radius=1.5, color=BLUE, fill_opacity=0.3)
            circle.move_to(ORIGIN)
            
            # Create language labels
            lang_label = Text("{languages[0]}", font_size=32, color=YELLOW).move_to(RIGHT * 2 + UP * 1)
            lang_percent = Text("100%", font_size=24, color=GRAY).move_to(RIGHT * 2 + UP * 0.5)
            
            # Animate pie chart
            self.play(Create(circle), run_time=2)
            self.wait(0.5)
            
            self.play(FadeIn(lang_label), FadeIn(lang_percent))
            self.wait(2)
            
            # Add rotation animation
            self.play(Rotate(circle, angle=PI/4), run_time=1)
            self.wait(1)
            '''
        else:
            # Multiple languages - segmented pie chart
            lang_labels = []
            for i, lang in enumerate(languages):
                angle = (i * 2 * PI) / len(languages)
                x = 2 * np.cos(angle)
                y = 2 * np.sin(angle)
                lang_labels.append(f'Text("{lang}", font_size=20, color=YELLOW).move_to(np.array([{x}, {y}, 0]))')
            
            lang_labels_str = ',\n            '.join(lang_labels)
            
            return f'''
            # Create segmented pie chart for multiple languages
            circle = Circle(radius=1.5, color=BLUE, fill_opacity=0.3)
            circle.move_to(ORIGIN)
            
            # Create language labels
            lang_labels = [
                {lang_labels_str}
            ]
            
            # Animate pie chart
            self.play(Create(circle), run_time=2)
            self.wait(0.5)
            
            for label in lang_labels:
                self.play(FadeIn(label), run_time=0.5)
            
            self.wait(2)
            
            # Add rotation animation
            self.play(Rotate(circle, angle=PI/4), run_time=1)
            self.wait(1)
            '''
    
    def _generate_complexity_content(self, storyboard_scene: StoryboardScene, repo_data: dict) -> str:
        """Generate complexity analysis content based on actual repository data."""
        avg_complexity = repo_data.get('complexity', {}).get('avg', 5.0)
        max_complexity = repo_data.get('complexity', {}).get('max', avg_complexity)
        
        # Scale bar width based on complexity values
        avg_width = min(3.0, max(1.0, avg_complexity / 10.0))
        max_width = min(3.0, max(1.0, max_complexity / 10.0))
        
        return f'''
        # Create complexity bar chart based on actual repository data
        bars = VGroup()
        
        # Average complexity bar
        avg_bar = Rectangle(width={avg_width}, height=0.5, color=GREEN, fill_opacity=0.7)
        avg_bar.move_to(LEFT * 2 + UP * 0.5)
        avg_label = Text("Avg: {avg_complexity:.1f}", font_size=20, color=WHITE).move_to(LEFT * 2 + UP * 1.2)
        bars.add(avg_bar, avg_label)
        
        # Max complexity bar
        max_bar = Rectangle(width={max_width}, height=0.5, color=RED, fill_opacity=0.7)
        max_bar.move_to(RIGHT * 2 + UP * 0.5)
        max_label = Text("Max: {max_complexity:.1f}", font_size=20, color=WHITE).move_to(RIGHT * 2 + UP * 1.2)
        bars.add(max_bar, max_label)
        
        # Animate bars
        for bar in [avg_bar, max_bar]:
            self.play(GrowFromEdge(bar, DOWN), run_time=1)
        
        for label in [avg_label, max_label]:
            self.play(FadeIn(label), run_time=0.5)
        
        self.wait(2)
        '''
    
    def _generate_function_content(self, storyboard_scene: StoryboardScene, repo_data: dict) -> str:
        """Generate function call graph content based on actual repository data."""
        functions_list = repo_data.get('functions_list', [])
        functions_count = repo_data.get('functions', 0)
        
        if not functions_list and functions_count > 0:
            # Generate generic function names if none found
            functions_list = [f"function_{i+1}" for i in range(min(functions_count, 5))]
        
        if not functions_list:
            functions_list = ["main", "process", "validate", "execute"]
        
        # Create main function
        main_func_name = functions_list[0] if functions_list else "main"
        
        # Create called functions
        called_funcs = []
        positions = [
            (UP * 1.5 + LEFT * 2),
            (UP * 1.5 + RIGHT * 2),
            (DOWN * 1.5 + LEFT * 2),
            (DOWN * 1.5 + RIGHT * 2)
        ]
        
        for i, func_name in enumerate(functions_list[1:5]):  # Limit to 4 called functions
            called_funcs.append((func_name, positions[i]))
        
        if not called_funcs:
            called_funcs = [("process", UP * 1.5 + LEFT * 2), ("validate", UP * 1.5 + RIGHT * 2)]
        
        func_nodes_code = []
        for func_name, pos in called_funcs:
            # Convert numpy array to Manim vector notation
            if hasattr(pos, '__iter__'):
                pos_str = f"np.array([{pos[0]}, {pos[1]}, {pos[2]}])"
            else:
                pos_str = str(pos)
            func_nodes_code.append(f'''
        node = Circle(radius=0.2, color=GREEN, fill_opacity=0.7).move_to({pos_str})
        label = Text("{func_name}", font_size=12, color=WHITE).move_to({pos_str})
        func_nodes.add(node, label)''')
        
        func_nodes_str = ''.join(func_nodes_code)
        
        return f'''
        # Create function call graph based on actual repository data
        main_func = Circle(radius=0.3, color=BLUE, fill_opacity=0.7)
        main_func.move_to(ORIGIN)
        main_label = Text("{main_func_name}", font_size=16, color=WHITE).move_to(ORIGIN)
        
        # Create called functions
        func_nodes = VGroup()
        {func_nodes_str}
        
        # Animate main function
        self.play(Create(main_func), Write(main_label))
        self.wait(1)
        
        # Animate called functions
        for i in range(0, len(func_nodes), 2):
            self.play(Create(func_nodes[i]), Write(func_nodes[i+1]), run_time=0.5)
        
        # Create connections
        connections = VGroup()
        for i in range(0, len(func_nodes), 2):
            line = Line(main_func.get_center(), func_nodes[i].get_center(), color=YELLOW)
            connections.add(line)
        
        self.play(Create(connections), run_time=2)
        self.wait(2)
        '''
    
    def _generate_ast_content(self, storyboard_scene: StoryboardScene, repo_data: dict) -> str:
        """Generate AST visualization content based on actual repository data."""
        functions = repo_data.get('functions', 0)
        classes = repo_data.get('classes', 0)
        files = repo_data.get('files', 0)
        
        # Generate dynamic AST nodes based on repository structure
        nodes = []
        
        if functions > 0:
            nodes.append(("FunctionDef", UP * 1 + LEFT * 2))
        if classes > 0:
            nodes.append(("ClassDef", UP * 1 + RIGHT * 2))
        
        # Add common AST nodes
        nodes.extend([
            ("Import", DOWN * 1 + LEFT * 2),
            ("Assign", DOWN * 1 + RIGHT * 2)
        ])
        
        # Limit to 4 nodes for visualization
        nodes = nodes[:4]
        
        nodes_code = []
        for node_name, pos in nodes:
            # Convert numpy array to Manim vector notation
            if hasattr(pos, '__iter__'):
                pos_str = f"np.array([{pos[0]}, {pos[1]}, {pos[2]}])"
            else:
                pos_str = str(pos)
            nodes_code.append(f'''
        node = Rectangle(width=1.5, height=0.4, color=BLUE, fill_opacity=0.3).move_to({pos_str})
        label = Text("{node_name}", font_size=16, color=WHITE).move_to({pos_str})
        ast_nodes.add(node, label)''')
        
        nodes_str = ''.join(nodes_code)
        
        return f'''
        # Create AST tree structure based on repository data
        root = Text("Module", font_size=24, color=WHITE).move_to(UP * 2)
        
        # Create AST nodes
        ast_nodes = VGroup()
        {nodes_str}
        
        # Animate root
        self.play(Create(root))
        self.wait(0.5)
        
        # Animate child nodes
        for i in range(0, len(ast_nodes), 2):
            self.play(Create(ast_nodes[i]), Write(ast_nodes[i+1]), run_time=0.5)
        
        # Create tree connections
        connections = VGroup()
        for i in range(0, len(ast_nodes), 2):
            line = Line(root.get_center(), ast_nodes[i].get_center(), color=GRAY)
            connections.add(line)
        
        self.play(Create(connections), run_time=2)
        self.wait(2)
        '''
    
    def _generate_execution_content(self, storyboard_scene: StoryboardScene, repo_data: dict) -> str:
        """Generate execution flow content based on actual repository data."""
        functions = repo_data.get('functions', 0)
        functions_list = repo_data.get('functions_list', [])
        
        # Generate dynamic execution steps based on repository complexity
        if functions > 5:
            steps = [
                ("Start", UP * 2),
                ("Parse", UP * 1),
                ("Process", ORIGIN),
                ("Validate", DOWN * 1),
                ("Execute", DOWN * 2)
            ]
        elif functions > 2:
            steps = [
                ("Initialize", UP * 1.5),
                ("Process", ORIGIN),
                ("Complete", DOWN * 1.5)
            ]
        else:
            steps = [
                ("Start", UP * 1),
                ("Execute", DOWN * 1)
            ]
        
        steps_code = []
        for step_name, pos in steps:
            # Convert numpy array to Manim vector notation
            if hasattr(pos, '__iter__'):
                pos_str = f"np.array([{pos[0]}, {pos[1]}, {pos[2]}])"
            else:
                pos_str = str(pos)
            steps_code.append(f'''
        node = Circle(radius=0.3, color=ORANGE, fill_opacity=0.7).move_to({pos_str})
        label = Text("{step_name}", font_size=14, color=WHITE).move_to({pos_str})
        flow_nodes.add(node, label)''')
        
        steps_str = ''.join(steps_code)
        
        return f'''
        # Create execution flow diagram based on repository complexity
        flow_nodes = VGroup()
        {steps_str}
        
        # Animate nodes sequentially
        for i in range(0, len(flow_nodes), 2):
            self.play(Create(flow_nodes[i]), Write(flow_nodes[i+1]), run_time=0.8)
        
        # Create flow arrows
        arrows = VGroup()
        for i in range(0, len(flow_nodes)-2, 2):
            arrow = Arrow(
                flow_nodes[i].get_center(),
                flow_nodes[i+2].get_center(),
                color=YELLOW,
                buff=0.3
            )
            arrows.add(arrow)
        
        self.play(Create(arrows), run_time=2)
        self.wait(2)
        '''
    
    def _generate_data_structure_content(self, storyboard_scene: StoryboardScene, repo_data: dict) -> str:
        """Generate data structure visualization content based on actual repository data."""
        files = repo_data.get('files', 0)
        functions = repo_data.get('functions', 0)
        
        # Determine which data structures to show based on repository complexity
        if files > 10:
            # Large repository - show multiple data structures
            return '''
            # Create multiple data structures for large repository
            # Array
            array_elements = VGroup()
            for i in range(5):
                element = Square(side_length=0.4, color=BLUE, fill_opacity=0.7)
                element.move_to(LEFT * 3 + RIGHT * i * 0.5)
                label = Text(str(i+1), font_size=16, color=WHITE).move_to(element.get_center())
                array_elements.add(element, label)
            
            # Tree
            tree_root = Circle(radius=0.2, color=GREEN, fill_opacity=0.7).move_to(ORIGIN)
            tree_left = Circle(radius=0.15, color=GREEN, fill_opacity=0.7).move_to(LEFT * 1 + DOWN * 1)
            tree_right = Circle(radius=0.15, color=GREEN, fill_opacity=0.7).move_to(RIGHT * 1 + DOWN * 1)
            
            tree_connections = VGroup(
                Line(tree_root.get_center(), tree_left.get_center(), color=GRAY),
                Line(tree_root.get_center(), tree_right.get_center(), color=GRAY)
            )
            
            # Animate array
            self.play(Create(array_elements), run_time=2)
            self.wait(1)
            
            # Animate tree
            self.play(Create(tree_root))
            self.play(Create(tree_left), Create(tree_right))
            self.play(Create(tree_connections))
            self.wait(2)
            '''
        else:
            # Small repository - simple data structure
            return '''
            # Create simple data structure for small repository
            # Array
            array_elements = VGroup()
            for i in range(3):
                element = Square(side_length=0.4, color=BLUE, fill_opacity=0.7)
                element.move_to(LEFT * 1.5 + RIGHT * i * 0.5)
                label = Text(str(i+1), font_size=16, color=WHITE).move_to(element.get_center())
                array_elements.add(element, label)
            
            # Animate array
            self.play(Create(array_elements), run_time=2)
            self.wait(2)
            '''
    
    def _generate_performance_content(self, storyboard_scene: StoryboardScene, repo_data: dict) -> str:
        """Generate performance analysis content based on actual repository data."""
        functions = repo_data.get('functions', 0)
        lines_of_code = repo_data.get('lines_of_code', 0)
        
        # Calculate average function length
        avg_length = lines_of_code / max(functions, 1)
        
        # Determine performance rating
        if avg_length < 20:
            perf_color = "GREEN"
            perf_symbol = "✓"
        elif avg_length < 50:
            perf_color = "YELLOW"
            perf_symbol = "⚠"
        else:
            perf_color = "RED"
            perf_symbol = "✗"
        
        return f'''
        # Create performance metrics based on actual repository data
        metrics = VGroup()
        
        # Function count
        func_metric = Text("Functions: {functions}", font_size=28, color=BLUE).move_to(LEFT * 3 + UP * 0.5)
        metrics.add(func_metric)
        
        # Average length
        length_metric = Text("Avg Length: {avg_length:.1f}", font_size=28, color=GREEN).move_to(RIGHT * 3 + UP * 0.5)
        metrics.add(length_metric)
        
        # Performance indicator
        perf_indicator = Circle(radius=0.5, color={perf_color}, fill_opacity=0.7).move_to(DOWN * 1)
        perf_label = Text("{perf_symbol}", font_size=36, color=WHITE).move_to(DOWN * 1)
        
        # Animate metrics
        for metric in metrics:
            self.play(FadeIn(metric), run_time=0.5)
        
        self.wait(1)
        
        # Animate performance indicator
        self.play(Create(perf_indicator), Write(perf_label))
        self.wait(2)
        '''
    
    def _generate_summary_content(self, storyboard_scene: StoryboardScene, repo_data: dict) -> str:
        """Generate summary content based on actual repository data."""
        files = repo_data.get('files', 0)
        languages = repo_data.get('languages', [])
        lines_of_code = repo_data.get('lines_of_code', 0)
        functions = repo_data.get('functions', 0)
        classes = repo_data.get('classes', 0)
        
        lang_str = f"{len(languages)} language{'s' if len(languages) != 1 else ''}"
        
        return f'''
        # Create summary dashboard based on actual repository data
        summary_box = Rectangle(width=6, height=3, color=BLUE, fill_opacity=0.1)
        summary_box.move_to(ORIGIN)
        
        # Summary text
        summary_text = Text(
            "Repository Analysis Complete",
            font_size=24,
            color=WHITE
        ).move_to(UP * 0.5)
        
        details = Text(
            "{files} files • {lang_str} • {lines_of_code:,} lines • {functions} functions",
            font_size=18,
            color=GRAY
        ).move_to(DOWN * 0.5)
        
        # Animate summary
        self.play(Create(summary_box), run_time=1)
        self.wait(0.5)
        
        self.play(Write(summary_text))
        self.wait(1)
        
        self.play(Write(details))
        self.wait(2)
        '''
    
    def _generate_generic_content(self, storyboard_scene: StoryboardScene, repo_data: dict) -> str:
        """Generate generic content for unknown scene types based on repository data."""
        files = repo_data.get('files', 0)
        functions = repo_data.get('functions', 0)
        
        # Create dynamic visualization based on repository size
        if files > 10:
            # Large repository - show multiple elements
            return '''
            # Create dynamic visualization for large repository
            elements = VGroup()
            
            # Create multiple circles representing files
            for i in range(5):
                circle = Circle(radius=0.3, color=BLUE, fill_opacity=0.3)
                circle.move_to(LEFT * 2 + RIGHT * i * 0.8 + UP * (i % 2 - 0.5))
                elements.add(circle)
            
            # Animate elements
            for element in elements:
                self.play(Create(element), run_time=0.3)
            
            self.wait(2)
            '''
        else:
            # Small repository - simple visualization
            return '''
            # Create simple visualization for small repository
            circle = Circle(radius=1, color=BLUE, fill_opacity=0.3)
            circle.move_to(ORIGIN)
            
            # Create some geometric elements
            square = Square(side_length=0.8, color=GREEN, fill_opacity=0.3)
            square.move_to(LEFT * 2)
            
            triangle = Triangle(color=RED, fill_opacity=0.3)
            triangle.move_to(RIGHT * 2)
            
            # Animate elements
            self.play(Create(circle), run_time=1)
            self.wait(0.5)
            
            self.play(Create(square), Create(triangle), run_time=1)
            self.wait(2)
            '''
    
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