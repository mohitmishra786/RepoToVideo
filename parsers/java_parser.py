"""
Java Parser

This module provides a parser for Java files using regex patterns.
"""

import re
import logging
from typing import Dict, List, Any
from pathlib import Path
from . import BaseParser

logger = logging.getLogger(__name__)


class JavaParser(BaseParser):
    """Parser for Java files using regex patterns."""
    
    def __init__(self):
        """Initialize the Java parser."""
        super().__init__()
        self.supported_extensions = ['.java']
        self.language_name = "Java"
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a Java file using regex patterns.
        
        Args:
            file_path: Path to the Java file
            
        Returns:
            Dictionary containing parsed information
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'language': 'Java',
                'file_path': str(file_path),
                'size': len(content),
                'lines': len(content.splitlines()),
                'classes': self._extract_classes(content),
                'methods': self._extract_methods(content),
                'imports': self._extract_imports(content),
                'variables': self._extract_variables(content),
                'complexity': self._calculate_complexity(content),
                'comments': self._extract_comments(content),
                'error_patterns': self._detect_error_patterns(content)
            }
            
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return {
                'language': 'Java',
                'file_path': str(file_path),
                'error': str(e)
            }
    
    def get_supported_extensions(self) -> List[str]:
        """Get supported file extensions."""
        return self.supported_extensions
    
    def get_language_name(self) -> str:
        """Get the language name."""
        return self.language_name
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class information using regex patterns."""
        classes = []
        
        # Class declaration pattern
        class_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
        matches = re.finditer(class_pattern, content)
        
        for match in matches:
            class_name = match.group(1)
            parent_class = match.group(2) if match.group(2) else None
            interfaces = [i.strip() for i in match.group(3).split(',')] if match.group(3) else []
            line_num = content[:match.start()].count('\n') + 1
            
            # Find class methods and fields
            class_body = self._extract_class_body(content, match.start())
            methods = self._extract_class_methods(class_body)
            fields = self._extract_class_fields(class_body)
            
            classes.append({
                'name': class_name,
                'line_start': line_num,
                'inheritance': [parent_class] if parent_class else [],
                'interfaces': interfaces,
                'methods': methods,
                'fields': fields,
                'modifiers': self._extract_modifiers(content[:match.start()])
            })
        
        return classes
    
    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract method information using regex patterns."""
        methods = []
        
        # Method declaration pattern
        method_pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:native\s+)?(?:abstract\s+)?(?:strictfp\s+)?(?:<[^>]+>\s+)?(?:[\w\[\]]+)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{'
        matches = re.finditer(method_pattern, content)
        
        for match in matches:
            method_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            # Extract method signature
            method_signature = self._extract_method_signature(content, match.start())
            
            methods.append({
                'name': method_name,
                'line_start': line_num,
                'signature': method_signature,
                'modifiers': self._extract_modifiers(content[:match.start()]),
                'calls': self._extract_method_calls(content, match.start(), match.end())
            })
        
        return methods
    
    def _extract_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract import information using regex patterns."""
        imports = []
        
        # Import patterns
        import_patterns = [
            r'import\s+(?:static\s+)?([^;]+);',
            r'import\s+([^;]+);'
        ]
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                import_statement = match.group(1).strip()
                line_num = content[:match.start()].count('\n') + 1
                
                imports.append({
                    'statement': import_statement,
                    'line': line_num,
                    'type': 'static_import' if 'static' in pattern else 'regular_import'
                })
        
        return imports
    
    def _extract_variables(self, content: str) -> List[Dict[str, Any]]:
        """Extract variable declarations using regex patterns."""
        variables = []
        
        # Variable declaration patterns
        var_patterns = [
            r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:[\w\[\]]+)\s+(\w+)\s*=\s*([^;]+);',
            r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:[\w\[\]]+)\s+(\w+);',
            r'(\w+)\s*=\s*([^;]+);'
        ]
        
        for pattern in var_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                var_name = match.group(1)
                var_value = match.group(2) if len(match.groups()) > 1 else None
                line_num = content[:match.start()].count('\n') + 1
                
                variables.append({
                    'name': var_name,
                    'line': line_num,
                    'value': var_value,
                    'type': self._infer_variable_type(var_value) if var_value else 'unknown'
                })
        
        return variables
    
    def _calculate_complexity(self, content: str) -> Dict[str, int]:
        """Calculate code complexity metrics."""
        complexity = {
            'cyclomatic': 1,  # Base complexity
            'nesting_depth': 0,
            'statements': 0
        }
        
        lines = content.splitlines()
        
        for line in lines:
            line = line.strip()
            
            # Cyclomatic complexity
            if re.search(r'\b(if|else|for|while|switch|catch|case)\b', line):
                complexity['cyclomatic'] += 1
            
            # Statement count
            if re.search(r'[;{}]', line) and not line.startswith('//'):
                complexity['statements'] += 1
        
        # Calculate nesting depth (simplified)
        depth = 0
        max_depth = 0
        for char in content:
            if char == '{':
                depth += 1
                max_depth = max(max_depth, depth)
            elif char == '}':
                depth = max(0, depth - 1)
        
        complexity['nesting_depth'] = max_depth
        
        return complexity
    
    def _extract_comments(self, content: str) -> List[Dict[str, Any]]:
        """Extract comments from the code."""
        comments = []
        
        # Single-line comments
        single_line_pattern = r'//\s*(.+)'
        matches = re.finditer(single_line_pattern, content)
        
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            comments.append({
                'type': 'single_line',
                'line': line_num,
                'content': match.group(1).strip()
            })
        
        # Multi-line comments
        multi_line_pattern = r'/\*([^*]|\*(?!/))*\*/'
        matches = re.finditer(multi_line_pattern, content, re.DOTALL)
        
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            comments.append({
                'type': 'multi_line',
                'line': line_num,
                'content': match.group(0).strip()
            })
        
        # Javadoc comments
        javadoc_pattern = r'/\*\*([^*]|\*(?!/))*\*/'
        matches = re.finditer(javadoc_pattern, content, re.DOTALL)
        
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            comments.append({
                'type': 'javadoc',
                'line': line_num,
                'content': match.group(0).strip()
            })
        
        return comments
    
    def _detect_error_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Detect common error patterns in Java code."""
        patterns = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Null pointer access patterns
            if re.search(r'(\w+)\.\w+\s*\([^)]*\)', line):
                var_name = re.search(r'(\w+)\.\w+\s*\([^)]*\)', line).group(1)
                if not self._is_variable_defined(var_name, content, i):
                    patterns.append({
                        'type': 'null_pointer_access',
                        'severity': 'error',
                        'line': i,
                        'message': f"Variable '{var_name}' might be null",
                        'suggestion': f"Add null check for '{var_name}'"
                    })
            
            # Type mismatches
            if re.search(r'(\w+)\s*\+\s*(\d+)', line):
                var_name = re.search(r'(\w+)\s*\+\s*(\d+)', line).group(1)
                patterns.append({
                    'type': 'type_mismatch',
                    'severity': 'warning',
                    'line': i,
                    'message': f"Potential type mismatch with '{var_name}'",
                    'suggestion': "Convert types explicitly or use proper types"
                })
            
            # Missing semicolons
            if (re.search(r'[^;{}]\s*$', line) and 
                not line.startswith('//') and 
                not line.startswith('/*') and
                not line.startswith('*') and
                not line.startswith('*/') and
                not line.startswith('@') and
                line.strip()):
                patterns.append({
                    'type': 'missing_semicolon',
                    'severity': 'warning',
                    'line': i,
                    'message': "Missing semicolon",
                    'suggestion': "Add semicolon at the end of the statement"
                })
        
        return patterns
    
    def _extract_class_body(self, content: str, class_start: int) -> str:
        """Extract the body of a class."""
        class_body = content[class_start:]
        brace_count = 0
        body_start = 0
        body_end = 0
        
        for i, char in enumerate(class_body):
            if char == '{':
                if brace_count == 0:
                    body_start = i + 1
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    body_end = i
                    break
        
        if body_end > body_start:
            return class_body[body_start:body_end]
        
        return ""
    
    def _extract_class_methods(self, class_body: str) -> List[Dict[str, Any]]:
        """Extract methods from a class body."""
        methods = []
        
        # Method pattern for class methods
        method_pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:native\s+)?(?:abstract\s+)?(?:strictfp\s+)?(?:<[^>]+>\s+)?(?:[\w\[\]]+)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{'
        matches = re.finditer(method_pattern, class_body)
        
        for match in matches:
            method_name = match.group(1)
            methods.append({
                'name': method_name,
                'signature': self._extract_method_signature(class_body, match.start())
            })
        
        return methods
    
    def _extract_class_fields(self, class_body: str) -> List[Dict[str, Any]]:
        """Extract fields from a class body."""
        fields = []
        
        # Field pattern
        field_pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:[\w\[\]]+)\s+(\w+)\s*(?:=\s*([^;]+))?;'
        matches = re.finditer(field_pattern, class_body)
        
        for match in matches:
            field_name = match.group(1)
            field_value = match.group(2) if match.group(2) else None
            
            fields.append({
                'name': field_name,
                'value': field_value,
                'type': self._infer_variable_type(field_value) if field_value else 'unknown'
            })
        
        return fields
    
    def _extract_method_signature(self, content: str, method_start: int) -> str:
        """Extract the complete method signature."""
        # Find the method declaration line
        lines = content[:method_start].splitlines()
        method_line = lines[-1] if lines else ""
        
        # Find the opening brace
        after_method = content[method_start:]
        brace_pos = after_method.find('{')
        
        if brace_pos > 0:
            method_signature = after_method[:brace_pos].strip()
            return method_line + " " + method_signature
        
        return method_line
    
    def _extract_method_calls(self, content: str, method_start: int, method_end: int) -> List[str]:
        """Extract method calls within a method."""
        calls = []
        
        # Find the method body
        method_body = content[method_end:]
        brace_count = 0
        body_end = 0
        
        for i, char in enumerate(method_body):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    body_end = i
                    break
        
        if body_end > 0:
            method_body = method_body[:body_end]
            
            # Extract method calls
            call_pattern = r'(\w+)\s*\('
            matches = re.finditer(call_pattern, method_body)
            
            for match in matches:
                calls.append(match.group(1))
        
        return calls
    
    def _extract_modifiers(self, content_before: str) -> List[str]:
        """Extract modifiers from the content before a declaration."""
        modifiers = []
        
        # Common Java modifiers
        modifier_patterns = [
            r'\bpublic\b',
            r'\bprivate\b',
            r'\bprotected\b',
            r'\bstatic\b',
            r'\bfinal\b',
            r'\bsynchronized\b',
            r'\bnative\b',
            r'\babstract\b',
            r'\bstrictfp\b'
        ]
        
        for pattern in modifier_patterns:
            if re.search(pattern, content_before):
                modifier = re.search(pattern, content_before).group(0)
                modifiers.append(modifier)
        
        return modifiers
    
    def _is_variable_defined(self, var_name: str, content: str, line_num: int) -> bool:
        """Check if a variable is defined before use."""
        lines = content.splitlines()
        before_lines = lines[:line_num - 1]
        
        # Check for variable declarations
        declaration_patterns = [
            rf'[\w\[\]]+\s+{var_name}\s*=',
            rf'[\w\[\]]+\s+{var_name}\s*;',
            rf'for\s*\([\w\[\]]+\s+{var_name}\s*:',
            rf'catch\s*\([\w\[\]]+\s+{var_name}\s*\)'
        ]
        
        for line in before_lines:
            for pattern in declaration_patterns:
                if re.search(pattern, line):
                    return True
        
        return False
    
    def _infer_variable_type(self, value: str) -> str:
        """Infer the type of a variable from its value."""
        if not value:
            return 'unknown'
        
        value = value.strip()
        
        # Check for different types
        if re.match(r'^[\'"].*[\'"]$', value):
            return 'string'
        elif re.match(r'^\d+$', value):
            return 'number'
        elif re.match(r'^\d+\.\d+$', value):
            return 'number'
        elif value in ['true', 'false']:
            return 'boolean'
        elif value == 'null':
            return 'null'
        elif value.startswith('new '):
            return 'object'
        elif value.startswith('[') and value.endswith(']'):
            return 'array'
        elif value.startswith('{') and value.endswith('}'):
            return 'map'
        
        return 'unknown' 