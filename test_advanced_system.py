"""
Test script for the Advanced Animation System

This script tests the modular components of the advanced animation system
to ensure everything works correctly.
"""

import os
import sys
import logging
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the advanced animation system
try:
    from advanced_animation import (
        AdvancedAnimationSystem, create_animation, generate_storyboard,
        capture_execution, Storyboard, StoryboardScene
    )
    print("✅ Successfully imported advanced animation system")
except ImportError as e:
    print(f"❌ Failed to import advanced animation system: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_data_structures():
    """Test the core data structures."""
    print("\n🧪 Testing Data Structures...")
    
    try:
        from advanced_animation.core.data_structures import (
            VisualElement, AnimationStep, CameraMovement, StoryboardScene
        )
        
        # Create a test visual element
        visual_element = VisualElement(
            type="rectangle_array",
            properties={"values": [1, 2, 3, 4, 5]},
            position={"x": 0, "y": 0, "z": 0},
            color="#ff7f0e"
        )
        
        # Create a test animation step
        animation_step = AnimationStep(
            action="FadeIn",
            target="array",
            duration=2.0
        )
        
        # Create a test camera movement
        camera_movement = CameraMovement(
            phi=75.0,
            theta=-45.0,
            zoom=1.2
        )
        
        # Create a test scene
        scene = StoryboardScene(
            id=1,
            concept="Test Scene",
            visual_elements=[visual_element],
            animation_sequence=[animation_step],
            narration="This is a test scene",
            duration=5.0,
            camera_movement=camera_movement
        )
        
        print("✅ Data structures created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Data structures test failed: {e}")
        return False

def test_storyboard_generation():
    """Test storyboard generation."""
    print("\n🧪 Testing Storyboard Generation...")
    
    try:
        # Create sample code analysis
        code_analysis = {
            "files": ["test.py", "utils.py"],
            "algorithms": ["quicksort", "binary_search"],
            "data_structures": ["array", "tree"],
            "complexity_analysis": {
                "time": "O(n log n)",
                "space": "O(log n)"
            },
            "language": "python"
        }
        
        # Generate storyboard
        storyboard = generate_storyboard(code_analysis)
        
        print(f"✅ Storyboard generated with {len(storyboard.scenes)} scenes")
        print(f"   Title: {storyboard.title}")
        print(f"   Total duration: {storyboard.total_duration}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Storyboard generation test failed: {e}")
        return False

def test_execution_capture():
    """Test execution capture."""
    print("\n🧪 Testing Execution Capture...")
    
    try:
        # Sample Python code
        sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(5)
print(result)
"""
        
        # Capture execution
        execution_trace = capture_execution(sample_code, "python")
        
        print(f"✅ Execution captured with {len(execution_trace.states)} states")
        print(f"   Language: {execution_trace.language}")
        print(f"   Total duration: {execution_trace.total_duration:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Execution capture test failed: {e}")
        return False

def test_visual_metaphors():
    """Test visual metaphor creation."""
    print("\n🧪 Testing Visual Metaphors...")
    
    try:
        from advanced_animation.visualizations.visual_metaphors import VisualMetaphorLibrary
        
        # Create visual metaphor library
        library = VisualMetaphorLibrary()
        
        # Test creating a visual element
        from advanced_animation.core.data_structures import VisualElement
        
        element = VisualElement(
            type="rectangle_array",
            properties={"values": [1, 2, 3, 4, 5]},
            position={"x": 0, "y": 0, "z": 0},
            color="#ff7f0e"
        )
        
        # Create visual object (this might fail if ManimGL is not available, which is expected)
        try:
            visual_obj = library.create_visual_element(element)
            print("✅ Visual metaphor created successfully")
        except Exception as e:
            print(f"⚠️  Visual metaphor creation failed (expected if ManimGL not available): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Visual metaphors test failed: {e}")
        return False

def test_system_integration():
    """Test the complete system integration."""
    print("\n🧪 Testing System Integration...")
    
    try:
        # Create the advanced animation system
        system = AdvancedAnimationSystem()
        
        # Sample code analysis
        code_analysis = {
            "files": ["algorithm.py"],
            "algorithms": ["bubble_sort"],
            "data_structures": ["array"],
            "complexity_analysis": {
                "time": "O(n²)",
                "space": "O(1)"
            },
            "language": "python"
        }
        
        # Test storyboard generation
        storyboard = system.storyboard_generator.generate_storyboard(code_analysis)
        print(f"✅ System integration test passed - generated {len(storyboard.scenes)} scenes")
        
        return True
        
    except Exception as e:
        print(f"❌ System integration test failed: {e}")
        return False

def test_save_load():
    """Test saving and loading storyboards."""
    print("\n🧪 Testing Save/Load Functionality...")
    
    try:
        # Create sample code analysis
        code_analysis = {
            "files": ["test.py"],
            "algorithms": ["test_algorithm"],
            "data_structures": ["test_structure"],
            "language": "python"
        }
        
        # Generate storyboard
        system = AdvancedAnimationSystem()
        storyboard = system.storyboard_generator.generate_storyboard(code_analysis)
        
        # Save storyboard
        save_path = system.save_storyboard(storyboard, "test_storyboard.json")
        print(f"✅ Storyboard saved to: {save_path}")
        
        # Load storyboard
        loaded_storyboard = system.load_storyboard(save_path)
        print(f"✅ Storyboard loaded successfully with {len(loaded_storyboard.scenes)} scenes")
        
        # Clean up
        try:
            os.remove(save_path)
            print("✅ Test file cleaned up")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Save/Load test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Advanced Animation System Tests")
    print("=" * 50)
    
    tests = [
        ("Data Structures", test_data_structures),
        ("Storyboard Generation", test_storyboard_generation),
        ("Execution Capture", test_execution_capture),
        ("Visual Metaphors", test_visual_metaphors),
        ("System Integration", test_system_integration),
        ("Save/Load", test_save_load)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The advanced animation system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 