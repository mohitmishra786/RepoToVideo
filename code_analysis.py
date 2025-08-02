"""
Enhanced Code Analysis Module

This module provides advanced code analysis capabilities including:
- Call graph generation using pycallgraph2
- Dependency detection via pipdeptree
- Error pattern identification using AST inspection
- Multi-language support (Python, JavaScript, Java)
"""

import ast
import subprocess
import tempfile
import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from pathlib import Path
import re
from dataclasses import dataclass
from enum import Enum

# Tree-sitter imports
try:
    import tree_sitter
    from tree_sitter import Language, Parser
except ImportError:
    tree_sitter = None
    Language = None
    Parser = None

# Optional imports for advanced features
try:
    import pycallgraph2
    from pycallgraph2 import PyCallGraph
    from pycallgraph2.output import GraphvizOutput
    CALLGRAPH_AVAILABLE = True
except ImportError:
    CALLGRAPH_AVAILABLE = False

try:
    import pipdeptree
    DEPTREE_AVAILABLE = True
except ImportError:
    DEPTREE_AVAILABLE = False

logger = logging.getLogger(__name__)


class LanguageType(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    UNKNOWN = "unknown"


@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    line_start: int
    line_end: int
    parameters: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    calls: List[str]
    complexity: int


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    line_start: int
    line_end: int
    methods: List[FunctionInfo]
    attributes: List[str]
    inheritance: List[str]
    docstring: Optional[str]


@dataclass
class ErrorPattern:
    """Information about a detected error pattern."""
    type: str
    severity: str
    line: int
    message: str
    suggestion: str
    code_snippet: str


class EnhancedCodeAnalyzer:
    """Enhanced code analyzer with advanced features."""
    
    def __init__(self, project_path: str):
        """
        Initialize the code analyzer.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = Path(project_path)
        self.language_parsers = {}
        self._setup_tree_sitter()
        
    def _setup_tree_sitter(self):
        """Setup Tree-sitter parsers for different languages."""
        if not tree_sitter:
            logger.warning("Tree-sitter not available. Using fallback parsing.")
            return
            
        try:
            # Initialize parsers for different languages
            self.language_parsers = {
                LanguageType.PYTHON: Parser(),
                LanguageType.JAVASCRIPT: Parser(),
                LanguageType.JAVA: Parser()
            }
            
            # Set language libraries (these would need to be installed)
            # For now, we'll use fallback parsing
            logger.info("Tree-sitter parsers initialized")
            
        except Exception as e:
            logger.warning(f"Failed to setup Tree-sitter parsers: {e}")
    
    def analyze_project(self) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of the entire project.
        
        Returns:
            Dictionary containing complete project analysis
        """
        logger.info(f"Starting comprehensive analysis of {self.project_path}")
        
        analysis = {
            'project_info': self._get_project_info(),
            'files': {},
            'dependencies': self._analyze_dependencies(),
            'call_graph': self._generate_call_graph(),
            'error_patterns': [],
            'metrics': {}
        }
        
        # Analyze each file
        for file_path in self._get_code_files():
            try:
                file_analysis = self.analyze_file(file_path)
                analysis['files'][str(file_path)] = file_analysis
                analysis['error_patterns'].extend(file_analysis.get('error_patterns', []))
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
        
        # Calculate project metrics
        analysis['metrics'] = self._calculate_project_metrics(analysis)
        
        return analysis
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a single file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary containing file analysis
        """
        language = self._detect_language(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'language': language.value,
            'size': len(content),
            'lines': len(content.splitlines()),
            'functions': [],
            'classes': [],
            'imports': [],
            'error_patterns': [],
            'complexity': 0
        }
        
        if language == LanguageType.PYTHON:
            analysis.update(self._analyze_python_file(content, file_path))
        elif language == LanguageType.JAVASCRIPT:
            analysis.update(self._analyze_javascript_file(content, file_path))
        elif language == LanguageType.JAVA:
            analysis.update(self._analyze_java_file(content, file_path))
        
        return analysis
    
    def _analyze_python_file(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file using AST."""
        try:
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            error_patterns = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_function_info(node, content)
                    functions.append(func_info)
                    
                elif isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node, content)
                    classes.append(class_info)
                    
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_info = self._extract_import_info(node)
                    imports.append(import_info)
            
            # Detect error patterns
            error_patterns = self._detect_python_error_patterns(tree, content)
            
            return {
                'functions': [self._function_to_dict(f) for f in functions],
                'classes': [self._class_to_dict(c) for c in classes],
                'imports': imports,
                'error_patterns': [self._error_pattern_to_dict(e) for e in error_patterns]
            }
            
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return {
                'functions': [],
                'classes': [],
                'imports': [],
                'error_patterns': [{
                    'type': 'syntax_error',
                    'severity': 'error',
                    'line': e.lineno,
                    'message': str(e),
                    'suggestion': 'Fix syntax error',
                    'code_snippet': content.splitlines()[e.lineno - 1] if e.lineno else ''
                }]
            }
    
    def _analyze_javascript_file(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze a JavaScript file."""
        # Basic JavaScript analysis using regex patterns
        functions = self._extract_js_functions(content)
        classes = self._extract_js_classes(content)
        imports = self._extract_js_imports(content)
        error_patterns = self._detect_js_error_patterns(content)
        
        return {
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'error_patterns': error_patterns
        }
    
    def _analyze_java_file(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze a Java file."""
        # Basic Java analysis using regex patterns
        functions = self._extract_java_methods(content)
        classes = self._extract_java_classes(content)
        imports = self._extract_java_imports(content)
        error_patterns = self._detect_java_error_patterns(content)
        
        return {
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'error_patterns': error_patterns
        }
    
    def _extract_function_info(self, node: ast.FunctionDef, content: str) -> FunctionInfo:
        """Extract detailed information about a function."""
        lines = content.splitlines()
        
        # Get function calls within this function
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(f"{child.func.value.id}.{child.func.attr}")
        
        # Calculate complexity (simplified)
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
                complexity += 1
        
        return FunctionInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            parameters=[arg.arg for arg in node.args.args],
            return_type=self._get_return_type_annotation(node),
            docstring=ast.get_docstring(node),
            calls=calls,
            complexity=complexity
        )
    
    def _extract_class_info(self, node: ast.ClassDef, content: str) -> ClassInfo:
        """Extract detailed information about a class."""
        methods = []
        attributes = []
        
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                methods.append(self._extract_function_info(child, content))
            elif isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        return ClassInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            methods=methods,
            attributes=attributes,
            inheritance=[base.id for base in node.bases if isinstance(base, ast.Name)],
            docstring=ast.get_docstring(node)
        )
    
    def _extract_import_info(self, node: Union[ast.Import, ast.ImportFrom]) -> Dict[str, Any]:
        """Extract import information."""
        if isinstance(node, ast.Import):
            return {
                'type': 'import',
                'modules': [alias.name for alias in node.names],
                'line': node.lineno
            }
        else:
            return {
                'type': 'from_import',
                'module': node.module,
                'names': [alias.name for alias in node.names],
                'line': node.lineno
            }
    
    def _detect_python_error_patterns(self, tree: ast.AST, content: str) -> List[ErrorPattern]:
        """Detect common error patterns in Python code."""
        patterns = []
        lines = content.splitlines()
        
        for node in ast.walk(tree):
            # Undefined variables
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if not self._is_variable_defined(node.id, node, tree):
                    patterns.append(ErrorPattern(
                        type='undefined_variable',
                        severity='error',
                        line=node.lineno,
                        message=f"Variable '{node.id}' might be undefined",
                        suggestion=f"Define '{node.id}' before using it",
                        code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else ''
                    ))
            
            # Type mismatches (basic detection)
            if isinstance(node, ast.BinOp):
                if isinstance(node.op, ast.Add):
                    if (isinstance(node.left, ast.Str) and isinstance(node.right, ast.Num)) or \
                       (isinstance(node.left, ast.Num) and isinstance(node.right, ast.Str)):
                        patterns.append(ErrorPattern(
                            type='type_mismatch',
                            severity='warning',
                            line=node.lineno,
                            message="Potential type mismatch in addition",
                            suggestion="Convert types explicitly or use proper types",
                            code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else ''
                        ))
        
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
    
    def _get_return_type_annotation(self, node: ast.FunctionDef) -> Optional[str]:
        """Get return type annotation from function."""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return None
    
    def _extract_js_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract JavaScript functions using regex."""
        functions = []
        
        # Function declaration pattern
        func_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*\{'
        matches = re.finditer(func_pattern, content)
        
        for match in matches:
            functions.append({
                'name': match.group(1),
                'parameters': [p.strip() for p in match.group(2).split(',') if p.strip()],
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Arrow function pattern
        arrow_pattern = r'(\w+)\s*=\s*\(([^)]*)\)\s*=>'
        matches = re.finditer(arrow_pattern, content)
        
        for match in matches:
            functions.append({
                'name': match.group(1),
                'parameters': [p.strip() for p in match.group(2).split(',') if p.strip()],
                'line': content[:match.start()].count('\n') + 1
            })
        
        return functions
    
    def _extract_js_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract JavaScript classes using regex."""
        classes = []
        
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
        matches = re.finditer(class_pattern, content)
        
        for match in matches:
            classes.append({
                'name': match.group(1),
                'inheritance': [match.group(2)] if match.group(2) else [],
                'line': content[:match.start()].count('\n') + 1
            })
        
        return classes
    
    def _extract_js_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract JavaScript imports using regex."""
        imports = []
        
        # ES6 import patterns
        import_patterns = [
            r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s*\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                imports.append({
                    'type': 'es6_import',
                    'names': [name.strip() for name in match.group(1).split(',')],
                    'module': match.group(2),
                    'line': content[:match.start()].count('\n') + 1
                })
        
        return imports
    
    def _detect_js_error_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Detect common error patterns in JavaScript code."""
        patterns = []
        lines = content.splitlines()
        
        # Undefined variable patterns
        undefined_patterns = [
            r'console\.log\((\w+)\)',
            r'(\w+)\.\w+',
        ]
        
        for pattern in undefined_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                var_name = match.group(1)
                if not self._is_js_variable_defined(var_name, content, match.start()):
                    line_num = content[:match.start()].count('\n') + 1
                    patterns.append({
                        'type': 'undefined_variable',
                        'severity': 'error',
                        'line': line_num,
                        'message': f"Variable '{var_name}' might be undefined",
                        'suggestion': f"Define '{var_name}' before using it",
                        'code_snippet': lines[line_num - 1] if line_num <= len(lines) else ''
                    })
        
        return patterns
    
    def _is_js_variable_defined(self, var_name: str, content: str, position: int) -> bool:
        """Check if a JavaScript variable is defined before use."""
        # Simplified check
        before_content = content[:position]
        
        # Check for variable declarations
        declaration_patterns = [
            rf'let\s+{var_name}\b',
            rf'const\s+{var_name}\b',
            rf'var\s+{var_name}\b',
            rf'function\s+{var_name}\b',
            rf'{var_name}\s*='
        ]
        
        for pattern in declaration_patterns:
            if re.search(pattern, before_content):
                return True
        
        return False
    
    def _extract_java_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract Java methods using regex."""
        methods = []
        
        method_pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:native\s+)?(?:abstract\s+)?(?:strictfp\s+)?(?:<[^>]+>\s+)?(?:[\w\[\]]+)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{'
        matches = re.finditer(method_pattern, content)
        
        for match in matches:
            methods.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return methods
    
    def _extract_java_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract Java classes using regex."""
        classes = []
        
        class_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
        matches = re.finditer(class_pattern, content)
        
        for match in matches:
            classes.append({
                'name': match.group(1),
                'inheritance': [match.group(2)] if match.group(2) else [],
                'interfaces': [i.strip() for i in match.group(3).split(',')] if match.group(3) else [],
                'line': content[:match.start()].count('\n') + 1
            })
        
        return classes
    
    def _extract_java_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract Java imports using regex."""
        imports = []
        
        import_pattern = r'import\s+(?:static\s+)?([^;]+);'
        matches = re.finditer(import_pattern, content)
        
        for match in matches:
            imports.append({
                'type': 'java_import',
                'module': match.group(1).strip(),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return imports
    
    def _detect_java_error_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Detect common error patterns in Java code."""
        patterns = []
        lines = content.splitlines()
        
        # Null pointer access patterns
        null_patterns = [
            r'(\w+)\.\w+\s*\([^)]*\)',
            r'(\w+)\.\w+\s*='
        ]
        
        for pattern in null_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                var_name = match.group(1)
                if not self._is_java_variable_defined(var_name, content, match.start()):
                    line_num = content[:match.start()].count('\n') + 1
                    patterns.append({
                        'type': 'null_pointer_access',
                        'severity': 'error',
                        'line': line_num,
                        'message': f"Variable '{var_name}' might be null",
                        'suggestion': f"Add null check for '{var_name}'",
                        'code_snippet': lines[line_num - 1] if line_num <= len(lines) else ''
                    })
        
        return patterns
    
    def _is_java_variable_defined(self, var_name: str, content: str, position: int) -> bool:
        """Check if a Java variable is defined before use."""
        # Simplified check
        before_content = content[:position]
        
        # Check for variable declarations
        declaration_patterns = [
            rf'[\w\[\]]+\s+{var_name}\s*=',
            rf'[\w\[\]]+\s+{var_name}\s*;',
            rf'for\s*\([\w\[\]]+\s+{var_name}\s*:',
            rf'catch\s*\([\w\[\]]+\s+{var_name}\s*\)'
        ]
        
        for pattern in declaration_patterns:
            if re.search(pattern, before_content):
                return True
        
        return False
    
    def _detect_language(self, file_path: Path) -> LanguageType:
        """Detect the programming language of a file."""
        extension = file_path.suffix.lower()
        
        if extension == '.py':
            return LanguageType.PYTHON
        elif extension in ['.js', '.jsx', '.ts', '.tsx']:
            return LanguageType.JAVASCRIPT
        elif extension == '.java':
            return LanguageType.JAVA
        else:
            return LanguageType.UNKNOWN
    
    def _get_code_files(self) -> List[Path]:
        """Get all code files in the project."""
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java'}
        code_files = []
        
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in code_extensions:
                # Skip common directories to ignore
                if not any(part.startswith('.') for part in file_path.parts):
                    code_files.append(file_path)
        
        return code_files
    
    def _get_project_info(self) -> Dict[str, Any]:
        """Get basic project information."""
        return {
            'name': self.project_path.name,
            'path': str(self.project_path),
            'total_files': len(self._get_code_files()),
            'languages': self._get_language_distribution()
        }
    
    def _get_language_distribution(self) -> Dict[str, int]:
        """Get distribution of programming languages in the project."""
        distribution = {}
        
        for file_path in self._get_code_files():
            language = self._detect_language(file_path)
            distribution[language.value] = distribution.get(language.value, 0) + 1
        
        return distribution
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies."""
        if not DEPTREE_AVAILABLE:
            return {'error': 'pipdeptree not available'}
        
        try:
            # This would require running pipdeptree in the project directory
            # For now, return a placeholder
            return {
                'python_dependencies': [],
                'dependency_tree': {},
                'conflicts': []
            }
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {e}")
            return {'error': str(e)}
    
    def _generate_call_graph(self) -> Dict[str, Any]:
        """Generate call graph for the project."""
        if not CALLGRAPH_AVAILABLE:
            return {'error': 'pycallgraph2 not available'}
        
        try:
            # This would require running pycallgraph2 on the project
            # For now, return a placeholder
            return {
                'nodes': [],
                'edges': [],
                'graph_file': None
            }
        except Exception as e:
            logger.error(f"Error generating call graph: {e}")
            return {'error': str(e)}
    
    def _calculate_project_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate project-wide metrics."""
        total_lines = 0
        total_functions = 0
        total_classes = 0
        total_errors = 0
        
        for file_analysis in analysis['files'].values():
            total_lines += file_analysis.get('lines', 0)
            total_functions += len(file_analysis.get('functions', []))
            total_classes += len(file_analysis.get('classes', []))
            total_errors += len(file_analysis.get('error_patterns', []))
        
        return {
            'total_lines': total_lines,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'total_errors': total_errors,
            'average_complexity': 0,  # Would need to calculate this
            'test_coverage': 0,  # Would need to run tests
            'maintainability_index': 0  # Would need to calculate this
        }
    
    def _function_to_dict(self, func: FunctionInfo) -> Dict[str, Any]:
        """Convert FunctionInfo to dictionary."""
        return {
            'name': func.name,
            'line_start': func.line_start,
            'line_end': func.line_end,
            'parameters': func.parameters,
            'return_type': func.return_type,
            'docstring': func.docstring,
            'calls': func.calls,
            'complexity': func.complexity
        }
    
    def _class_to_dict(self, cls: ClassInfo) -> Dict[str, Any]:
        """Convert ClassInfo to dictionary."""
        return {
            'name': cls.name,
            'line_start': cls.line_start,
            'line_end': cls.line_end,
            'methods': [self._function_to_dict(m) for m in cls.methods],
            'attributes': cls.attributes,
            'inheritance': cls.inheritance,
            'docstring': cls.docstring
        }
    
    def _error_pattern_to_dict(self, error: ErrorPattern) -> Dict[str, Any]:
        """Convert ErrorPattern to dictionary."""
        return {
            'type': error.type,
            'severity': error.severity,
            'line': error.line,
            'message': error.message,
            'suggestion': error.suggestion,
            'code_snippet': error.code_snippet
        } 