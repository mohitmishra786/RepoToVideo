"""
AI Narration System

This module provides AI-powered narration capabilities including:
- ElevenLabs API integration for high-quality voice synthesis
- Context-aware script generation
- Audio-video synchronization
- Multi-language support
"""

import os
import json
import logging
import tempfile
import requests
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import hashlib
from pathlib import Path


logger = logging.getLogger(__name__)


class VoiceStyle(Enum):
    """Available voice styles for narration."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    EDUCATIONAL = "educational"
    TECHNICAL = "technical"
    CASUAL = "casual"


class Language(Enum):
    """Supported languages for narration."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    JAPANESE = "ja"
    KOREAN = "ko"
    CHINESE = "zh"


@dataclass
class NarrationConfig:
    """Configuration for narration generation."""
    voice_id: str
    voice_style: VoiceStyle
    language: Language
    speed: float = 1.0
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0
    use_speaker_boost: bool = True


@dataclass
class ScriptSegment:
    """Represents a segment of the narration script."""
    content: str
    duration: float
    start_time: float
    end_time: float
    context: Dict[str, Any]
    audio_file: Optional[str] = None


class AINarrator:
    """AI-powered narrator with ElevenLabs integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI narrator.
        
        Args:
            api_key: ElevenLabs API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            logger.warning("No ElevenLabs API key provided. Narration will be limited.")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.voices_cache = {}
        self.script_cache = {}
        
        # Default voice configurations
        self.default_voices = {
            VoiceStyle.PROFESSIONAL: "21m00Tcm4TlvDq8ikWAM",  # Rachel
            VoiceStyle.FRIENDLY: "AZnzlk1XvdvUeBnXmlld",      # Domi
            VoiceStyle.EDUCATIONAL: "EXAVITQu4vr4xnSDxMaL",   # Bella
            VoiceStyle.TECHNICAL: "VR6AewLTigWG4xSOukaG",     # Arnold
            VoiceStyle.CASUAL: "pNInz6obpgDQGcFmaJgB"        # Adam
        }
        
        # Language-specific voice mappings
        self.language_voices = {
            Language.SPANISH: "ErXwobaYiN019PkySvjV",
            Language.FRENCH: "yoZ06aMxZJJ28mfd3POQ",
            Language.GERMAN: "VR6AewLTigWG4xSOukaG",
            Language.ITALIAN: "pNInz6obpgDQGcFmaJgB",
            Language.PORTUGUESE: "21m00Tcm4TlvDq8ikWAM",
            Language.JAPANESE: "AZnzlk1XvdvUeBnXmlld",
            Language.KOREAN: "EXAVITQu4vr4xnSDxMaL",
            Language.CHINESE: "VR6AewLTigWG4xSOukaG"
        }
    
    def generate_narration_script(self, content: Dict[str, Any], config: NarrationConfig) -> List[ScriptSegment]:
        """
        Generate a narration script based on content and configuration.
        
        Args:
            content: Content to narrate (repository analysis, code, etc.)
            config: Narration configuration
            
        Returns:
            List of script segments
        """
        logger.info("Generating narration script")
        
        # Check cache first
        cache_key = self._generate_cache_key(content, config)
        if cache_key in self.script_cache:
            logger.info("Using cached script")
            return self.script_cache[cache_key]
        
        segments = []
        current_time = 0.0
        
        # Generate script based on content type
        if 'type' in content:
            if content['type'] == 'intro':
                segments.extend(self._generate_intro_script(content, config))
            elif content['type'] == 'code_analysis':
                segments.extend(self._generate_code_analysis_script(content, config))
            elif content['type'] == 'error_simulation':
                segments.extend(self._generate_error_simulation_script(content, config))
            elif content['type'] == 'overview':
                segments.extend(self._generate_overview_script(content, config))
            else:
                segments.extend(self._generate_generic_script(content, config))
        else:
            segments.extend(self._generate_generic_script(content, config))
        
        # Calculate timing for segments
        for segment in segments:
            segment.start_time = current_time
            segment.duration = self._estimate_duration(segment.content, config.speed)
            segment.end_time = current_time + segment.duration
            current_time = segment.end_time
        
        # Cache the result
        self.script_cache[cache_key] = segments
        
        return segments
    
    def _generate_intro_script(self, content: Dict[str, Any], config: NarrationConfig) -> List[ScriptSegment]:
        """Generate introduction script."""
        repo_name = content.get('repo_name', 'this repository')
        owner = content.get('owner', 'the developer')
        language = content.get('language', 'code')
        stars = content.get('stars', 0)
        forks = content.get('forks', 0)
        
        script_parts = [
            f"Welcome to this walkthrough of {repo_name}, a {language} project by {owner}.",
            f"This repository has {stars} stars and {forks} forks, making it a popular choice in the community.",
            "Let's explore what makes this project interesting and how it works under the hood."
        ]
        
        segments = []
        for part in script_parts:
            segments.append(ScriptSegment(
                content=part,
                duration=0.0,  # Will be calculated later
                start_time=0.0,
                end_time=0.0,
                context={'type': 'intro', 'part': script_parts.index(part)}
            ))
        
        return segments
    
    def _generate_code_analysis_script(self, content: Dict[str, Any], config: NarrationConfig) -> List[ScriptSegment]:
        """Generate code analysis script."""
        language = content.get('language', 'Python')
        functions = content.get('functions', [])
        classes = content.get('classes', [])
        imports = content.get('imports', [])
        
        script_parts = [
            f"This {language} file contains {len(functions)} functions and {len(classes)} classes.",
        ]
        
        if functions:
            func_names = [f['name'] for f in functions[:3]]  # Show first 3 functions
            script_parts.append(f"The main functions include {', '.join(func_names)}.")
        
        if classes:
            class_names = [c['name'] for c in classes[:2]]  # Show first 2 classes
            script_parts.append(f"The classes are {', '.join(class_names)}.")
        
        if imports:
            script_parts.append(f"The code imports {len(imports)} modules for various functionalities.")
        
        script_parts.append("Let's examine the key components and understand how they work together.")
        
        segments = []
        for part in script_parts:
            segments.append(ScriptSegment(
                content=part,
                duration=0.0,
                start_time=0.0,
                end_time=0.0,
                context={'type': 'code_analysis', 'part': script_parts.index(part)}
            ))
        
        return segments
    
    def _generate_error_simulation_script(self, content: Dict[str, Any], config: NarrationConfig) -> List[ScriptSegment]:
        """Generate error simulation script."""
        error_type = content.get('error_type', 'an error')
        error_message = content.get('error_message', '')
        explanation = content.get('explanation', '')
        
        script_parts = [
            f"Now let's look at a common {error_type} that developers might encounter.",
            f"When we run this code, we get the error: {error_message}",
            explanation,
            "Here's how to fix this issue and prevent it in the future."
        ]
        
        segments = []
        for part in script_parts:
            segments.append(ScriptSegment(
                content=part,
                duration=0.0,
                start_time=0.0,
                end_time=0.0,
                context={'type': 'error_simulation', 'part': script_parts.index(part)}
            ))
        
        return segments
    
    def _generate_overview_script(self, content: Dict[str, Any], config: NarrationConfig) -> List[ScriptSegment]:
        """Generate overview script."""
        description = content.get('description', 'This project')
        readme_title = content.get('readme_title', '')
        
        script_parts = [
            f"Let's start by looking at the README file. {readme_title} provides a comprehensive overview.",
            description,
            "The documentation includes several code examples that demonstrate key functionality."
        ]
        
        segments = []
        for part in script_parts:
            segments.append(ScriptSegment(
                content=part,
                duration=0.0,
                start_time=0.0,
                end_time=0.0,
                context={'type': 'overview', 'part': script_parts.index(part)}
            ))
        
        return segments
    
    def _generate_generic_script(self, content: Dict[str, Any], config: NarrationConfig) -> List[ScriptSegment]:
        """Generate generic script for unknown content types."""
        title = content.get('title', 'This section')
        description = content.get('description', 'contains important information')
        
        script_parts = [
            f"{title} {description}.",
            "Let's examine the details and understand the implementation."
        ]
        
        segments = []
        for part in script_parts:
            segments.append(ScriptSegment(
                content=part,
                duration=0.0,
                start_time=0.0,
                end_time=0.0,
                context={'type': 'generic', 'part': script_parts.index(part)}
            ))
        
        return segments
    
    def generate_code_explanation_script(self, code_snippet: str, language: str, config: NarrationConfig) -> str:
        """
        Generate a beginner-friendly explanation of code.
        
        Args:
            code_snippet: The code to explain
            language: Programming language
            config: Narration configuration
            
        Returns:
            Generated explanation script
        """
        # Create a context-aware prompt
        prompt = f"""
        Explain this {language} function in beginner terms: {code_snippet}
        
        Focus on:
        1. What the function does in simple terms
        2. What inputs it expects
        3. What output it produces
        4. One common mistake beginners might make
        
        Keep it conversational and educational.
        """
        
        # For now, return a template-based explanation
        # In a full implementation, this would use an LLM API
        return self._generate_template_explanation(code_snippet, language)
    
    def _generate_template_explanation(self, code_snippet: str, language: str) -> str:
        """Generate a template-based explanation for code."""
        lines = code_snippet.strip().split('\n')
        
        if language.lower() == 'python':
            if 'def ' in code_snippet:
                # Function explanation
                func_match = re.search(r'def\s+(\w+)\s*\(([^)]*)\)', code_snippet)
                if func_match:
                    func_name = func_match.group(1)
                    params = func_match.group(2)
                    return f"This Python function called {func_name} takes {params} as input and performs a specific task. It's like giving instructions to the computer. A common mistake is forgetting to call the function with the right parameters."
            
            elif 'class ' in code_snippet:
                # Class explanation
                class_match = re.search(r'class\s+(\w+)', code_snippet)
                if class_match:
                    class_name = class_match.group(1)
                    return f"This defines a Python class called {class_name}, which is like a blueprint for creating objects. Think of it as a template that describes what properties and behaviors an object should have."
            
            elif 'import ' in code_snippet or 'from ' in code_snippet:
                # Import explanation
                return "This line imports external libraries or modules that provide additional functionality. It's like telling Python to bring in tools from a toolbox. A common mistake is trying to use a module without importing it first."
        
        # Generic explanation
        return f"This {language} code performs a specific operation. It's important to understand what each line does and how they work together. A common mistake is not testing the code with different inputs."
    
    def synthesize_speech(self, text: str, config: NarrationConfig, output_path: Optional[str] = None) -> str:
        """
        Synthesize speech using ElevenLabs API.
        
        Args:
            text: Text to synthesize
            config: Narration configuration
            output_path: Output file path (optional)
            
        Returns:
            Path to the generated audio file
        """
        if not self.api_key:
            logger.error("No ElevenLabs API key available")
            return ""
        
        if not output_path:
            output_path = self._generate_temp_audio_path()
        
        try:
            # Prepare the request
            url = f"{self.base_url}/text-to-speech/{config.voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": config.stability,
                    "similarity_boost": config.similarity_boost,
                    "style": config.style,
                    "use_speaker_boost": config.use_speaker_boost
                }
            }
            
            # Make the API request
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                # Save the audio file
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                logger.info(f"Audio synthesized successfully: {output_path}")
                return output_path
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return ""
    
    def synthesize_script(self, script_segments: List[ScriptSegment], config: NarrationConfig, output_dir: Optional[str] = None) -> List[str]:
        """
        Synthesize speech for all script segments.
        
        Args:
            script_segments: List of script segments
            config: Narration configuration
            output_dir: Output directory for audio files
            
        Returns:
            List of audio file paths
        """
        if not output_dir:
            output_dir = tempfile.mkdtemp()
        
        audio_files = []
        
        for i, segment in enumerate(script_segments):
            if segment.content.strip():
                output_path = os.path.join(output_dir, f"segment_{i:03d}.mp3")
                audio_file = self.synthesize_speech(segment.content, config, output_path)
                
                if audio_file:
                    segment.audio_file = audio_file
                    audio_files.append(audio_file)
                    logger.info(f"Generated audio for segment {i}: {audio_file}")
                else:
                    logger.warning(f"Failed to generate audio for segment {i}")
        
        return audio_files
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices from ElevenLabs.
        
        Returns:
            List of voice information dictionaries
        """
        if not self.api_key:
            logger.warning("No API key available for voice list")
            return []
        
        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                voices = response.json().get("voices", [])
                self.voices_cache = {v["voice_id"]: v for v in voices}
                return voices
            else:
                logger.error(f"Failed to get voices: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    def get_voice_by_style(self, style: VoiceStyle) -> Optional[str]:
        """
        Get voice ID for a specific style.
        
        Args:
            style: Voice style
            
        Returns:
            Voice ID or None if not found
        """
        return self.default_voices.get(style)
    
    def get_voice_by_language(self, language: Language) -> Optional[str]:
        """
        Get voice ID for a specific language.
        
        Args:
            language: Language
            
        Returns:
            Voice ID or None if not found
        """
        return self.language_voices.get(language)
    
    def create_narration_config(self, style: VoiceStyle = VoiceStyle.PROFESSIONAL, 
                               language: Language = Language.ENGLISH,
                               voice_id: Optional[str] = None) -> NarrationConfig:
        """
        Create a narration configuration.
        
        Args:
            style: Voice style
            language: Language
            voice_id: Custom voice ID (optional)
            
        Returns:
            Narration configuration
        """
        if voice_id:
            config_voice_id = voice_id
        elif language != Language.ENGLISH:
            config_voice_id = self.get_voice_by_language(language) or self.default_voices[style]
        else:
            config_voice_id = self.default_voices[style]
        
        return NarrationConfig(
            voice_id=config_voice_id,
            voice_style=style,
            language=language
        )
    
    def _estimate_duration(self, text: str, speed: float = 1.0) -> float:
        """
        Estimate the duration of spoken text.
        
        Args:
            text: Text to estimate duration for
            speed: Speech speed multiplier
            
        Returns:
            Estimated duration in seconds
        """
        # Average speaking rate is about 150 words per minute
        words = len(text.split())
        base_duration = (words / 150) * 60  # Convert to seconds
        
        # Apply speed factor
        duration = base_duration / speed
        
        # Add some buffer for natural pauses
        duration += len(text.split('.')) * 0.5
        
        return max(duration, 1.0)  # Minimum 1 second
    
    def _generate_cache_key(self, content: Dict[str, Any], config: NarrationConfig) -> str:
        """Generate a cache key for content and configuration."""
        content_str = json.dumps(content, sort_keys=True)
        config_str = f"{config.voice_id}_{config.voice_style.value}_{config.language.value}_{config.speed}"
        
        combined = f"{content_str}_{config_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _generate_temp_audio_path(self) -> str:
        """Generate a temporary audio file path."""
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time())
        return os.path.join(temp_dir, f"narration_{timestamp}.mp3")
    
    def cleanup_audio_files(self, audio_files: List[str]):
        """
        Clean up generated audio files.
        
        Args:
            audio_files: List of audio file paths to delete
        """
        for audio_file in audio_files:
            try:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                    logger.info(f"Cleaned up audio file: {audio_file}")
            except Exception as e:
                logger.error(f"Error cleaning up {audio_file}: {e}")


