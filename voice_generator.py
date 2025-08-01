"""
Voice Generator Module

This module handles text-to-speech generation for video walkthroughs using gTTS.
"""

import os
import tempfile
from typing import Optional
from gtts import gTTS
from gtts.lang import tts_langs
import time


class VoiceGenerator:
    """Handles text-to-speech generation for video narration."""
    
    def __init__(self, language: str = 'en', slow: bool = False):
        """
        Initialize the VoiceGenerator.
        
        Args:
            language: Language code for TTS (default: 'en' for English)
            slow: Whether to use slow speech (default: False)
        """
        self.language = language
        self.slow = slow
        # Create a permanent audio directory instead of temp
        self.audio_dir = "audio_files"
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
        self.audio_files = []
    
    def generate_voice(self, text: str, filename: str) -> str:
        """
        Generate speech from text and save to file.
        
        Args:
            text: Text to convert to speech
            filename: Name for the output audio file
            
        Returns:
            Path to the generated audio file
        """
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            if not cleaned_text.strip():
                return None
            
            # Generate TTS
            tts = gTTS(text=cleaned_text, lang=self.language, slow=self.slow)
            
            # Save to permanent audio directory
            audio_path = os.path.join(self.audio_dir, f"{filename}.mp3")
            tts.save(audio_path)
            
            self.audio_files.append(audio_path)
            return audio_path
            
        except Exception as e:
            print(f"Error generating voice for '{filename}': {str(e)}")
            return None
    
    def generate_step_voice(self, step: dict, step_number: int) -> Optional[str]:
        """
        Generate voice for a specific step.
        
        Args:
            step: Step dictionary containing voice_script
            step_number: Number of the step
            
        Returns:
            Path to the generated audio file
        """
        voice_script = step.get('voice_script', '')
        if not voice_script:
            return None
        
        filename = f"step_{step_number:02d}_{step['type']}"
        return self.generate_voice(voice_script, filename)
    
    def generate_intro_voice(self, repo_name: str, owner: str) -> Optional[str]:
        """
        Generate introduction voice.
        
        Args:
            repo_name: Name of the repository
            owner: Repository owner
            
        Returns:
            Path to the generated audio file
        """
        text = f"Welcome to RepoToVideo! Today we'll be exploring {repo_name}, " \
               f"a repository by {owner}. This automated walkthrough will guide you " \
               f"through the codebase, explaining key concepts and demonstrating functionality. " \
               f"Let's get started!"
        
        return self.generate_voice(text, "intro")
    
    def generate_outro_voice(self, repo_name: str, total_steps: int) -> Optional[str]:
        """
        Generate outro voice.
        
        Args:
            repo_name: Name of the repository
            total_steps: Total number of steps completed
            
        Returns:
            Path to the generated audio file
        """
        text = f"Thank you for watching this walkthrough of {repo_name}! " \
               f"We've covered {total_steps} key aspects of the codebase. " \
               f"Remember to explore the repository yourself, read the documentation, " \
               f"and try running the code. Happy coding!"
        
        return self.generate_voice(text, "outro")
    
    def generate_error_voice(self, error_type: str) -> Optional[str]:
        """
        Generate voice for error explanations.
        
        Args:
            error_type: Type of error being explained
            
        Returns:
            Path to the generated audio file
        """
        error_explanations = {
            'syntax_error': "This is a syntax error. The code has invalid syntax that prevents it from running. " \
                           "Common causes include missing colons, parentheses, or incorrect indentation.",
            'name_error': "This is a name error. The code is trying to use a variable or function that hasn't been defined. " \
                         "Make sure all variables are declared before use.",
            'indentation_error': "This is an indentation error. Python uses indentation to define code blocks. " \
                               "Make sure your indentation is consistent throughout the file.",
            'general': "Programming errors are common when learning to code. " \
                      "The key is to read error messages carefully and understand what went wrong. " \
                      "Don't be afraid to experiment and learn from mistakes."
        }
        
        text = error_explanations.get(error_type, "An error occurred in the code.")
        return self.generate_voice(text, f"error_{error_type}")
    
    def generate_code_explanation_voice(self, filename: str, language: str, 
                                      functions: int, classes: int) -> Optional[str]:
        """
        Generate voice for code file explanations.
        
        Args:
            filename: Name of the code file
            language: Programming language
            functions: Number of functions
            classes: Number of classes
            
        Returns:
            Path to the generated audio file
        """
        text = f"Let's examine {filename}, a {language} file. " \
               f"This file contains {functions} functions and {classes} classes. " \
               f"We'll go through the code step by step to understand how it works."
        
        return self.generate_voice(text, f"code_explanation_{filename.replace('.', '_')}")
    
    def generate_execution_voice(self, execution_type: str, description: str) -> Optional[str]:
        """
        Generate voice for code execution explanations.
        
        Args:
            execution_type: Type of execution (import, function_def, etc.)
            description: Description of what's happening
            
        Returns:
            Path to the generated audio file
        """
        execution_explanations = {
            'import': f"Here we're importing {description}. This makes the module available for use in our code.",
            'function_def': f"We're defining a function called {description}. This creates a reusable block of code.",
            'class_def': f"We're defining a class called {description}. Classes are used to create objects with shared behavior.",
            'code_block': f"Now we're executing {description}. This code performs the main functionality of the program."
        }
        
        text = execution_explanations.get(execution_type, f"We're executing {description}.")
        return self.generate_voice(text, f"execution_{execution_type}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and prepare text for TTS.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text suitable for TTS
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Replace code snippets with more natural language
        text = text.replace('```', '')
        text = text.replace('`', '')
        
        # Replace common programming terms with more natural language
        replacements = {
            'def ': 'define ',
            'class ': 'class ',
            'import ': 'import ',
            'from ': 'from ',
            'print(': 'print ',
            'return ': 'return ',
            'if ': 'if ',
            'else:': 'else',
            'elif ': 'else if ',
            'for ': 'for ',
            'while ': 'while ',
            'try:': 'try',
            'except ': 'except ',
            'finally:': 'finally',
            'with ': 'with ',
            'as ': 'as ',
            'in ': 'in ',
            'is ': 'is ',
            '==': 'equals',
            '!=': 'not equals',
            '>=': 'greater than or equal to',
            '<=': 'less than or equal to',
            '>': 'greater than',
            '<': 'less than',
            'and ': 'and ',
            'or ': 'or ',
            'not ': 'not ',
            'True': 'true',
            'False': 'false',
            'None': 'none',
            'self.': 'self dot ',
            '()': 'parentheses',
            '[]': 'square brackets',
            '{}': 'curly braces',
            '->': 'arrow',
            '=>': 'arrow',
            '//': 'comment',
            '#': 'comment',
            '/*': 'comment',
            '*/': 'comment'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Add pauses for better speech flow
        text = text.replace('.', '. ')
        text = text.replace(',', ', ')
        text = text.replace(';', '; ')
        text = text.replace(':', ': ')
        
        return text.strip()
    
    def get_available_languages(self) -> dict:
        """
        Get available languages for TTS.
        
        Returns:
            Dictionary of available language codes and names
        """
        return tts_langs()
    
    def cleanup(self):
        """Clean up audio files (optional)."""
        for audio_file in self.audio_files:
            try:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            except Exception as e:
                print(f"Error removing audio file {audio_file}: {str(e)}")
        
        try:
            if os.path.exists(self.audio_dir):
                import shutil
                shutil.rmtree(self.audio_dir)
        except Exception as e:
            print(f"Error removing audio directory {self.audio_dir}: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        # Don't auto-cleanup audio files by default
        pass 