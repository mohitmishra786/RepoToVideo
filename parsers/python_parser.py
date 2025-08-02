"""
Python Parser

This module provides a parser for Python files using AST analysis.
"""

import ast
import logging
from typing import Dict, List, Any
from pathlib import Path
from . import BaseParser

logger = logging.getLogger(__name__)


class PythonParser(BaseParser):
    """Parser for Python files using AST analysis."""
    
    def __init__(self):
        """Initialize the Python parser."""
        super().__init__()
        self.supported_extensions = ['.py']
        self.language_name = "Python"
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a Python file using AST analysis.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary containing parsed information
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            return {
                'language': 'Python',
                'file_path': str(file_path),
                'size': len(content),
                'lines': len(content.splitlines()),
                'functions': self._extract_functions(tree, content),
                'classes': self._extract_classes(tree, content),
                'imports': self._extract_imports(tree),
                'variables': self._extract_variables(tree),
                'complexity': self._calculate_complexity(tree),
                'docstrings': self._extract_docstrings(tree),
                'error_patterns': self._detect_error_patterns(tree, content)
            }
            
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return {
                'language': 'Python',
                'file_path': str(file_path),
                'error': f'Syntax error: {e}',
                'error_line': e.lineno
            }
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return {
                'language': 'Python',
                'file_path': str(file_path),
                'error': str(e)
            }
    
    def get_supported_extensions(self) -> List[str]:
        """Get supported file extensions."""
        return self.supported_extensions
    
    def get_language_name(self) -> str:
        """Get the language name."""
        return self.language_name
    
    def _extract_functions(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Extract function information from AST."""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': node.end_lineno or node.lineno,
                    'parameters': [arg.arg for arg in node.args.args],
                    'defaults': [ast.unparse(default) if default else None for default in node.args.defaults],
                    'returns': ast.unparse(node.returns) if node.returns else None,
                    'docstring': ast.get_docstring(node),
                    'decorators': [ast.unparse(decorator) for decorator in node.decorator_list],
                    'calls': self._extract_function_calls(node),
                    'complexity': self._calculate_function_complexity(node)
                }
                functions.append(func_info)
        
        return functions
    
    def _extract_classes(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Extract class information from AST."""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                attributes = []
                
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        methods.append({
                            'name': child.name,
                            'line_start': child.lineno,
                            'line_end': child.end_lineno or child.lineno,
                            'parameters': [arg.arg for arg in child.args.args],
                            'docstring': ast.get_docstring(child)
                        })
                    elif isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name):
                                attributes.append({
                                    'name': target.id,
                                    'line': child.lineno,
                                    'value': ast.unparse(child.value) if child.value else None
                                })
                
                class_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': node.end_lineno or node.lineno,
                    'bases': [ast.unparse(base) for base in node.bases],
                    'keywords': [ast.unparse(keyword) for keyword in node.keywords],
                    'docstring': ast.get_docstring(node),
                    'methods': methods,
                    'attributes': attributes,
                    'decorators': [ast.unparse(decorator) for decorator in node.decorator_list]
                }
                classes.append(class_info)
        
        return classes
    
    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract import information from AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'as_name': alias.asname,
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        'type': 'from_import',
                        'module': node.module,
                        'name': alias.name,
                        'as_name': alias.asname,
                        'line': node.lineno
                    })
        
        return imports
    
    def _extract_variables(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract variable assignments from AST."""
        variables = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append({
                            'name': target.id,
                            'line': node.lineno,
                            'value': ast.unparse(node.value) if node.value else None,
                            'type': self._infer_variable_type(node.value)
                        })
        
        return variables
    
    def _extract_function_calls(self, node: ast.FunctionDef) -> List[str]:
        """Extract function calls within a function."""
        calls = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(f"{ast.unparse(child.func.value)}.{child.func.attr}")
        
        return calls
    
    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, int]:
        """Calculate code complexity metrics."""
        complexity = {
            'cyclomatic': 1,  # Base complexity
            'nesting_depth': 0,
            'statements': 0
        }
        
        for node in ast.walk(tree):
            # Cyclomatic complexity
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler, ast.With)):
                complexity['cyclomatic'] += 1
            
            # Nesting depth
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                depth = self._calculate_nesting_depth(node)
                complexity['nesting_depth'] = max(complexity['nesting_depth'], depth)
            
            # Statement count
            if isinstance(node, (ast.Expr, ast.Assign, ast.AugAssign, ast.AnnAssign, 
                               ast.Return, ast.Delete, ast.Pass, ast.Break, ast.Continue)):
                complexity['statements'] += 1
        
        return complexity
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate complexity for a specific function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
                complexity += 1
        
        return complexity
    
    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate the maximum nesting depth of a node."""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _extract_docstrings(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract docstrings from the AST."""
        docstrings = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                docstring = ast.get_docstring(node)
                if docstring:
                    docstrings.append({
                        'type': type(node).__name__,
                        'name': getattr(node, 'name', 'module'),
                        'line': node.lineno,
                        'content': docstring,
                        'length': len(docstring)
                    })
        
        return docstrings
    
    def _detect_error_patterns(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect common error patterns in Python code."""
        patterns = []
        lines = content.splitlines()
        
        for node in ast.walk(tree):
            # Undefined variables
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if not self._is_variable_defined(node.id, node, tree):
                    patterns.append({
                        'type': 'undefined_variable',
                        'severity': 'error',
                        'line': node.lineno,
                        'message': f"Variable '{node.id}' might be undefined",
                        'suggestion': f"Define '{node.id}' before using it"
                    })
            
            # Type mismatches
            if isinstance(node, ast.BinOp):
                if isinstance(node.op, ast.Add):
                    if (isinstance(node.left, ast.Str) and isinstance(node.right, ast.Num)) or \
                       (isinstance(node.left, ast.Num) and isinstance(node.right, ast.Str)):
                        patterns.append({
                            'type': 'type_mismatch',
                            'severity': 'warning',
                            'line': node.lineno,
                            'message': "Potential type mismatch in addition",
                            'suggestion': "Convert types explicitly or use proper types"
                        })
            
            # Unused imports (basic detection)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if not self._is_import_used(node, tree):
                    patterns.append({
                        'type': 'unused_import',
                        'severity': 'warning',
                        'line': node.lineno,
                        'message': "Import might be unused",
                        'suggestion': "Remove unused import or use it in the code"
                    })
        
        return patterns
    
    def _is_variable_defined(self, var_name: str, node: ast.AST, tree: ast.AST) -> bool:
        """Check if a variable is defined before use."""
        # Simplified check - in a real implementation, this would be more sophisticated
        for ancestor in self._get_ancestors(node, tree):
            if isinstance(ancestor, ast.FunctionDef):
                # Check function parameters
                if var_name in [arg.arg for arg in ancestor.args.args]:
                    return True
            elif isinstance(ancestor, ast.ClassDef):
                # Check class attributes
                if var_name in [attr.id for attr in ancestor.body if isinstance(attr, ast.Assign) and isinstance(attr.targets[0], ast.Name)]:
                    return True
        
        return False
    
    def _get_ancestors(self, node: ast.AST, tree: ast.AST) -> List[ast.AST]:
        """Get ancestor nodes of a given node."""
        # Simplified implementation
        ancestors = []
        for n in ast.walk(tree):
            if hasattr(n, 'body') and node in ast.walk(n):
                ancestors.append(n)
        return ancestors
    
    def _is_import_used(self, import_node: ast.AST, tree: ast.AST) -> bool:
        """Check if an import is used in the code."""
        # Simplified check - in a real implementation, this would track actual usage
        return True  # Assume imports are used for now
    
    def _infer_variable_type(self, value_node: ast.AST) -> str:
        """Infer the type of a variable from its value."""
        if value_node is None:
            return 'unknown'
        
        if isinstance(value_node, ast.Num):
            return 'number'
        elif isinstance(value_node, ast.Str):
            return 'string'
        elif isinstance(value_node, ast.List):
            return 'list'
        elif isinstance(value_node, ast.Dict):
            return 'dict'
        elif isinstance(value_node, ast.Tuple):
            return 'tuple'
        elif isinstance(value_node, ast.Set):
            return 'set'
        elif isinstance(value_node, ast.NameConstant):
            if value_node.value is True or value_node.value is False:
                return 'boolean'
            elif value_node.value is None:
                return 'none'
        elif isinstance(value_node, ast.Call):
            return 'function_call'
        
        return 'unknown' 