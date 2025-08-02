#!/usr/bin/env python3
"""
ManimGL Demo Test

This script tests the new ManimGL setup with actual animations
to demonstrate the advanced animation system working.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_animation import (
    AdvancedAnimationSystem, create_animation, generate_storyboard,
    capture_execution, Storyboard, StoryboardScene
)

def test_manimgl_import():
    """Test if ManimGL is working."""
    print("🔍 Testing ManimGL Import...")
    
    try:
        import manimlib
        print("✅ ManimGL imported successfully!")
        return True
    except Exception as e:
        print(f"❌ ManimGL import failed: {e}")
        return False

def test_manim_import():
    """Test if Manim Community Edition is working."""
    print("🔍 Testing Manim Community Edition Import...")
    
    try:
        import manim
        print("✅ Manim Community Edition imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Manim Community Edition import failed: {e}")
        return False

def create_sample_code_analysis():
    """Create a sample code analysis for testing."""
    return {
        "files": [
            {
                "name": "quicksort.py",
                "language": "python",
                "content": """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# Test the algorithm
numbers = [3, 6, 8, 10, 1, 2, 1]
sorted_numbers = quicksort(numbers)
print(f"Original: {numbers}")
print(f"Sorted: {sorted_numbers}")
""",
                "complexity": "O(n log n)",
                "algorithms": ["quicksort", "divide_and_conquer"],
                "data_structures": ["array", "recursion"]
            }
        ],
        "language": "python",
        "total_lines": 15,
        "complexity_analysis": {
            "time_complexity": "O(n log n)",
            "space_complexity": "O(log n)",
            "best_case": "O(n log n)",
            "worst_case": "O(n²)"
        }
    }

def test_storyboard_generation():
    """Test storyboard generation with the new system."""
    print("\n🎬 Testing Storyboard Generation...")
    
    try:
        code_analysis = create_sample_code_analysis()
        storyboard = generate_storyboard(code_analysis)
        
        print(f"✅ Storyboard generated successfully!")
        print(f"   Title: {storyboard.title}")
        print(f"   Scenes: {len(storyboard.scenes)}")
        print(f"   Duration: {storyboard.total_duration}s")
        
        # Show scene details
        for i, scene in enumerate(storyboard.scenes[:3]):  # Show first 3 scenes
            print(f"   Scene {i+1}: {scene.concept} ({scene.duration}s)")
        
        return storyboard
        
    except Exception as e:
        print(f"❌ Storyboard generation failed: {e}")
        return None

def test_visual_metaphors():
    """Test visual metaphor creation."""
    print("\n🎨 Testing Visual Metaphors...")
    
    try:
        from advanced_animation.visualizations.visual_metaphors import VisualMetaphorLibrary
        from advanced_animation.core.data_structures import VisualElement
        
        library = VisualMetaphorLibrary()
        
        # Test different visual elements
        test_elements = [
            VisualElement(
                type="rectangle_array",
                properties={"values": [3, 1, 4, 1, 5]},
                position={"x": 0, "y": 0, "z": 0},
                color="#ff7f0e"
            ),
            VisualElement(
                type="hierarchical_tree",
                properties={"values": [1, 2, 3, 4, 5]},
                position={"x": 0, "y": 0, "z": 0},
                color="#2ca02c"
            )
        ]
        
        for element in test_elements:
            result = library.create_visual_element(element)
            print(f"✅ Created {element.type} successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Visual metaphor creation failed: {e}")
        return False

def test_rendering_pipeline():
    """Test the rendering pipeline."""
    print("\n🎥 Testing Rendering Pipeline...")
    
    try:
        from advanced_animation.rendering.manim_scene import ManimSceneRenderer
        from advanced_animation.core.data_structures import StoryboardScene, CameraMovement
        
        # Create a simple test scene
        test_scene = StoryboardScene(
            id=1,
            concept="Test Animation",
            visual_elements=[],
            animation_sequence=[],
            narration="This is a test animation.",
            duration=5.0,
            camera_movement=CameraMovement()
        )
        
        renderer = ManimSceneRenderer("test_output")
        
        # Test scene file creation
        scene_file = renderer.create_scene_file(test_scene)
        print(f"✅ Scene file created: {scene_file}")
        
        # Clean up
        if scene_file.exists():
            scene_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Rendering pipeline test failed: {e}")
        return False

def test_full_system():
    """Test the complete system integration."""
    print("\n🚀 Testing Full System Integration...")
    
    try:
        system = AdvancedAnimationSystem(output_dir="demo_output")
        
        code_analysis = create_sample_code_analysis()
        
        # Test storyboard generation
        storyboard = system.storyboard_generator.generate_storyboard(code_analysis)
        print(f"✅ Generated storyboard with {len(storyboard.scenes)} scenes")
        
        # Test execution capture
        execution_trace = system.execution_capture.capture_execution(
            code_analysis["files"][0]["content"], 
            "python"
        )
        print(f"✅ Captured execution with {len(execution_trace.states)} states")
        
        # Test save/load
        saved_path = system.save_storyboard(storyboard, "demo_storyboard.json")
        print(f"✅ Saved storyboard to: {saved_path}")
        
        loaded_storyboard = system.load_storyboard(saved_path)
        print(f"✅ Loaded storyboard with {len(loaded_storyboard.scenes)} scenes")
        
        return True
        
    except Exception as e:
        print(f"❌ Full system test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🎬 ManimGL Advanced Animation System Demo")
    print("=" * 50)
    
    # Test imports
    manimgl_working = test_manimgl_import()
    manim_working = test_manim_import()
    
    if not manimgl_working and not manim_working:
        print("❌ Neither ManimGL nor Manim is working!")
        return
    
    # Test components
    tests = [
        ("Storyboard Generation", test_storyboard_generation),
        ("Visual Metaphors", test_visual_metaphors),
        ("Rendering Pipeline", test_rendering_pipeline),
        ("Full System Integration", test_full_system)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Demo Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎉 {passed}/{len(results)} tests passed!")
    
    if passed == len(results):
        print("🎊 All systems are working perfectly!")
        print("\n💡 Next steps:")
        print("   1. Create a sample animation with: python -c \"from advanced_animation import create_animation; create_animation(your_code_analysis)\"")
        print("   2. Check the 'demo_output' directory for generated files")
        print("   3. Run the main app: python app.py")
    else:
        print("⚠️ Some components need attention.")

if __name__ == "__main__":
    main() 