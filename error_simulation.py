"""
Error Simulation Engine

This module provides error simulation capabilities for educational purposes,
allowing users to see common programming errors and their solutions.
"""

import ast
import random
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import tempfile
import subprocess
import os
import sys


logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of errors that can be simulated."""
    UNDEFINED_VARIABLE = "undefined_variable"
    TYPE_MISMATCH = "type_mismatch"
    MISSING_IMPORT = "missing_import"
    SYNTAX_ERROR = "syntax_error"
    INDENTATION_ERROR = "indentation_error"
    NAME_ERROR = "name_error"
    ATTRIBUTE_ERROR = "attribute_error"
    INDEX_ERROR = "index_error"
    KEY_ERROR = "key_error"
    ZERO_DIVISION_ERROR = "zero_division_error"


@dataclass
class ErrorSimulation:
    """Represents an error simulation with bug and solution."""
    error_type: ErrorType
    original_code: str
    buggy_code: str
    fixed_code: str
    error_message: str
    explanation: str
    line_number: int
    severity: str
    category: str


class ErrorSimulator:
    """Simulates various programming errors for educational purposes."""
    
    def __init__(self):
        """Initialize the error simulator."""
        self.error_patterns = self._initialize_error_patterns()
        self.solution_templates = self._initialize_solution_templates()
        
    def _initialize_error_patterns(self) -> Dict[ErrorType, List[Dict[str, Any]]]:
        """Initialize error patterns for different error types."""
        return {
            ErrorType.UNDEFINED_VARIABLE: [
                {
                    'pattern': r'(\w+)\s*=\s*(\w+)',
                    'bug_injection': lambda m: f"{m.group(1)} = {m.group(2)}  # {m.group(2)} is undefined",
                    'description': 'Using a variable before it is defined'
                },
                {
                    'pattern': r'print\((\w+)\)',
                    'bug_injection': lambda m: f"print({m.group(1)})  # {m.group(1)} might be undefined",
                    'description': 'Printing an undefined variable'
                }
            ],
            ErrorType.TYPE_MISMATCH: [
                {
                    'pattern': r'(\w+)\s*\+\s*(\d+)',
                    'bug_injection': lambda m: f'"{m.group(1)}" + {m.group(2)}  # String + int',
                    'description': 'Adding string and integer without conversion'
                },
                {
                    'pattern': r'(\w+)\s*\[\s*(\w+)\s*\]',
                    'bug_injection': lambda m: f'{m.group(1)}["{m.group(2)}"]  # Using string as list index',
                    'description': 'Using string as list index instead of dictionary key'
                }
            ],
            ErrorType.MISSING_IMPORT: [
                {
                    'pattern': r'(\w+)\.(\w+)',
                    'bug_injection': lambda m: f"{m.group(1)}.{m.group(2)}  # Missing import for {m.group(1)}",
                    'description': 'Using a module without importing it'
                }
            ],
            ErrorType.SYNTAX_ERROR: [
                {
                    'pattern': r'if\s+(\w+):',
                    'bug_injection': lambda m: f"if {m.group(1)}  # Missing colon",
                    'description': 'Missing colon in if statement'
                },
                {
                    'pattern': r'def\s+(\w+)\s*\([^)]*\):',
                    'bug_injection': lambda m: f"def {m.group(1)}()  # Missing colon",
                    'description': 'Missing colon in function definition'
                }
            ],
            ErrorType.INDENTATION_ERROR: [
                {
                    'pattern': r'(\s+)(\w+)\s*=',
                    'bug_injection': lambda m: f"{m.group(1)[:-4]}{m.group(2)} =  # Wrong indentation",
                    'description': 'Incorrect indentation level'
                }
            ],
            ErrorType.NAME_ERROR: [
                {
                    'pattern': r'(\w+)\.(\w+)',
                    'bug_injection': lambda m: f"{m.group(1)}.{m.group(2)}  # {m.group(1)} not defined",
                    'description': 'Accessing attribute of undefined object'
                }
            ],
            ErrorType.ATTRIBUTE_ERROR: [
                {
                    'pattern': r'(\w+)\.(\w+)',
                    'bug_injection': lambda m: f"{m.group(1)}.{m.group(2)}  # {m.group(2)} attribute doesn't exist",
                    'description': 'Accessing non-existent attribute'
                }
            ],
            ErrorType.INDEX_ERROR: [
                {
                    'pattern': r'(\w+)\s*\[\s*(\d+)\s*\]',
                    'bug_injection': lambda m: f"{m.group(1)}[{int(m.group(2)) + 10}]  # Index out of range",
                    'description': 'Accessing list index that is out of range'
                }
            ],
            ErrorType.KEY_ERROR: [
                {
                    'pattern': r'(\w+)\s*\[\s*[\'"]([^\'"]+)[\'"]\s*\]',
                    'bug_injection': lambda m: f'{m.group(1)}["nonexistent_key"]  # Key does not exist',
                    'description': 'Accessing dictionary key that does not exist'
                }
            ],
            ErrorType.ZERO_DIVISION_ERROR: [
                {
                    'pattern': r'(\w+)\s*/\s*(\w+)',
                    'bug_injection': lambda m: f"{m.group(1)} / 0  # Division by zero",
                    'description': 'Dividing by zero'
                }
            ]
        }
    
    def _initialize_solution_templates(self) -> Dict[ErrorType, List[str]]:
        """Initialize solution templates for different error types."""
        return {
            ErrorType.UNDEFINED_VARIABLE: [
                "Define the variable before using it: {variable} = value",
                "Check if the variable exists: if '{variable}' in locals():",
                "Use a default value: {variable} = some_value or default_value"
            ],
            ErrorType.TYPE_MISMATCH: [
                "Convert types explicitly: str({variable}) or int({variable})",
                "Use proper data structure: list vs dict",
                "Check types before operation: isinstance({variable}, expected_type)"
            ],
            ErrorType.MISSING_IMPORT: [
                "Add import statement: import {module}",
                "Use from import: from {module} import {item}",
                "Check if module is installed: pip install {module}"
            ],
            ErrorType.SYNTAX_ERROR: [
                "Add missing colon: if condition:",
                "Check parentheses matching",
                "Verify proper syntax structure"
            ],
            ErrorType.INDENTATION_ERROR: [
                "Use consistent indentation (4 spaces recommended)",
                "Check for mixed tabs and spaces",
                "Ensure proper indentation level"
            ],
            ErrorType.NAME_ERROR: [
                "Define the object before accessing its attributes",
                "Check if the object exists in current scope",
                "Import the required module or class"
            ],
            ErrorType.ATTRIBUTE_ERROR: [
                "Check if the attribute exists: hasattr(obj, 'attr')",
                "Use getattr with default: getattr(obj, 'attr', default)",
                "Verify the object type and available attributes"
            ],
            ErrorType.INDEX_ERROR: [
                "Check list length before accessing: if index < len(list)",
                "Use negative indexing: list[-1] for last element",
                "Handle empty lists: if list: list[0]"
            ],
            ErrorType.KEY_ERROR: [
                "Check if key exists: if key in dict",
                "Use dict.get(): dict.get(key, default_value)",
                "Use try-except: try: value = dict[key] except KeyError:"
            ],
            ErrorType.ZERO_DIVISION_ERROR: [
                "Check for zero before division: if divisor != 0",
                "Use try-except: try: result = a / b except ZeroDivisionError:",
                "Provide default value: result = a / b if b != 0 else default"
            ]
        }
    
    def generate_error_simulations(self, code_content: str, num_errors: int = 3) -> List[ErrorSimulation]:
        """
        Generate error simulations for the given code.
        
        Args:
            code_content: The original code content
            num_errors: Number of errors to simulate
            
        Returns:
            List of error simulations
        """
        logger.info(f"Generating {num_errors} error simulations")
        
        simulations = []
        lines = code_content.splitlines()
        
        # Select random error types
        error_types = random.sample(list(ErrorType), min(num_errors, len(ErrorType)))
        
        for error_type in error_types:
            try:
                simulation = self._create_error_simulation(code_content, error_type, lines)
                if simulation:
                    simulations.append(simulation)
            except Exception as e:
                logger.error(f"Error creating simulation for {error_type}: {e}")
        
        return simulations
    
    def _create_error_simulation(self, code_content: str, error_type: ErrorType, lines: List[str]) -> Optional[ErrorSimulation]:
        """Create a specific error simulation."""
        patterns = self.error_patterns.get(error_type, [])
        
        if not patterns:
            return None
        
        # Select a random pattern for this error type
        pattern_info = random.choice(patterns)
        pattern = pattern_info['pattern']
        
        # Find matches in the code
        matches = list(re.finditer(pattern, code_content))
        
        if not matches:
            return None
        
        # Select a random match
        match = random.choice(matches)
        line_number = code_content[:match.start()].count('\n') + 1
        
        # Create buggy code
        buggy_code = self._inject_bug(code_content, match, pattern_info['bug_injection'])
        
        # Create fixed code
        fixed_code = self._create_fix(code_content, match, error_type, pattern_info)
        
        # Generate error message
        error_message = self._generate_error_message(error_type, match)
        
        # Generate explanation
        explanation = self._generate_explanation(error_type, pattern_info['description'])
        
        return ErrorSimulation(
            error_type=error_type,
            original_code=code_content,
            buggy_code=buggy_code,
            fixed_code=fixed_code,
            error_message=error_message,
            explanation=explanation,
            line_number=line_number,
            severity=self._get_error_severity(error_type),
            category=self._get_error_category(error_type)
        )
    
    def _inject_bug(self, code_content: str, match: re.Match, bug_injection_func) -> str:
        """Inject a bug into the code."""
        try:
            buggy_line = bug_injection_func(match)
            
            # Replace the matched line with the buggy version
            lines = code_content.splitlines()
            line_number = code_content[:match.start()].count('\n')
            
            if line_number < len(lines):
                lines[line_number] = buggy_line
                return '\n'.join(lines)
            
            return code_content
        except Exception as e:
            logger.error(f"Error injecting bug: {e}")
            return code_content
    
    def _create_fix(self, code_content: str, match: re.Match, error_type: ErrorType, pattern_info: Dict) -> str:
        """Create a fixed version of the code."""
        solutions = self.solution_templates.get(error_type, [])
        
        if not solutions:
            return code_content
        
        # Select a random solution template
        solution_template = random.choice(solutions)
        
        # Apply the solution based on error type
        if error_type == ErrorType.UNDEFINED_VARIABLE:
            return self._fix_undefined_variable(code_content, match, solution_template)
        elif error_type == ErrorType.TYPE_MISMATCH:
            return self._fix_type_mismatch(code_content, match, solution_template)
        elif error_type == ErrorType.MISSING_IMPORT:
            return self._fix_missing_import(code_content, match, solution_template)
        elif error_type == ErrorType.SYNTAX_ERROR:
            return self._fix_syntax_error(code_content, match, solution_template)
        elif error_type == ErrorType.INDENTATION_ERROR:
            return self._fix_indentation_error(code_content, match, solution_template)
        elif error_type == ErrorType.NAME_ERROR:
            return self._fix_name_error(code_content, match, solution_template)
        elif error_type == ErrorType.ATTRIBUTE_ERROR:
            return self._fix_attribute_error(code_content, match, solution_template)
        elif error_type == ErrorType.INDEX_ERROR:
            return self._fix_index_error(code_content, match, solution_template)
        elif error_type == ErrorType.KEY_ERROR:
            return self._fix_key_error(code_content, match, solution_template)
        elif error_type == ErrorType.ZERO_DIVISION_ERROR:
            return self._fix_zero_division_error(code_content, match, solution_template)
        
        return code_content
    
    def _fix_undefined_variable(self, code_content: str, match: re.Match, template: str) -> str:
        """Fix undefined variable error."""
        variable = match.group(1) if match.groups() else "variable"
        
        # Add variable definition before the problematic line
        lines = code_content.splitlines()
        line_number = code_content[:match.start()].count('\n')
        
        if line_number < len(lines):
            # Insert definition before the line
            definition = f"{variable} = 0  # Define variable before use"
            lines.insert(line_number, definition)
            return '\n'.join(lines)
        
        return code_content
    
    def _fix_type_mismatch(self, code_content: str, match: re.Match, template: str) -> str:
        """Fix type mismatch error."""
        # Add type conversion
        lines = code_content.splitlines()
        line_number = code_content[:match.start()].count('\n')
        
        if line_number < len(lines):
            original_line = lines[line_number]
            # Convert string to int for addition
            fixed_line = original_line.replace('"', '').replace("'", '')
            lines[line_number] = f"{fixed_line}  # Convert types properly"
            return '\n'.join(lines)
        
        return code_content
    
    def _fix_missing_import(self, code_content: str, match: re.Match, template: str) -> str:
        """Fix missing import error."""
        module = match.group(1) if match.groups() else "module"
        
        # Add import at the top
        lines = code_content.splitlines()
        import_line = f"import {module}"
        
        # Find the first non-import line
        insert_position = 0
        for i, line in enumerate(lines):
            if not line.strip().startswith(('import ', 'from ')):
                insert_position = i
                break
        
        lines.insert(insert_position, import_line)
        return '\n'.join(lines)
    
    def _fix_syntax_error(self, code_content: str, match: re.Match, template: str) -> str:
        """Fix syntax error."""
        lines = code_content.splitlines()
        line_number = code_content[:match.start()].count('\n')
        
        if line_number < len(lines):
            original_line = lines[line_number]
            # Add missing colon
            if 'if' in original_line and not original_line.strip().endswith(':'):
                lines[line_number] = f"{original_line}:  # Add missing colon"
            elif 'def' in original_line and not original_line.strip().endswith(':'):
                lines[line_number] = f"{original_line}:  # Add missing colon"
            return '\n'.join(lines)
        
        return code_content
    
    def _fix_indentation_error(self, code_content: str, match: re.Match, template: str) -> str:
        """Fix indentation error."""
        lines = code_content.splitlines()
        line_number = code_content[:match.start()].count('\n')
        
        if line_number < len(lines):
            original_line = lines[line_number]
            # Fix indentation to 4 spaces
            stripped_line = original_line.lstrip()
            lines[line_number] = f"    {stripped_line}  # Fixed indentation"
            return '\n'.join(lines)
        
        return code_content
    
    def _fix_name_error(self, code_content: str, match: re.Match, template: str) -> str:
        """Fix name error."""
        return self._fix_undefined_variable(code_content, match, template)
    
    def _fix_attribute_error(self, code_content: str, match: re.Match, template: str) -> str:
        """Fix attribute error."""
        lines = code_content.splitlines()
        line_number = code_content[:match.start()].count('\n')
        
        if line_number < len(lines):
            original_line = lines[line_number]
            # Add attribute check
            lines[line_number] = f"if hasattr({match.group(1)}, '{match.group(2)}'): {original_line}"
            return '\n'.join(lines)
        
        return code_content
    
    def _fix_index_error(self, code_content: str, match: re.Match, template: str) -> str:
        """Fix index error."""
        lines = code_content.splitlines()
        line_number = code_content[:match.start()].count('\n')
        
        if line_number < len(lines):
            original_line = lines[line_number]
            # Add bounds check
            lines[line_number] = f"if len({match.group(1)}) > {match.group(2)}: {original_line}"
            return '\n'.join(lines)
        
        return code_content
    
    def _fix_key_error(self, code_content: str, match: re.Match, template: str) -> str:
        """Fix key error."""
        lines = code_content.splitlines()
        line_number = code_content[:match.start()].count('\n')
        
        if line_number < len(lines):
            original_line = lines[line_number]
            # Use get() method
            key = match.group(2) if len(match.groups()) > 1 else "key"
            lines[line_number] = f"{match.group(1)}.get('{key}', 'default_value')  # Use get() with default"
            return '\n'.join(lines)
        
        return code_content
    
    def _fix_zero_division_error(self, code_content: str, match: re.Match, template: str) -> str:
        """Fix zero division error."""
        lines = code_content.splitlines()
        line_number = code_content[:match.start()].count('\n')
        
        if line_number < len(lines):
            original_line = lines[line_number]
            # Add zero check
            lines[line_number] = f"if {match.group(2)} != 0: {original_line}"
            return '\n'.join(lines)
        
        return code_content
    
    def _generate_error_message(self, error_type: ErrorType, match: re.Match) -> str:
        """Generate an error message for the given error type."""
        error_messages = {
            ErrorType.UNDEFINED_VARIABLE: f"NameError: name '{match.group(1) if match.groups() else 'variable'}' is not defined",
            ErrorType.TYPE_MISMATCH: "TypeError: unsupported operand type(s) for +: 'str' and 'int'",
            ErrorType.MISSING_IMPORT: f"ModuleNotFoundError: No module named '{match.group(1) if match.groups() else 'module'}'",
            ErrorType.SYNTAX_ERROR: "SyntaxError: invalid syntax",
            ErrorType.INDENTATION_ERROR: "IndentationError: expected an indented block",
            ErrorType.NAME_ERROR: f"NameError: name '{match.group(1) if match.groups() else 'name'}' is not defined",
            ErrorType.ATTRIBUTE_ERROR: f"AttributeError: '{match.group(1) if match.groups() else 'object'}' object has no attribute '{match.group(2) if len(match.groups()) > 1 else 'attribute'}'",
            ErrorType.INDEX_ERROR: "IndexError: list index out of range",
            ErrorType.KEY_ERROR: "KeyError: 'key'",
            ErrorType.ZERO_DIVISION_ERROR: "ZeroDivisionError: division by zero"
        }
        
        return error_messages.get(error_type, "Unknown error occurred")
    
    def _generate_explanation(self, error_type: ErrorType, description: str) -> str:
        """Generate an explanation for the error."""
        explanations = {
            ErrorType.UNDEFINED_VARIABLE: f"This error occurs when you try to use a variable that hasn't been defined yet. {description}",
            ErrorType.TYPE_MISMATCH: f"This error occurs when you try to perform operations on incompatible data types. {description}",
            ErrorType.MISSING_IMPORT: f"This error occurs when you try to use a module or function that hasn't been imported. {description}",
            ErrorType.SYNTAX_ERROR: f"This error occurs when the Python interpreter cannot understand your code due to incorrect syntax. {description}",
            ErrorType.INDENTATION_ERROR: f"This error occurs when the indentation of your code is incorrect. {description}",
            ErrorType.NAME_ERROR: f"This error occurs when you try to use a name that doesn't exist in the current scope. {description}",
            ErrorType.ATTRIBUTE_ERROR: f"This error occurs when you try to access an attribute that doesn't exist on an object. {description}",
            ErrorType.INDEX_ERROR: f"This error occurs when you try to access a list index that is out of range. {description}",
            ErrorType.KEY_ERROR: f"This error occurs when you try to access a dictionary key that doesn't exist. {description}",
            ErrorType.ZERO_DIVISION_ERROR: f"This error occurs when you try to divide by zero. {description}"
        }
        
        return explanations.get(error_type, f"An error occurred: {description}")
    
    def _get_error_severity(self, error_type: ErrorType) -> str:
        """Get the severity level of an error type."""
        severity_map = {
            ErrorType.UNDEFINED_VARIABLE: "error",
            ErrorType.TYPE_MISMATCH: "error",
            ErrorType.MISSING_IMPORT: "error",
            ErrorType.SYNTAX_ERROR: "error",
            ErrorType.INDENTATION_ERROR: "error",
            ErrorType.NAME_ERROR: "error",
            ErrorType.ATTRIBUTE_ERROR: "error",
            ErrorType.INDEX_ERROR: "error",
            ErrorType.KEY_ERROR: "error",
            ErrorType.ZERO_DIVISION_ERROR: "error"
        }
        
        return severity_map.get(error_type, "error")
    
    def _get_error_category(self, error_type: ErrorType) -> str:
        """Get the category of an error type."""
        category_map = {
            ErrorType.UNDEFINED_VARIABLE: "runtime",
            ErrorType.TYPE_MISMATCH: "runtime",
            ErrorType.MISSING_IMPORT: "import",
            ErrorType.SYNTAX_ERROR: "syntax",
            ErrorType.INDENTATION_ERROR: "syntax",
            ErrorType.NAME_ERROR: "runtime",
            ErrorType.ATTRIBUTE_ERROR: "runtime",
            ErrorType.INDEX_ERROR: "runtime",
            ErrorType.KEY_ERROR: "runtime",
            ErrorType.ZERO_DIVISION_ERROR: "runtime"
        }
        
        return category_map.get(error_type, "runtime")
    
    def execute_with_error(self, simulation: ErrorSimulation) -> Dict[str, Any]:
        """
        Execute the buggy code and capture the error.
        
        Args:
            simulation: The error simulation to execute
            
        Returns:
            Dictionary containing execution results
        """
        try:
            # Create temporary file with buggy code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(simulation.buggy_code)
                temp_file = f.name
            
            # Execute the buggy code
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return {
                'success': False,
                'error_message': result.stderr.strip(),
                'stdout': result.stdout.strip(),
                'return_code': result.returncode,
                'execution_time': 0  # Would need to measure this
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error_message': 'Execution timeout',
                'stdout': '',
                'return_code': -1,
                'execution_time': 10
            }
        except Exception as e:
            return {
                'success': False,
                'error_message': str(e),
                'stdout': '',
                'return_code': -1,
                'execution_time': 0
            }
    
    def execute_fixed_code(self, simulation: ErrorSimulation) -> Dict[str, Any]:
        """
        Execute the fixed code to verify the solution.
        
        Args:
            simulation: The error simulation with fixed code
            
        Returns:
            Dictionary containing execution results
        """
        try:
            # Create temporary file with fixed code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(simulation.fixed_code)
                temp_file = f.name
            
            # Execute the fixed code
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return {
                'success': result.returncode == 0,
                'error_message': result.stderr.strip() if result.stderr else '',
                'stdout': result.stdout.strip(),
                'return_code': result.returncode,
                'execution_time': 0  # Would need to measure this
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error_message': 'Execution timeout',
                'stdout': '',
                'return_code': -1,
                'execution_time': 10
            }
        except Exception as e:
            return {
                'success': False,
                'error_message': str(e),
                'stdout': '',
                'return_code': -1,
                'execution_time': 0
            } 