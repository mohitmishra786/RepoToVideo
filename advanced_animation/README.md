# Advanced Animation System

A modular system for creating 3Blue1Brown-style educational animations from code repositories using ManimGL and AI-powered storyboarding.

## 🏗️ Architecture

The system is organized into modular components for easy maintenance and extensibility:

```
advanced_animation/
├── __init__.py                 # Main package entry point
├── core/                       # Core functionality
│   ├── __init__.py
│   ├── data_structures.py     # Data classes and structures
│   ├── storyboard_generator.py # AI-powered storyboard generation
│   └── execution_capture.py   # Runtime execution tracing
├── visualizations/             # Visual components
│   ├── __init__.py
│   └── visual_metaphors.py    # Visual metaphor library
├── rendering/                  # Rendering components
│   ├── __init__.py
│   └── manim_scene.py         # ManimGL scene rendering
└── README.md                   # This file
```

## 🚀 Quick Start

### Basic Usage

```python
from advanced_animation import create_animation, generate_storyboard

# Sample code analysis
code_analysis = {
    "files": ["algorithm.py"],
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

# Create animation (requires OpenAI API key for AI features)
video_path = create_animation(code_analysis, openai_api_key="your-key-here")
```

### Advanced Usage

```python
from advanced_animation import AdvancedAnimationSystem

# Initialize the system
system = AdvancedAnimationSystem(
    openai_api_key="your-openai-key",
    output_dir="my_animations"
)

# Create animation with execution capture
video_path = system.create_animation_from_code(
    code_analysis,
    capture_execution=True
)

# Save storyboard for later use
system.save_storyboard(storyboard, "my_storyboard.json")

# Load storyboard
loaded_storyboard = system.load_storyboard("my_storyboard.json")
```

## 📦 Core Components

### 1. Data Structures (`core/data_structures.py`)

Defines the fundamental data classes used throughout the system:

- `VisualElement`: Represents visual elements in animations
- `AnimationStep`: Defines animation actions and parameters
- `CameraMovement`: Camera positioning and movement
- `StoryboardScene`: Individual scenes in the storyboard
- `Storyboard`: Complete storyboard with multiple scenes
- `ExecutionState`: Runtime execution state capture
- `ExecutionTrace`: Complete execution history

### 2. Storyboard Generator (`core/storyboard_generator.py`)

AI-powered storyboard generation using GPT-4:

- Converts code analysis into visual storyboards
- Supports both AI-generated and rule-based storyboards
- Creates scenes with visual metaphors and animations
- Handles fallback when AI is not available

### 3. Execution Capture (`core/execution_capture.py`)

Runtime execution tracing using E2B sandbox:

- Captures variable states during execution
- Records call stack and execution flow
- Supports Python, JavaScript, and Java
- Provides simulation fallback when E2B is unavailable

### 4. Visual Metaphors (`visualizations/visual_metaphors.py`)

Library of visual metaphors for different data structures:

- Arrays as rectangles
- Trees as hierarchical structures
- Graphs as network diagrams
- Stacks and queues
- Sorting and searching visualizations
- Complexity analysis graphs

### 5. ManimGL Rendering (`rendering/manim_scene.py`)

ManimGL scene creation and rendering:

- Converts storyboards into ManimGL scenes
- Handles animation sequences
- Manages camera movements
- Provides fallback video generation

## 🔧 Installation

### Prerequisites

1. **Python 3.8+**
2. **ManimGL** (for advanced animations)
3. **OpenAI API Key** (for AI-powered storyboarding)
4. **E2B API Key** (for runtime execution capture)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Optional Dependencies

- **ManimGL**: For 3Blue1Brown-style animations
- **E2B**: For runtime execution capture
- **OpenAI**: For AI-powered storyboard generation

## 🧪 Testing

Run the test suite to verify the system works correctly:

```bash
python test_advanced_system.py
```

The test suite covers:
- Data structure creation
- Storyboard generation
- Execution capture
- Visual metaphor creation
- System integration
- Save/load functionality

