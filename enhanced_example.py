"""
Enhanced RepoToVideo Example

This example demonstrates how to use all the new enhanced features:
- Enhanced code analysis with call graphs and dependency detection
- Dynamic execution visualization with E2B sandbox
- AI narration with ElevenLabs
- Error simulation engine
- Plugin-based parser architecture
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import debug configuration
from debug_config import setup_debug_logging, verify_environment_setup, test_api_connections

# Import enhanced modules
from code_analysis import EnhancedCodeAnalyzer
from error_simulation import ErrorSimulator
from narration import AINarrator, NarrationManager, VoiceStyle, Language
from video_generator import VideoGenerator
from parsers import ParserManager

# Setup comprehensive debug logging
logger = setup_debug_logging("DEBUG")


class EnhancedRepoToVideo:
    """Enhanced RepoToVideo with all new features."""
    
    def __init__(self, project_path: str):
        """
        Initialize the enhanced RepoToVideo system.
        
        Args:
            project_path: Path to the project to analyze
        """
        self.project_path = Path(project_path)
        
        # Initialize components
        self.code_analyzer = EnhancedCodeAnalyzer(str(self.project_path))
        self.error_simulator = ErrorSimulator()
        self.narrator = AINarrator(api_key=os.getenv('ELEVENLABS_API_KEY'))
        self.narration_manager = NarrationManager(self.narrator)
        self.video_generator = VideoGenerator()
        self.parser_manager = ParserManager()
        
        logger.info(f"Enhanced RepoToVideo initialized for project: {project_path}")
    
    def analyze_project(self) -> Dict[str, Any]:
        """
        Perform comprehensive project analysis.
        
        Returns:
            Complete project analysis results
        """
        logger.info("Starting comprehensive project analysis")
        
        # Enhanced code analysis
        analysis = self.code_analyzer.analyze_project()
        
        # Parse project using plugin architecture
        parser_results = self.parser_manager.parse_project(self.project_path)
        analysis['parser_results'] = parser_results
        
        logger.info(f"Analysis complete. Found {len(analysis['files'])} files")
        return analysis
    
    def generate_error_simulations(self, code_content: str, num_errors: int = 3) -> List[Any]:
        """
        Generate error simulations for educational purposes.
        
        Args:
            code_content: Code to simulate errors for
            num_errors: Number of errors to simulate
            
        Returns:
            List of error simulations
        """
        logger.info(f"Generating {num_errors} error simulations")
        
        simulations = self.error_simulator.generate_error_simulations(code_content, num_errors)
        
        # Execute simulations to capture actual errors
        for simulation in simulations:
            error_result = self.error_simulator.execute_with_error(simulation)
            simulation.execution_result = error_result
            
            # Also execute fixed code to verify solutions
            fixed_result = self.error_simulator.execute_fixed_code(simulation)
            simulation.fixed_result = fixed_result
        
        logger.info(f"Generated {len(simulations)} error simulations")
        return simulations
    
    def create_dynamic_visualization(self, code_content: str) -> str:
        """
        Create dynamic execution visualization.
        
        Args:
            code_content: Code to visualize
            
        Returns:
            Path to the generated visualization video
        """
        logger.info("Creating dynamic execution visualization")
        
        # Trace code execution
        execution_trace = self.video_generator.trace_code_execution(code_content)
        
        # Create dynamic visualization
        video_path = self.video_generator.create_dynamic_execution_scene(
            code_content, execution_trace
        )
        
        logger.info(f"Dynamic visualization created: {video_path}")
        return video_path
    
    def generate_narration(self, content: Dict[str, Any], voice_style: VoiceStyle = VoiceStyle.PROFESSIONAL) -> List[Dict[str, Any]]:
        """
        Generate AI narration for content.
        
        Args:
            content: Content to narrate
            voice_style: Style of voice to use
            
        Returns:
            List of narrated content with audio files
        """
        logger.info(f"Generating narration with {voice_style.value} voice style")
        
        # Create narration configuration
        config = self.narrator.create_narration_config(style=voice_style)
        
        # Generate narration
        narrated_content = self.narration_manager.generate_video_narration([content], config)
        
        logger.info(f"Generated narration for {len(narrated_content)} content items")
        return narrated_content
    
    def create_call_graph_visualization(self, call_graph: Dict[str, Any]) -> str:
        """
        Create call graph visualization.
        
        Args:
            call_graph: Call graph data
            
        Returns:
            Path to the generated visualization video
        """
        logger.info("Creating call graph visualization")
        
        video_path = self.video_generator.create_call_graph_visualization(call_graph)
        
        logger.info(f"Call graph visualization created: {video_path}")
        return video_path
    
    def create_terminal_simulation(self, commands: List[str], outputs: List[str]) -> str:
        """
        Create terminal simulation video.
        
        Args:
            commands: List of commands to simulate
            outputs: List of corresponding outputs
            
        Returns:
            Path to the generated simulation video
        """
        logger.info("Creating terminal simulation")
        
        video_path = self.video_generator.create_terminal_simulation(commands, outputs)
        
        logger.info(f"Terminal simulation created: {video_path}")
        return video_path
    
    def generate_complete_video(self, output_path: str = "enhanced_walkthrough.mp4") -> str:
        """
        Generate a complete enhanced video walkthrough.
        
        Args:
            output_path: Path for the output video
            
        Returns:
            Path to the generated video
        """
        logger.info("Generating complete enhanced video walkthrough")
        
        # Step 1: Analyze the project
        analysis = self.analyze_project()
        
        # Step 2: Generate video steps
        steps = []
        
        # Introduction step
        intro_step = {
            'type': 'intro',
            'title': f"Introduction to {self.project_path.name}",
            'content': {
                'repo_name': self.project_path.name,
                'total_files': len(analysis['files']),
                'languages': analysis['project_info']['languages']
            }
        }
        
        # Generate narration for intro
        narrated_intro = self.generate_narration(intro_step, VoiceStyle.PROFESSIONAL)
        steps.append(narrated_intro[0])
        
        # Code analysis steps
        for file_path, file_analysis in analysis['files'].items():
            if 'error' not in file_analysis:
                # Create code analysis step
                code_step = {
                    'type': 'code_analysis',
                    'title': f"Analysis of {Path(file_path).name}",
                    'content': file_analysis
                }
                
                # Generate error simulations for this file
                if 'content' in file_analysis:
                    error_simulations = self.generate_error_simulations(
                        file_analysis['content'], num_errors=2
                    )
                    code_step['error_simulations'] = error_simulations
                
                # Generate narration
                narrated_code = self.generate_narration(code_step, VoiceStyle.EDUCATIONAL)
                steps.append(narrated_code[0])
        
        # Step 3: Create video
        video_path = self.video_generator.create_video(steps, [])
        
        logger.info(f"Complete video generated: {video_path}")
        return video_path
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up resources")
        
        # Clean up narration manager
        self.narration_manager.cleanup()
        
        # Clean up video generator
        self.video_generator.cleanup()
        
        logger.info("Cleanup complete")


def main():
    """Main example function."""
    # Example usage of enhanced RepoToVideo
    
    logger.info("=== Enhanced RepoToVideo Example Started ===")
    
    # Verify environment setup first
    logger.info("Verifying environment setup...")
    env_results = verify_environment_setup()
    
    if env_results['overall_status'] == 'FAIL':
        logger.error("Environment verification failed. Please check the logs and fix issues.")
        return
    
    # Test API connections
    logger.info("Testing API connections...")
    api_results = test_api_connections()
    
    # Initialize enhanced system
    logger.info("Initializing enhanced RepoToVideo system...")
    enhanced_system = EnhancedRepoToVideo(".")
    
    try:
        # Example 1: Comprehensive project analysis
        logger.info("=== Example 1: Project Analysis ===")
        analysis = enhanced_system.analyze_project()
        
        print(f"Project Analysis Results:")
        print(f"- Total files: {len(analysis['files'])}")
        print(f"- Languages: {analysis['project_info']['languages']}")
        print(f"- Total errors detected: {len(analysis['error_patterns'])}")
        
        # Example 2: Error simulation
        logger.info("=== Example 2: Error Simulation ===")
        sample_code = """
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count

