# 🎥 RepoToVideo

**Convert GitHub repositories into animated step-by-step video walkthroughs**

RepoToVideo is a complete web application that automatically generates educational video walkthroughs from GitHub repositories. Simply input a repository URL, and the app will create a professional video explaining the codebase structure, functionality, and key concepts.

## ✨ Features

### 🎬 Video Generation
- **1080p HD Quality**: High-resolution video output with professional appearance
- **Multi-language Support**: Generate videos in English, Spanish, French, German, and more
- **Voice Narration**: Natural text-to-speech narration for each step
- **Code Highlighting**: Visual emphasis on important code sections
- **Error Simulation**: Demonstrates common programming errors and fixes

### 🔍 Repository Analysis
- **Smart Content Detection**: Automatically identifies main code files and documentation
- **Structure Analysis**: Analyzes repository organization and file relationships
- **Language Detection**: Supports Python, JavaScript, TypeScript, Java, and many more
- **README Parsing**: Extracts tutorial content and code examples from documentation

### 📋 Step-by-Step Walkthrough
- **Introduction**: Repository overview with metadata and statistics
- **Structure Analysis**: File organization and language breakdown
- **Code Examination**: Detailed analysis of main code files
- **Error Handling**: Common programming mistakes and debugging tips
- **Summary**: Key takeaways and best practices

### 🎤 Voice Features
- **Natural Speech**: High-quality text-to-speech with natural intonation
- **Multiple Languages**: Support for 10+ languages
- **Speed Control**: Normal and slow speech options
- **Code-Friendly**: Optimized pronunciation for programming terms

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)
- Internet connection (for GitHub API and TTS services)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/RepoToVideo.git
   cd RepoToVideo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501` to access the web interface.

### Usage

1. **Enter Repository URL**: Paste a GitHub repository URL (e.g., `https://github.com/scikit-learn/scikit-learn`)

2. **Configure Settings** (Optional):
   - **GitHub Token**: For private repos or higher rate limits
   - **Voice Language**: Choose from 10+ languages
   - **Speech Speed**: Normal or slow
   - **Video Quality**: 1080p, 720p, or 480p

3. **Generate Video**: Click "Generate Video Walkthrough" and wait for processing

4. **Download**: Once complete, download your MP4 video file

## 📁 Project Structure

```
RepoToVideo/
├── app.py                 # Main Streamlit application
├── repo_fetcher.py        # GitHub repository fetching and analysis
├── step_generator.py      # Step-by-step analysis generation
├── voice_generator.py     # Text-to-speech functionality
├── video_generator.py     # Video creation and rendering
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── LICENSE               # Project license
```

## 🔧 Technical Details

### Core Components

#### 1. Repository Fetcher (`repo_fetcher.py`)
- **GitHub API Integration**: Uses PyGitHub for repository access
- **Content Analysis**: Recursively fetches and analyzes repository files
- **Language Detection**: Identifies primary programming languages
- **Structure Mapping**: Creates file hierarchy and relationship maps

#### 2. Step Generator (`step_generator.py`)
- **AST Analysis**: Parses Python code using Abstract Syntax Trees
- **Content Categorization**: Organizes content into logical steps
- **Error Simulation**: Generates realistic programming error scenarios
- **Best Practices**: Extracts coding patterns and recommendations

#### 3. Voice Generator (`voice_generator.py`)
- **gTTS Integration**: Google Text-to-Speech for natural voice generation
- **Text Processing**: Cleans and optimizes text for speech synthesis
- **Multi-language Support**: Handles various languages and accents
- **Code Optimization**: Special handling for programming terminology

#### 4. Video Generator (`video_generator.py`)
- **MoviePy Integration**: Professional video creation and editing
- **Visual Design**: Consistent styling with code-friendly themes
- **Animation Support**: Smooth transitions and visual effects
- **Audio Synchronization**: Perfect timing between visuals and narration

### Supported Languages

#### Programming Languages
- **Python** (.py) - Full AST analysis and execution simulation
- **JavaScript** (.js) - Syntax highlighting and structure analysis
- **TypeScript** (.ts) - Type-aware code analysis
- **Java** (.java) - Class and method structure analysis
- **C/C++** (.c, .cpp, .h) - Header and implementation analysis
- **Ruby** (.rb) - Method and class detection
- **Go** (.go) - Package and function analysis
- **Rust** (.rs) - Module and trait analysis
- **PHP** (.php) - Class and function structure
- **Swift** (.swift) - Protocol and extension analysis
- **Kotlin** (.kt) - Android and JVM code analysis
- **Scala** (.scala) - Functional programming patterns
- **R** (.r) - Statistical computing code
- **Shell** (.sh) - Script analysis and execution flow

