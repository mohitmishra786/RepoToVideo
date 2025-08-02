"""
JavaScript Parser

This module provides a parser for JavaScript files using regex patterns.
"""

import re
import logging
from typing import Dict, List, Any
from pathlib import Path
from . import BaseParser

logger = logging.getLogger(__name__)


class JavaScriptParser(BaseParser):
    """Parser for JavaScript files using regex patterns."""
    
    def __init__(self):
        """Initialize the JavaScript parser."""
        super().__init__()
        self.supported_extensions = ['.js', '.jsx', '.ts', '.tsx']
        self.language_name = "JavaScript"
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a JavaScript file using regex patterns.
        
        Args:
            file_path: Path to the JavaScript file
            
        Returns:
            Dictionary containing parsed information
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'language': 'JavaScript',
                'file_path': str(file_path),
                'size': len(content),
                'lines': len(content.splitlines()),
                'functions': self._extract_functions(content),
                'classes': self._extract_classes(content),
                'imports': self._extract_imports(content),
                'variables': self._extract_variables(content),
                'complexity': self._calculate_complexity(content),
                'comments': self._extract_comments(content),
                'error_patterns': self._detect_error_patterns(content)
            }
            
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return {
                'language': 'JavaScript',
                'file_path': str(file_path),
                'error': str(e)
            }
    
    def get_supported_extensions(self) -> List[str]:
        """Get supported file extensions."""
        return self.supported_extensions
    
    def get_language_name(self) -> str:
        """Get the language name."""
        return self.language_name
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function information using regex patterns."""
        functions = []
        
        # Function declarations
        func_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*\{'
        matches = re.finditer(func_pattern, content)
        
        for match in matches:
            func_name = match.group(1)
            params = [p.strip() for p in match.group(2).split(',') if p.strip()]
            line_num = content[:match.start()].count('\n') + 1
            
            functions.append({
                'name': func_name,
                'type': 'function_declaration',
                'line_start': line_num,
                'parameters': params,
                'calls': self._extract_function_calls(content, match.start(), match.end())
            })
        
        # Arrow functions
        arrow_pattern = r'(\w+)\s*=\s*\(([^)]*)\)\s*=>'
        matches = re.finditer(arrow_pattern, content)
        
        for match in matches:
            func_name = match.group(1)
            params = [p.strip() for p in match.group(2).split(',') if p.strip()]
            line_num = content[:match.start()].count('\n') + 1
            
            functions.append({
                'name': func_name,
                'type': 'arrow_function',
                'line_start': line_num,
                'parameters': params,
                'calls': self._extract_function_calls(content, match.start(), match.end())
            })
        
        # Method definitions in classes
        method_pattern = r'(\w+)\s*\(([^)]*)\)\s*\{'
        matches = re.finditer(method_pattern, content)
        
        for match in matches:
            method_name = match.group(1)
            params = [p.strip() for p in match.group(2).split(',') if p.strip()]
            line_num = content[:match.start()].count('\n') + 1
            
            # Check if this is inside a class
            if self._is_inside_class(content, match.start()):
                functions.append({
                    'name': method_name,
                    'type': 'method',
                    'line_start': line_num,
                    'parameters': params,
                    'calls': self._extract_function_calls(content, match.start(), match.end())
                })
        
        return functions
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class information using regex patterns."""
        classes = []
        
        # ES6 class declarations
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
        matches = re.finditer(class_pattern, content)
        
        for match in matches:
            class_name = match.group(1)
            parent_class = match.group(2) if match.group(2) else None
            line_num = content[:match.start()].count('\n') + 1
            
            # Find class methods
            methods = self._extract_class_methods(content, match.start())
            
            classes.append({
                'name': class_name,
                'line_start': line_num,
                'inheritance': [parent_class] if parent_class else [],
                'methods': methods
            })
        
        return classes
    
    def _extract_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract import information using regex patterns."""
        imports = []
        
        # ES6 import patterns
        import_patterns = [
            r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s*\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+([^;]+);'
        ]
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                if pattern == r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]':
                    imports.append({
                        'type': 'default_import',
                        'name': match.group(1),
                        'module': match.group(2),
                        'line': line_num
                    })
                elif pattern == r'import\s*\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]':
                    names = [name.strip() for name in match.group(1).split(',')]
                    imports.append({
                        'type': 'named_import',
                        'names': names,
                        'module': match.group(2),
                        'line': line_num
                    })
                elif pattern == r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]':
                    imports.append({
                        'type': 'namespace_import',
                        'name': match.group(1),
                        'module': match.group(2),
                        'line': line_num
                    })
                else:
                    imports.append({
                        'type': 'legacy_import',
                        'content': match.group(1),
                        'line': line_num
                    })
        
        return imports
    
    def _extract_variables(self, content: str) -> List[Dict[str, Any]]:
        """Extract variable declarations using regex patterns."""
        variables = []
        
        # Variable declaration patterns
        var_patterns = [
            r'(?:let|const|var)\s+(\w+)\s*=\s*([^;]+);',
            r'(?:let|const|var)\s+(\w+);',
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
            if re.search(r'\b(if|else|for|while|switch|catch)\b', line):
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
        
        return comments
    
    def _detect_error_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Detect common error patterns in JavaScript code."""
        patterns = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Undefined variable patterns
            if re.search(r'console\.log\((\w+)\)', line):
                var_name = re.search(r'console\.log\((\w+)\)', line).group(1)
                if not self._is_variable_defined(var_name, content, i):
                    patterns.append({
                        'type': 'undefined_variable',
                        'severity': 'error',
                        'line': i,
                        'message': f"Variable '{var_name}' might be undefined",
                        'suggestion': f"Define '{var_name}' before using it"
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
            
            # Missing semicolons (basic detection)
            if (re.search(r'[^;{}]\s*$', line) and 
                not line.startswith('//') and 
                not line.startswith('/*') and
                not line.startswith('*') and
                not line.startswith('*/') and
                line.strip()):
                patterns.append({
                    'type': 'missing_semicolon',
                    'severity': 'warning',
                    'line': i,
                    'message': "Missing semicolon",
                    'suggestion': "Add semicolon at the end of the statement"
                })
        
        return patterns
    
    def _extract_function_calls(self, content: str, start_pos: int, end_pos: int) -> List[str]:
        """Extract function calls within a specific range."""
        calls = []
        
        # Look for function calls in the function body
        function_body = content[end_pos:]
        
        # Find the end of the function
        brace_count = 0
        body_end = 0
        
        for i, char in enumerate(function_body):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    body_end = i
                    break
        
        if body_end > 0:
            function_body = function_body[:body_end]
            
            # Extract function calls
            call_pattern = r'(\w+)\s*\('
            matches = re.finditer(call_pattern, function_body)
            
            for match in matches:
                calls.append(match.group(1))
        
        return calls
    
    def _extract_class_methods(self, content: str, class_start: int) -> List[Dict[str, Any]]:
        """Extract methods from a class."""
        methods = []
        
        # Find the class body
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
            class_body = class_body[body_start:body_end]
            
            # Extract method definitions
            method_pattern = r'(\w+)\s*\(([^)]*)\)\s*\{'
            matches = re.finditer(method_pattern, class_body)
            
            for match in matches:
                method_name = match.group(1)
                params = [p.strip() for p in match.group(2).split(',') if p.strip()]
                
                methods.append({
                    'name': method_name,
                    'parameters': params
                })
        
        return methods
    
    def _is_inside_class(self, content: str, position: int) -> bool:
        """Check if a position is inside a class definition."""
        before_content = content[:position]
        
        # Count braces to determine if we're inside a class
        brace_count = 0
        in_class = False
        
        for char in before_content:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            
            # Check for class keyword
            if 'class' in before_content and brace_count > 0:
                in_class = True
        
        return in_class
    
    def _is_variable_defined(self, var_name: str, content: str, line_num: int) -> bool:
        """Check if a variable is defined before use."""
        lines = content.splitlines()
        before_lines = lines[:line_num - 1]
        
        # Check for variable declarations
        declaration_patterns = [
            rf'let\s+{var_name}\b',
            rf'const\s+{var_name}\b',
            rf'var\s+{var_name}\b',
            rf'function\s+{var_name}\b',
            rf'{var_name}\s*='
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
        elif value == 'undefined':
            return 'undefined'
        elif value.startswith('[') and value.endswith(']'):
            return 'array'
        elif value.startswith('{') and value.endswith('}'):
            return 'object'
        elif re.match(r'^function\s*\(', value):
            return 'function'
        elif re.match(r'^\([^)]*\)\s*=>', value):
            return 'arrow_function'
        
        return 'unknown' 