class NarrationManager:
    """Manages narration generation and synchronization."""
    
    def __init__(self, narrator: AINarrator):
        """
        Initialize the narration manager.
        
        Args:
            narrator: AI narrator instance
        """
        self.narrator = narrator
        self.generated_audio = []
    
    def generate_video_narration(self, video_steps: List[Dict[str, Any]], 
                                config: NarrationConfig) -> List[Dict[str, Any]]:
        """
        Generate narration for video steps.
        
        Args:
            video_steps: List of video step dictionaries
            config: Narration configuration
            
        Returns:
            List of steps with narration data
        """
        logger.info(f"Generating narration for {len(video_steps)} video steps")
        
        narrated_steps = []
        
        for step in video_steps:
            try:
                # Generate script for this step
                script_segments = self.narrator.generate_narration_script(step, config)
                
                # Synthesize audio
                audio_files = self.narrator.synthesize_script(script_segments, config)
                
                # Add narration data to step
                step_with_narration = step.copy()
                step_with_narration['narration'] = {
                    'script_segments': [self._segment_to_dict(s) for s in script_segments],
                    'audio_files': audio_files,
                    'total_duration': sum(s.duration for s in script_segments)
                }
                
                narrated_steps.append(step_with_narration)
                self.generated_audio.extend(audio_files)
                
            except Exception as e:
                logger.error(f"Error generating narration for step: {e}")
                narrated_steps.append(step)
        
        return narrated_steps
    
    def _segment_to_dict(self, segment: ScriptSegment) -> Dict[str, Any]:
        """Convert ScriptSegment to dictionary."""
        return {
            'content': segment.content,
            'duration': segment.duration,
            'start_time': segment.start_time,
            'end_time': segment.end_time,
            'context': segment.context,
            'audio_file': segment.audio_file
        }
    
    def cleanup(self):
        """Clean up generated audio files."""
        self.narrator.cleanup_audio_files(self.generated_audio)
        self.generated_audio.clear() 