#### Documentation Formats
- **Markdown** (.md) - README and documentation parsing
- **Text** (.txt) - Plain text documentation
- **reStructuredText** (.rst) - Sphinx documentation
- **YAML** (.yml, .yaml) - Configuration files
- **JSON** (.json) - Data and configuration files
- **XML** (.xml) - Configuration and data files

### Video Specifications

- **Resolution**: 1920x1080 (1080p), 1280x720 (720p), or 854x480 (480p)
- **Frame Rate**: 30 FPS for smooth playback
- **Format**: MP4 with H.264 codec
- **Audio**: AAC codec with clear narration
- **Duration**: 2-5 minutes depending on repository complexity
- **File Size**: Typically 10-50 MB depending on quality settings

## 🎯 Use Cases

### Educational Content
- **Tutorial Creation**: Generate video tutorials for open-source projects
- **Code Reviews**: Create walkthroughs for code review sessions
- **Onboarding**: Help new developers understand project structure
- **Documentation**: Visual documentation for complex codebases

### Learning and Training
- **Programming Education**: Teach coding concepts through visual examples
- **Workshop Materials**: Create materials for coding workshops
- **Self-Study**: Learn from existing projects with guided walkthroughs
- **Code Analysis**: Understand unfamiliar codebases quickly

### Content Creation
- **YouTube Content**: Generate educational programming videos
- **Course Materials**: Create video content for online courses
- **Presentations**: Visual aids for technical presentations
- **Documentation**: Supplement written documentation with videos

## 🔒 Security and Privacy

### GitHub API Usage
- **Anonymous Access**: Works without authentication for public repositories
- **Rate Limiting**: Respects GitHub API rate limits
- **Token Security**: Optional GitHub tokens are not stored permanently
- **Private Repos**: Supports private repositories with proper authentication

### Code Execution
- **Sandboxed Environment**: Safe code analysis without execution
- **No Code Storage**: Repository contents are not permanently stored
- **Temporary Files**: All temporary files are cleaned up automatically
- **Error Handling**: Graceful handling of malicious or problematic code

## 🛠️ Configuration

### Environment Variables
```bash
# Optional: GitHub Personal Access Token
GITHUB_TOKEN=your_github_token_here

# Optional: Custom output directory
OUTPUT_DIR=/path/to/output/directory

# Optional: TTS language override
TTS_LANGUAGE=en
```

### GitHub Token Setup
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` and `read:user` permissions
3. Copy the token and paste it in the app's GitHub Token field

## 🐛 Troubleshooting

### Common Issues

#### "Repository not found" Error
- Verify the repository URL is correct
- Check if the repository is private (requires GitHub token)
- Ensure the repository exists and is accessible

#### "Rate limit exceeded" Error
- Add a GitHub personal access token
- Wait for rate limit reset (usually 1 hour)
- Use a different GitHub account

#### "Video generation failed" Error
- Check available disk space (requires 100MB+ free space)
- Verify all dependencies are installed correctly
- Check internet connection for TTS services

#### "Audio generation failed" Error
- Check internet connection (required for gTTS)
- Try a different language setting
- Verify text content is not empty

### Performance Optimization

#### For Large Repositories
- Limit analysis to main directories
- Focus on key files only
- Use lower video quality for faster processing

#### For Faster Processing
- Use 720p or 480p video quality
- Select "Normal" speech speed
- Process smaller repositories first

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

### Areas for Contribution
- **Language Support**: Add support for more programming languages
- **Video Effects**: Enhance visual effects and animations
- **Voice Quality**: Improve text-to-speech quality and options
- **UI/UX**: Enhance the Streamlit interface
- **Documentation**: Improve code documentation and examples
- **Testing**: Add comprehensive test coverage

### Code Style
- Follow PEP 8 for Python code
- Add type hints for all functions
- Include docstrings for all classes and methods
- Write clear commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit**: For the amazing web framework
- **PyGitHub**: For GitHub API integration
- **gTTS**: For text-to-speech functionality
- **MoviePy**: For video creation and editing
- **GitHub**: For providing the repository data API

## 📞 Support

- **Issues**: Report bugs and request features on GitHub Issues
- **Discussions**: Join community discussions on GitHub Discussions
- **Email**: Contact the maintainers for private support

## 🔮 Roadmap

### Upcoming Features
- **Advanced Animations**: More sophisticated code visualization
- **Interactive Elements**: Clickable elements in videos
- **Custom Templates**: User-defined video templates
- **Batch Processing**: Generate multiple videos at once
- **Cloud Deployment**: Deploy to cloud platforms
- **API Access**: REST API for programmatic access

### Long-term Goals
- **AI-Powered Analysis**: Machine learning for better code understanding
- **Multi-platform Support**: Desktop and mobile applications
- **Real-time Collaboration**: Collaborative video creation
- **Advanced Editing**: Post-production video editing tools
- **Analytics**: Video performance and engagement metrics

---

**Made with ❤️ by the RepoToVideo team**

*Transform your GitHub repositories into engaging educational videos!* 