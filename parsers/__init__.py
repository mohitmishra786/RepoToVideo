"""
Parser Plugin Architecture

This module provides a plugin-based architecture for code parsers,
allowing easy extension to support new programming languages.
"""

import os
import importlib
import logging
from typing import Dict, List, Optional, Any, Type
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Base class for all code parsers."""
    
    def __init__(self):
        """Initialize the parser."""
        self.supported_extensions = []
        self.language_name = ""
    
    @abstractmethod
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a single file.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Dictionary containing parsed information
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List of file extensions (e.g., ['.py', '.js'])
        """
        pass
    
    @abstractmethod
    def get_language_name(self) -> str:
        """
        Get the name of the language this parser supports.
        
        Returns:
            Language name (e.g., 'Python', 'JavaScript')
        """
        pass
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Check if this parser can parse the given file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the parser can handle this file
        """
        return file_path.suffix.lower() in self.supported_extensions


class ParserManager:
    """Manages parser plugins and provides unified parsing interface."""
    
    def __init__(self, parsers_dir: str = "parsers"):
        """
        Initialize the parser manager.
        
        Args:
            parsers_dir: Directory containing parser modules
        """
        self.parsers_dir = Path(parsers_dir)
        self.parsers: Dict[str, BaseParser] = {}
        self.load_parsers()
    
    def load_parsers(self):
        """Load all available parser plugins."""
        if not self.parsers_dir.exists():
            logger.warning(f"Parsers directory {self.parsers_dir} does not exist")
            return
        
        # Load built-in parsers
        self._load_builtin_parsers()
        
        # Load external parser plugins
        self._load_external_parsers()
        
        logger.info(f"Loaded {len(self.parsers)} parsers")
    
    def _load_builtin_parsers(self):
        """Load built-in parser modules."""
        builtin_parsers = [
            "python_parser",
            "javascript_parser", 
            "java_parser"
        ]
        
        for parser_name in builtin_parsers:
            try:
                module = importlib.import_module(f"parsers.{parser_name}")
                
                # Look for parser class in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseParser) and 
                        attr != BaseParser):
                        
                        parser_instance = attr()
                        language_name = parser_instance.get_language_name()
                        self.parsers[language_name.lower()] = parser_instance
                        logger.info(f"Loaded built-in parser: {language_name}")
                        break
                        
            except ImportError as e:
                logger.warning(f"Could not load built-in parser {parser_name}: {e}")
            except Exception as e:
                logger.error(f"Error loading built-in parser {parser_name}: {e}")
    
    def _load_external_parsers(self):
        """Load external parser plugins from the parsers directory."""
        for file_path in self.parsers_dir.glob("*.py"):
            if file_path.name.startswith("__"):
                continue
            
            try:
                # Import the module
                module_name = f"parsers.{file_path.stem}"
                module = importlib.import_module(module_name)
                
                # Look for parser class
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseParser) and 
                        attr != BaseParser):
                        
                        parser_instance = attr()
                        language_name = parser_instance.get_language_name()
                        
                        # Check for conflicts
                        if language_name.lower() in self.parsers:
                            logger.warning(f"Parser for {language_name} already loaded, skipping {file_path.name}")
                        else:
                            self.parsers[language_name.lower()] = parser_instance
                            logger.info(f"Loaded external parser: {language_name} from {file_path.name}")
                        break
                        
            except ImportError as e:
                logger.warning(f"Could not load external parser {file_path.name}: {e}")
            except Exception as e:
                logger.error(f"Error loading external parser {file_path.name}: {e}")
    
    def get_parser_for_file(self, file_path: Path) -> Optional[BaseParser]:
        """
        Get the appropriate parser for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Parser instance or None if no suitable parser found
        """
        for parser in self.parsers.values():
            if parser.can_parse(file_path):
                return parser
        
        return None
    
    def get_parser_for_language(self, language_name: str) -> Optional[BaseParser]:
        """
        Get parser for a specific language.
        
        Args:
            language_name: Name of the language
            
        Returns:
            Parser instance or None if not found
        """
        return self.parsers.get(language_name.lower())
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages.
        
        Returns:
            List of supported language names
        """
        return list(self.parsers.keys())
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a file using the appropriate parser.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Parsed file information
        """
        parser = self.get_parser_for_file(file_path)
        
        if parser is None:
            logger.warning(f"No parser found for file: {file_path}")
            return {
                'language': 'unknown',
                'error': f'No parser available for {file_path.suffix} files'
            }
        
        try:
            result = parser.parse_file(file_path)
            result['parser_used'] = parser.get_language_name()
            return result
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return {
                'language': parser.get_language_name(),
                'error': str(e)
            }
    
    def parse_project(self, project_path: Path) -> Dict[str, Any]:
        """
        Parse all files in a project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dictionary containing parsing results for all files
        """
        if not project_path.exists() or not project_path.is_dir():
            return {'error': f'Project path does not exist: {project_path}'}
        
        results = {
            'project_path': str(project_path),
            'files': {},
            'languages': {},
            'errors': []
        }
        
        # Get all code files
        code_files = []
        for ext in ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs']:
            code_files.extend(project_path.rglob(f"*{ext}"))
        
        # Parse each file
        for file_path in code_files:
            try:
                file_result = self.parse_file(file_path)
                results['files'][str(file_path)] = file_result
                
                # Track language statistics
                language = file_result.get('language', 'unknown')
                if language not in results['languages']:
                    results['languages'][language] = 0
                results['languages'][language] += 1
                
            except Exception as e:
                error_msg = f"Error parsing {file_path}: {e}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
        
        return results
    
    def register_parser(self, parser: BaseParser):
        """
        Register a parser manually.
        
        Args:
            parser: Parser instance to register
        """
        language_name = parser.get_language_name()
        self.parsers[language_name.lower()] = parser
        logger.info(f"Registered parser: {language_name}")
    
    def unregister_parser(self, language_name: str):
        """
        Unregister a parser.
        
        Args:
            language_name: Name of the language to unregister
        """
        if language_name.lower() in self.parsers:
            del self.parsers[language_name.lower()]
            logger.info(f"Unregistered parser: {language_name}")
        else:
            logger.warning(f"Parser for {language_name} not found") 