#!/usr/bin/env python3
"""
Test Real Repository Animation

This script tests our ManimGL system with real GitHub repositories
to generate animations from actual code.
"""

import os
import sys
import logging
from pathlib import Path
import argparse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import logging utilities
from advanced_animation.utils.logging_config import setup_logging_for_run, get_logger

# Setup logging for this run
logging_manager = setup_logging_for_run("logs", logging.INFO)
logger = get_logger(__name__)

from advanced_animation import AdvancedAnimationSystem
from code_analysis import EnhancedCodeAnalyzer
from repo_fetcher import RepoFetcher
import tempfile
import subprocess

"""
    Performs fetch_repository operation. Function may throw exceptions, may return early, has side effects. Takes repo_url as input. Returns a string value.
    :param repo_url: The repo_url string.
    :return: String value
    :raises Call: Thrown when call occurs.
"""
def fetch_repository(repo_url: str) -> str:
    """Wrapper function to fetch a repository."""
    # Create a temporary directory for the repository
    temp_dir = tempfile.mkdtemp(prefix="repo_")
    
    # Clone the repository using git
    try:
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True, capture_output=True)
        return temp_dir
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to clone repository: {e}")

"""
    Performs analyze_repository operation. Function has side effects. Takes repo_path as input. Returns a object value.
    :param repo_path: The repo_path string.
    :return: Value of type object
"""
def analyze_repository(repo_path: str):
    """Wrapper function to analyze a repository."""
    analyzer = EnhancedCodeAnalyzer(repo_path)
    return analyzer.analyze_project()

"""
    Performs analyze_github_repo operation. Function iterates over data, conditionally processes input, may return early, has side effects, performs arithmetic operations. Takes repo_url and output_dir as input. Returns a object value.
    :param repo_url: The repo_url string.
    :param output_dir: The output_dir string.
    :return: Value of type object
"""
def analyze_github_repo(repo_url: str, output_dir: str = "real_repo_output"):
    """Analyze a GitHub repository and create animations."""
    print(f"🎬 Testing Real Repository: {repo_url}")
    print("=" * 60)
    
    try:
        # Initialize the advanced animation system
        system = AdvancedAnimationSystem(output_dir=output_dir)
        
        # Fetch and analyze the repository
        print("📥 Fetching repository...")
        repo_path = fetch_repository(repo_url)
        print(f"✅ Repository fetched to: {repo_path}")
        
        print("\n🔍 Analyzing repository...")
        code_analysis = analyze_repository(repo_path)
        print(f"✅ Analysis complete: {len(code_analysis.get('files', []))} files analyzed")
        
        # Show analysis summary
        print("\n📊 Analysis Summary:")
        print(f"   Total files: {len(code_analysis.get('files', []))}")
        print(f"   Languages: {code_analysis.get('languages', [])}")
        print(f"   Total lines: {code_analysis.get('total_lines', 0)}")
        
        # Show detailed file analysis
        files = code_analysis.get('files', {})
        if files:
            print(f"\n📁 Detailed File Analysis ({len(files)} files):")
            
            successful_files = 0
            failed_files = 0
            
            for i, (file_path, file_info) in enumerate(files.items()):
                language = file_info.get('language', 'Unknown')
                lines = file_info.get('lines', 0)
                functions = len(file_info.get('functions', []))
                classes = len(file_info.get('classes', []))
                has_error = 'analysis_error' in file_info
                
                if has_error:
                    failed_files += 1
                    print(f"   ❌ {i+1}. {file_path} ({language}) - {lines} lines, {functions} functions, {classes} classes")
                    print(f"      Error: {file_info.get('analysis_error', 'Unknown error')}")
                else:
                    successful_files += 1
                    print(f"   ✅ {i+1}. {file_path} ({language}) - {lines} lines, {functions} functions, {classes} classes")
            
            print(f"\n📈 Analysis Results:")
            print(f"   ✅ Successfully analyzed: {successful_files} files")
            print(f"   ❌ Failed to analyze: {failed_files} files")
            print(f"   📊 Success rate: {(successful_files/len(files)*100):.1f}%")
        
        # Generate storyboard
        print("\n🎬 Generating storyboard...")
        storyboard = system.storyboard_generator.generate_storyboard(code_analysis)
        print(f"✅ Generated storyboard with {len(storyboard.scenes)} scenes")
        print(f"   Total duration: {storyboard.total_duration}s")
        
        # Show scene details
        print("\n🎭 Scenes:")
        for i, scene in enumerate(storyboard.scenes):
            print(f"   Scene {i+1}: {scene.concept} ({scene.duration}s)")
        
        # Save storyboard
        storyboard_path = system.save_storyboard(storyboard, f"{repo_url.split('/')[-1]}_storyboard.json")
        print(f"\n💾 Saved storyboard to: {storyboard_path}")
        
        # Create animations with audio generation
        print("\n🎥 Creating animations with audio...")
        print("   This may take several minutes...")
        
        try:
            # Use the full animation system which includes audio generation
            final_video_path = system.create_animation_from_code(code_analysis)
            print(f"   ✅ Complete animation created: {final_video_path}")
            return True
        except Exception as e:
            print(f"   ❌ Animation creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print(f"\n🎉 Animation creation completed!")
        print(f"📁 Check the '{output_dir}' directory for:")
        print(f"   - {repo_url.split('/')[-1]}_storyboard.json (storyboard data)")
        print(f"   - Generated individual scene videos")
        print(f"   - final_video/ (merged comprehensive video)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing repository: {e}")
        import traceback
        traceback.print_exc()
        return False

"""
    Performs main operation. Function conditionally processes input, may return early, has side effects. Returns a object value.
    :return: Value of type object
"""
def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test ManimGL system with real repositories")
    parser.add_argument("repo_url", help="GitHub repository URL (e.g., https://github.com/user/repo)")
    parser.add_argument("--output", "-o", default="real_repo_output", 
                       help="Output directory (default: real_repo_output)")
    
    args = parser.parse_args()
    
    # Validate repository URL
    if not args.repo_url.startswith("https://github.com/"):
        print("❌ Please provide a valid GitHub repository URL")
        print("   Example: https://github.com/user/repo")
        return
    
    # Process the repository
    success = analyze_github_repo(args.repo_url, args.output)
    
    if success:
        print("\n🎊 Repository animation test completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Check the generated videos in the output directory")
        print("   2. Try different repositories with various algorithms")
        print("   3. Customize the animation parameters")
    else:
        print("\n⚠️ Some issues encountered. Check the logs above.")

if __name__ == "__main__":
    # If no arguments provided, show usage
    if len(sys.argv) == 1:
        print("🎬 Real Repository Animation Test")
        print("=" * 50)
        print("Usage: python test_real_repository.py <github_repo_url>")
        print("\nExamples:")
        print("  python test_real_repository.py https://github.com/algorithm-visualizer/algorithm-visualizer")
        print("  python test_real_repository.py https://github.com/TheAlgorithms/Python")
        print("  python test_real_repository.py https://github.com/trekhleb/javascript-algorithms")
        print("\nOr run with specific output directory:")
        print("  python test_real_repository.py https://github.com/user/repo --output my_animations")
        print("\n💡 Choose repositories with interesting algorithms for best results!")
    else:
        main() 