## 📋 API Reference

### Main Functions

#### `create_animation(code_analysis, openai_api_key=None, output_dir="advanced_output")`
Creates a complete animation from code analysis.

**Parameters:**
- `code_analysis` (dict): Code analysis results
- `openai_api_key` (str, optional): OpenAI API key for AI features
- `output_dir` (str): Output directory for generated files

**Returns:**
- `str`: Path to the generated video file

#### `generate_storyboard(code_analysis, openai_api_key=None)`
Generates a storyboard from code analysis.

**Parameters:**
- `code_analysis` (dict): Code analysis results
- `openai_api_key` (str, optional): OpenAI API key for AI features

**Returns:**
- `Storyboard`: Generated storyboard object

#### `capture_execution(code_content, language="python")`
Captures execution trace of code.

**Parameters:**
- `code_content` (str): Source code to execute
- `language` (str): Programming language

**Returns:**
- `ExecutionTrace`: Execution trace object

### Classes

#### `AdvancedAnimationSystem`
Main orchestrator for the animation system.

**Methods:**
- `create_animation_from_code(code_analysis, capture_execution=True)`
- `save_storyboard(storyboard, filename)`
- `load_storyboard(filepath)`

#### `StoryboardGenerator`
AI-powered storyboard generator.

**Methods:**
- `generate_storyboard(code_analysis)`
- `save_storyboard(storyboard, output_path)`
- `load_storyboard(file_path)`

#### `RuntimeStateCapture`
Runtime execution state capture.

**Methods:**
- `capture_execution(code_content, language)`

#### `VisualMetaphorLibrary`
Visual metaphor creation library.

**Methods:**
- `create_visual_element(element)`

#### `ManimSceneRenderer`
ManimGL scene rendering.

**Methods:**
- `render_scene(storyboard_scene)`

## 🎨 Customization

### Adding New Visual Metaphors

1. Extend the `VisualMetaphorLibrary` class
2. Add new metaphor creation methods
3. Register them in the `metaphors` dictionary

```python
class CustomVisualMetaphorLibrary(VisualMetaphorLibrary):
    def create_custom_metaphor(self, element):
        # Your custom visualization logic
        pass
    
    def __init__(self):
        super().__init__()
        self.metaphors["custom_type"] = self.create_custom_metaphor
```

### Custom Animation Actions

1. Extend the `AdvancedManimScene` class
2. Add new animation creation methods
3. Handle them in the `create_animation` method

### Custom Storyboard Generation

1. Extend the `StoryboardGenerator` class
2. Override the `_generate_fallback_storyboard` method
3. Implement your custom storyboard logic

## 🐛 Troubleshooting

### Common Issues

1. **ManimGL Import Error**: Install ManimGL or use fallback rendering
2. **OpenAI API Error**: Check API key or use rule-based generation
3. **E2B Import Error**: Install E2B or use simulation mode
4. **Rendering Timeout**: Increase timeout or reduce scene complexity

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Fallback Modes

The system gracefully degrades when dependencies are missing:
- **No ManimGL**: Uses MoviePy fallback rendering
- **No OpenAI**: Uses rule-based storyboard generation
- **No E2B**: Uses execution simulation

## 📈 Performance

### Optimization Tips

1. **Reduce scene complexity** for faster rendering
2. **Use lower quality settings** for preview
3. **Cache storyboards** to avoid regeneration
4. **Parallel rendering** for multiple scenes

### Memory Usage

- Large codebases may require more memory
- Consider processing in chunks
- Monitor memory usage during execution capture

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

### Development Setup

```bash
git clone <repository>
cd advanced_animation
pip install -e .
python test_advanced_system.py
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **3Blue1Brown** for inspiration and animation style
- **ManimGL** for the animation engine
- **OpenAI** for GPT-4 integration
- **E2B** for runtime execution capture

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test suite
3. Open an issue on GitHub
4. Check the documentation

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Python Version**: 3.8+ 