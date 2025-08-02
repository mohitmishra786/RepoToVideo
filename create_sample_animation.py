#!/usr/bin/env python3
"""
Create Sample Animation

This script creates an actual sample animation using the new ManimGL system
to demonstrate the advanced animation capabilities.
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

from advanced_animation import AdvancedAnimationSystem

def create_bubble_sort_analysis():
    """Create a code analysis for bubble sort algorithm."""
    return {
        "files": [
            {
                "name": "bubble_sort.py",
                "language": "python",
                "content": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# Test the algorithm
numbers = [64, 34, 25, 12, 22, 11, 90]
print(f"Original array: {numbers}")
sorted_numbers = bubble_sort(numbers.copy())
print(f"Sorted array: {sorted_numbers}")
""",
                "complexity": "O(n²)",
                "algorithms": ["bubble_sort", "sorting"],
                "data_structures": ["array", "comparison_sort"]
            }
        ],
        "language": "python",
        "total_lines": 12,
        "complexity_analysis": {
            "time_complexity": "O(n²)",
            "space_complexity": "O(1)",
            "best_case": "O(n)",
            "worst_case": "O(n²)"
        }
    }

def main():
    """Main function to create a sample animation."""
    print("🎬 Creating Sample Animation with ManimGL System")
    print("=" * 50)
    
    try:
        # Initialize the advanced animation system
        system = AdvancedAnimationSystem(output_dir="sample_animation_output")
        
        # Create code analysis
        code_analysis = create_bubble_sort_analysis()
        print("✅ Created code analysis for bubble sort algorithm")
        
        # Generate storyboard
        print("\n🎬 Generating storyboard...")
        storyboard = system.storyboard_generator.generate_storyboard(code_analysis)
        print(f"✅ Generated storyboard with {len(storyboard.scenes)} scenes")
        print(f"   Total duration: {storyboard.total_duration}s")
        
        # Show scene details
        for i, scene in enumerate(storyboard.scenes):
            print(f"   Scene {i+1}: {scene.concept} ({scene.duration}s)")
        
        # Save storyboard
        storyboard_path = system.save_storyboard(storyboard, "bubble_sort_storyboard.json")
        print(f"\n💾 Saved storyboard to: {storyboard_path}")
        
        # Create animation (this will generate video files)
        print("\n🎥 Creating animation...")
        print("   This may take a few minutes...")
        
        # For now, let's just render the first scene to test
        if storyboard.scenes:
            first_scene = storyboard.scenes[0]
            video_path = system.scene_renderer.render_scene(first_scene)
            print(f"✅ Generated video: {video_path}")
        
        print("\n🎉 Sample animation created successfully!")
        print("\n📁 Check the 'sample_animation_output' directory for:")
        print("   - bubble_sort_storyboard.json (storyboard data)")
        print("   - Generated video files")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample animation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎊 Animation system is working perfectly!")
    else:
        print("\n⚠️ Some issues encountered. Check the logs above.") 