result = calculate_average([1, 2, 3, 4, 5])
print(result)
"""
        
        error_simulations = enhanced_system.generate_error_simulations(sample_code, num_errors=2)
        
        print(f"Generated {len(error_simulations)} error simulations:")
        for i, simulation in enumerate(error_simulations, 1):
            print(f"  {i}. {simulation.error_type.value}: {simulation.error_message}")
        
        # Example 3: Dynamic execution visualization
        logger.info("=== Example 3: Dynamic Visualization ===")
        viz_path = enhanced_system.create_dynamic_visualization(sample_code)
        print(f"Dynamic visualization created: {viz_path}")
        
        # Example 4: AI Narration
        logger.info("=== Example 4: AI Narration ===")
        content = {
            'type': 'code_analysis',
            'title': 'Sample Code Analysis',
            'content': {
                'language': 'Python',
                'functions': [{'name': 'calculate_average', 'parameters': ['numbers']}],
                'classes': [],
                'imports': []
            }
        }
        
        narrated_content = enhanced_system.generate_narration(content, VoiceStyle.EDUCATIONAL)
        print(f"Generated narration with {len(narrated_content)} audio segments")
        
        # Example 5: Call graph visualization
        logger.info("=== Example 5: Call Graph Visualization ===")
        call_graph = {
            'nodes': ['main', 'calculate_average', 'sum', 'len'],
            'edges': [('main', 'calculate_average'), ('calculate_average', 'sum'), ('calculate_average', 'len')]
        }
        
        call_graph_viz = enhanced_system.create_call_graph_visualization(call_graph)
        print(f"Call graph visualization created: {call_graph_viz}")
        
        # Example 6: Terminal simulation
        logger.info("=== Example 6: Terminal Simulation ===")
        commands = ['python script.py', 'pip install requests', 'python -m pytest']
        outputs = ['Hello, World!', 'Successfully installed requests', '2 passed, 0 failed']
        
        terminal_sim = enhanced_system.create_terminal_simulation(commands, outputs)
        print(f"Terminal simulation created: {terminal_sim}")
        
        # Example 7: Complete video generation
        logger.info("=== Example 7: Complete Video Generation ===")
        # Uncomment the following line to generate a complete video
        # complete_video = enhanced_system.generate_complete_video()
        # print(f"Complete video generated: {complete_video}")
        
        print("\n=== All examples completed successfully! ===")
        
    except Exception as e:
        logger.error(f"Error in example: {e}")
        raise
    finally:
        # Clean up
        enhanced_system.cleanup()


if __name__ == "__main__":
    main() 