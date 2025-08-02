"""
AI-Powered Storyboard Generator

This module converts code analysis into 3Blue1Brown-style visual storyboards
using GPT-4 for concept abstraction and visual metaphor generation.
"""

import os
import json
import logging
import openai
from typing import Dict, List, Any, Optional
from pathlib import Path
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .data_structures import (
    Storyboard, StoryboardScene, VisualElement, 
    AnimationStep, CameraMovement, DataStructureManager
)

logger = logging.getLogger(__name__)

class StoryboardGenerator:
    """AI-powered storyboard generator using GPT-4."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the storyboard generator.
        
        Args:
            openai_api_key: OpenAI API key for GPT-4 access
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            self.client = openai.OpenAI(api_key=self.openai_api_key)
        else:
            logger.warning("OpenAI API key not provided. Using fallback storyboard generation.")
            self.client = None
            
        # Visual metaphor library
        self.visual_metaphors = {
            "array": {
                "type": "rectangle_array",
                "default_color": "#ff7f0e",
                "animation": "sequential_highlight"
            },
            "tree": {
                "type": "hierarchical_tree",
                "default_color": "#2ca02c",
                "animation": "depth_first_traversal"
            },
            "graph": {
                "type": "network_graph",
                "default_color": "#d62728",
                "animation": "path_highlight"
            },
            "stack": {
                "type": "vertical_stack",
                "default_color": "#9467bd",
                "animation": "push_pop_animation"
            },
            "queue": {
                "type": "horizontal_queue",
                "default_color": "#8c564b",
                "animation": "enqueue_dequeue"
            },
            "sorting": {
                "type": "array_with_pivot",
                "default_color": "#e377c2",
                "animation": "partition_animation"
            },
            "searching": {
                "type": "array_with_pointer",
                "default_color": "#7f7f7f",
                "animation": "binary_search_animation"
            }
        }
        
        logger.info("StoryboardGenerator initialized with visual metaphor library")
        
    def generate_storyboard(self, code_analysis: Dict[str, Any]) -> Storyboard:
        """
        Convert code analysis into visual storyboard using GPT-4.
        
        Args:
            code_analysis: Dictionary containing code analysis results
            
        Returns:
            Storyboard object with scenes and animations
        """
        logger.info(f"Generating storyboard for code analysis with {len(code_analysis.get('files', []))} files")
        
        if self.client:
            return self._generate_ai_storyboard(code_analysis)
        else:
            return self._generate_fallback_storyboard(code_analysis)
    
    def _generate_ai_storyboard(self, code_analysis: Dict[str, Any]) -> Storyboard:
        """Generate storyboard using GPT-4 AI."""
        try:
            logger.info("Using GPT-4 for AI-powered storyboard generation")
            
            # Prepare the prompt
            prompt = self._create_storyboard_prompt(code_analysis)
            
            # Call GPT-4
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in creating 3Blue1Brown-style educational animations. Convert code analysis into visual storyboards with clear visual metaphors and smooth animations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=4000
            )
            
            # Parse the response
            storyboard_data = json.loads(response.choices[0].message.content)
            logger.info(f"Successfully generated AI storyboard with {len(storyboard_data.get('scenes', []))} scenes")
            
            return self._parse_storyboard_response(storyboard_data, code_analysis)
            
        except Exception as e:
            logger.error(f"Error generating AI storyboard: {e}")
            logger.info("Falling back to rule-based storyboard generation")
            return self._generate_fallback_storyboard(code_analysis)
    
    def _create_storyboard_prompt(self, code_analysis: Dict[str, Any]) -> str:
        """Create the prompt for GPT-4 storyboard generation."""
        
        # Extract key information from code analysis
        files = code_analysis.get('files', [])
        algorithms = code_analysis.get('algorithms', [])
        data_structures = code_analysis.get('data_structures', [])
        complexity = code_analysis.get('complexity_analysis', {})
        
        prompt = f"""
        Create a 3Blue1Brown-style storyboard for this code analysis:
        
        Files: {len(files)} files analyzed
        Algorithms: {algorithms}
        Data Structures: {data_structures}
        Complexity: {complexity}
        
        Code Analysis Details:
        {json.dumps(code_analysis, indent=2)}
        
        Output JSON format:
        {{
          "title": "Algorithm Visualization",
          "description": "Educational animation explaining the code",
          "scenes": [
            {{
              "id": 1,
              "concept": "Introduction to the algorithm",
              "visual_elements": [
                {{
                  "type": "array",
                  "properties": {{"size": 5, "values": [3, 1, 4, 1, 5]}},
                  "position": {{"x": 0, "y": 0, "z": 0}},
                  "color": "#ff7f0e",
                  "size": 1.0
                }}
              ],
              "animation_sequence": [
                {{
                  "action": "FadeIn",
                  "target": "array",
                  "duration": 2.0,
                  "easing": "ease_in_out",
                  "parameters": {{"scale": 1.2}}
                }}
              ],
              "narration": "We start by examining our array of numbers...",
              "duration": 8.0,
              "camera_movement": {{
                "phi": 75.0,
                "theta": -45.0,
                "zoom": 1.2,
                "duration": 2.0
              }}
            }}
          ],
          "total_duration": 45.0,
          "metadata": {{
            "style": "3blue1brown",
            "theme": "educational",
            "target_audience": "programmers"
          }}
        }}
        
        Guidelines:
        1. Use clear visual metaphors (arrays as rectangles, trees as hierarchical structures)
        2. Include smooth camera movements and transitions
        3. Break complex algorithms into digestible steps
        4. Use color coding for different concepts
        5. Include runtime execution visualization where possible
        6. Keep each scene focused on one concept
        7. Use 3D positioning for depth and visual interest
        """
        
        return prompt
    
    def _parse_storyboard_response(self, storyboard_data: Dict[str, Any], code_analysis: Dict[str, Any]) -> Storyboard:
        """Parse GPT-4 response into Storyboard object."""
        
        scenes = []
        for scene_data in storyboard_data.get('scenes', []):
            # Parse visual elements
            visual_elements = []
            for elem_data in scene_data.get('visual_elements', []):
                visual_elements.append(VisualElement(**elem_data))
            
            # Parse animation sequence
            animation_sequence = []
            for anim_data in scene_data.get('animation_sequence', []):
                animation_sequence.append(AnimationStep(**anim_data))
            
            # Parse camera movement
            camera_data = scene_data.get('camera_movement', {})
            camera_movement = CameraMovement(**camera_data)
            
            # Create scene
            scene = StoryboardScene(
                id=scene_data['id'],
                concept=scene_data['concept'],
                visual_elements=visual_elements,
                animation_sequence=animation_sequence,
                narration=scene_data['narration'],
                duration=scene_data['duration'],
                camera_movement=camera_movement,
                code_snippet=scene_data.get('code_snippet'),
                execution_state=scene_data.get('execution_state')
            )
            scenes.append(scene)
        
        return Storyboard(
            title=storyboard_data.get('title', 'Code Visualization'),
            description=storyboard_data.get('description', 'Educational animation'),
            scenes=scenes,
            total_duration=storyboard_data.get('total_duration', 60.0),
            metadata=storyboard_data.get('metadata', {})
        )
    
    def _generate_fallback_storyboard(self, code_analysis: Dict[str, Any]) -> Storyboard:
        """Generate storyboard using rule-based approach when AI is not available."""
        logger.info("Generating fallback storyboard using rule-based approach")
        
        scenes = []
        scene_id = 1
        
        # Introduction scene
        intro_scene = self._create_intro_scene(scene_id, code_analysis)
        scenes.append(intro_scene)
        scene_id += 1
        
        # Algorithm scenes
        algorithms = code_analysis.get('algorithms', [])
        for algorithm in algorithms:
            algorithm_scene = self._create_algorithm_scene(scene_id, algorithm, code_analysis)
            scenes.append(algorithm_scene)
            scene_id += 1
        
        # Data structure scenes
        data_structures = code_analysis.get('data_structures', [])
        for ds in data_structures:
            ds_scene = self._create_data_structure_scene(scene_id, ds, code_analysis)
            scenes.append(ds_scene)
            scene_id += 1
        
        # Complexity analysis scene
        complexity = code_analysis.get('complexity_analysis', {})
        if complexity:
            complexity_scene = self._create_complexity_scene(scene_id, complexity, code_analysis)
            scenes.append(complexity_scene)
            scene_id += 1
        
        # Summary scene
        summary_scene = self._create_summary_scene(scene_id, code_analysis)
        scenes.append(summary_scene)
        
        total_duration = sum(scene.duration for scene in scenes)
        
        return Storyboard(
            title="Code Repository Visualization",
            description="Educational animation of the codebase",
            scenes=scenes,
            total_duration=total_duration,
            metadata={
                "style": "3blue1brown",
                "theme": "educational",
                "generation_method": "rule_based"
            }
        )
    
    def _create_intro_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create introduction scene."""
        files = code_analysis.get('files', [])
        
        visual_elements = [
            VisualElement(
                type="text",
                properties={"text": f"Repository Analysis", "font_size": 48},
                position={"x": 0, "y": 2, "z": 0},
                color="#ffffff"
            ),
            VisualElement(
                type="text",
                properties={"text": f"{len(files)} files analyzed", "font_size": 24},
                position={"x": 0, "y": 0, "z": 0},
                color="#cccccc"
            )
        ]
        
        animation_sequence = [
            AnimationStep("FadeIn", "text", 2.0),
            AnimationStep("Scale", "text", 1.0, parameters={"scale": 1.1})
        ]
        
        return StoryboardScene(
            id=scene_id,
            concept="Repository Overview",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration="Welcome to our code repository analysis. We'll explore the algorithms and data structures used in this codebase.",
            duration=5.0,
            camera_movement=CameraMovement()
        )
    
    def _create_algorithm_scene(self, scene_id: int, algorithm: str, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create scene for algorithm visualization."""
        
        # Determine visual metaphor based on algorithm type
        if "sort" in algorithm.lower():
            visual_type = "sorting"
            metaphor = self.visual_metaphors["sorting"]
        elif "search" in algorithm.lower():
            visual_type = "searching"
            metaphor = self.visual_metaphors["searching"]
        else:
            visual_type = "array"
            metaphor = self.visual_metaphors["array"]
        
        visual_elements = [
            VisualElement(
                type=metaphor["type"],
                properties={"size": 6, "values": [3, 1, 4, 1, 5, 9]},
                position={"x": 0, "y": 0, "z": 0},
                color=metaphor["default_color"]
            ),
            VisualElement(
                type="text",
                properties={"text": algorithm.title(), "font_size": 36},
                position={"x": 0, "y": 2, "z": 0},
                color="#ffffff"
            )
        ]
        
        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.5),
            AnimationStep("Create", visual_type, 2.0),
            AnimationStep(metaphor["animation"], visual_type, 4.0)
        ]
        
        return StoryboardScene(
            id=scene_id,
            concept=f"{algorithm.title()} Algorithm",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration=f"Let's examine the {algorithm} algorithm. This is a fundamental algorithm that...",
            duration=8.0,
            camera_movement=CameraMovement(zoom=1.5)
        )
    
    def _create_data_structure_scene(self, scene_id: int, data_structure: str, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create scene for data structure visualization."""
        
        # Map data structure to visual metaphor
        ds_lower = data_structure.lower()
        if "tree" in ds_lower:
            visual_type = "tree"
            metaphor = self.visual_metaphors["tree"]
        elif "graph" in ds_lower:
            visual_type = "graph"
            metaphor = self.visual_metaphors["graph"]
        elif "stack" in ds_lower:
            visual_type = "stack"
            metaphor = self.visual_metaphors["stack"]
        elif "queue" in ds_lower:
            visual_type = "queue"
            metaphor = self.visual_metaphors["queue"]
        else:
            visual_type = "array"
            metaphor = self.visual_metaphors["array"]
        
        visual_elements = [
            VisualElement(
                type=metaphor["type"],
                properties={"size": 5, "values": [1, 2, 3, 4, 5]},
                position={"x": 0, "y": 0, "z": 0},
                color=metaphor["default_color"]
            ),
            VisualElement(
                type="text",
                properties={"text": data_structure.title(), "font_size": 36},
                position={"x": 0, "y": 2, "z": 0},
                color="#ffffff"
            )
        ]
        
        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.5),
            AnimationStep("Create", visual_type, 2.0),
            AnimationStep(metaphor["animation"], visual_type, 4.0)
        ]
        
        return StoryboardScene(
            id=scene_id,
            concept=f"{data_structure.title()} Data Structure",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration=f"The {data_structure} data structure is used to organize and store data efficiently...",
            duration=8.0,
            camera_movement=CameraMovement(phi=60, theta=-30)
        )
    
    def _create_complexity_scene(self, scene_id: int, complexity: Dict[str, Any], code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create scene for complexity analysis visualization."""
        
        visual_elements = [
            VisualElement(
                type="complexity_graph",
                properties={"time_complexity": complexity.get("time", "O(n)"), "space_complexity": complexity.get("space", "O(1)")},
                position={"x": 0, "y": 0, "z": 0},
                color="#e377c2"
            ),
            VisualElement(
                type="text",
                properties={"text": "Complexity Analysis", "font_size": 36},
                position={"x": 0, "y": 2, "z": 0},
                color="#ffffff"
            )
        ]
        
        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.5),
            AnimationStep("Create", "complexity_graph", 2.0),
            AnimationStep("AnimateGrowth", "complexity_graph", 4.0)
        ]
        
        return StoryboardScene(
            id=scene_id,
            concept="Algorithm Complexity",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration="Let's analyze the time and space complexity of our algorithms...",
            duration=8.0,
            camera_movement=CameraMovement(zoom=1.3)
        )
    
    def _create_summary_scene(self, scene_id: int, code_analysis: Dict[str, Any]) -> StoryboardScene:
        """Create summary scene."""
        
        algorithms = code_analysis.get('algorithms', [])
        data_structures = code_analysis.get('data_structures', [])
        
        visual_elements = [
            VisualElement(
                type="summary_dashboard",
                properties={"algorithms": algorithms, "data_structures": data_structures},
                position={"x": 0, "y": 0, "z": 0},
                color="#1f77b4"
            ),
            VisualElement(
                type="text",
                properties={"text": "Summary", "font_size": 48},
                position={"x": 0, "y": 2, "z": 0},
                color="#ffffff"
            )
        ]
        
        animation_sequence = [
            AnimationStep("FadeIn", "text", 1.5),
            AnimationStep("Create", "summary_dashboard", 3.0),
            AnimationStep("Highlight", "summary_dashboard", 2.0)
        ]
        
        return StoryboardScene(
            id=scene_id,
            concept="Repository Summary",
            visual_elements=visual_elements,
            animation_sequence=animation_sequence,
            narration="In summary, we've explored the key algorithms and data structures in this repository...",
            duration=6.0,
            camera_movement=CameraMovement(zoom=1.0)
        )
    
    def save_storyboard(self, storyboard: Storyboard, output_path: str) -> str:
        """Save storyboard to JSON file."""
        return DataStructureManager.save_storyboard(storyboard, output_path)
    
    def load_storyboard(self, file_path: str) -> Storyboard:
        """Load storyboard from JSON file."""
        return DataStructureManager.load_storyboard(file_path) 