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
    
"""
    Performs __init__ operation. Function has side effects. Takes self and project_path as input. Returns a object value.
    :param self: The self object.
    :param project_path: The project_path string.
    :return: Value of type object
"""
    def __init__(self, project_path: str):
        """
        Initialize the code analyzer.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = Path(project_path)
        self.language_parsers = {}
        self._setup_tree_sitter()
        
"""
    Performs _setup_tree_sitter operation. Function conditionally processes input, may return early, has side effects. Takes self as input. Returns a object value.
    :param self: The self object.
    :return: Value of type object
"""
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
    
"""
    Performs analyze_project operation. Function iterates over data, has side effects, performs arithmetic operations. Takes self as input. Returns a dict[(str, any)] value.
    :param self: The self object.
    :return: Value of type Dict[(str, Any)]
"""
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
        
        # Get all code files
        code_files = self._get_code_files()
        logger.info(f"Found {len(code_files)} code files to analyze")
        
        successful_analyses = 0
        failed_analyses = 0
        
        # Analyze each file
        for i, file_path in enumerate(code_files):
            logger.info(f"Analyzing file {i+1}/{len(code_files)}: {file_path}")
            try:
                file_analysis = self.analyze_file(file_path)
                analysis['files'][str(file_path)] = file_analysis
                analysis['error_patterns'].extend(file_analysis.get('error_patterns', []))
                successful_analyses += 1
                logger.info(f"✅ Successfully analyzed: {file_path}")
            except Exception as e:
                failed_analyses += 1
                logger.error(f"❌ Error analyzing {file_path}: {e}")
                # Add a basic file entry even if analysis fails
                analysis['files'][str(file_path)] = {
                    'language': 'unknown',
                    'size': 0,
                    'lines': 0,
                    'functions': [],
                    'classes': [],
                    'imports': [],
                    'error_patterns': [],
                    'complexity': 0,
                    'analysis_error': str(e)
                }
        
        logger.info(f"Analysis complete: {successful_analyses} successful, {failed_analyses} failed")
        
        # Calculate project metrics
        analysis['metrics'] = self._calculate_project_metrics(analysis)
        
        return analysis
    
"""
    Performs analyze_file operation. Function conditionally processes input, may throw exceptions, has side effects, performs file operations. Takes self and file_path as input. Returns a dict[(str, any)] value.
    :param self: The self object.
    :param file_path: The file_path value of type Path.
    :return: Value of type Dict[(str, Any)]
"""
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a single file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary containing file analysis
        """
        logger.debug(f"Starting analysis of {file_path}")
        
        language = self._detect_language(file_path)
        logger.debug(f"Detected language: {language.value}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"Read {len(content)} characters from {file_path}")
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise
        
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
        
        logger.debug(f"Basic analysis: {analysis['lines']} lines, {analysis['size']} bytes")
        
        try:
            if language == LanguageType.PYTHON:
                logger.debug(f"Analyzing as Python file")
                analysis.update(self._analyze_python_file(content, file_path))
            elif language == LanguageType.JAVASCRIPT:
                logger.debug(f"Analyzing as JavaScript file")
                analysis.update(self._analyze_javascript_file(content, file_path))
            elif language == LanguageType.JAVA:
                logger.debug(f"Analyzing as Java file")
                analysis.update(self._analyze_java_file(content, file_path))
            else:
                logger.debug(f"Unknown language, skipping detailed analysis")
        except Exception as e:
            logger.error(f"Error in detailed analysis of {file_path}: {e}")
            raise
        
        logger.debug(f"Analysis complete for {file_path}: {len(analysis.get('functions', []))} functions, {len(analysis.get('classes', []))} classes")
        
        return analysis
    
"""
    Performs _analyze_python_file operation. Function iterates over data, conditionally processes input, may throw exceptions, may return early, has side effects, performs arithmetic operations. Takes self, content and file_path as input. Returns a dict[(str, any)] value.
    :param self: The self object.
    :param content: The content string.
    :param file_path: The file_path value of type Path.
    :return: Value of type Dict[(str, Any)]
"""
    def _analyze_python_file(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file using AST."""
        logger.debug(f"Starting Python AST analysis for {file_path}")
        
        try:
            logger.debug(f"Parsing AST for {file_path}")
            tree = ast.parse(content)
            logger.debug(f"AST parsing successful for {file_path}")
            
            functions = []
            classes = []
            imports = []
            error_patterns = []
            
            logger.debug(f"Walking AST nodes for {file_path}")
            for node in ast.walk(tree):
                try:
                    if isinstance(node, ast.FunctionDef):
                        logger.debug(f"Found function: {node.name}")
                        func_info = self._extract_function_info(node, content)
                        functions.append(func_info)
                        
                    elif isinstance(node, ast.ClassDef):
                        logger.debug(f"Found class: {node.name}")
                        class_info = self._extract_class_info(node, content)
                        classes.append(class_info)
                        
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        logger.debug(f"Found import statement")
                        import_info = self._extract_import_info(node)
                        imports.append(import_info)
                except Exception as e:
                    logger.error(f"Error processing AST node in {file_path}: {e}")
                    # Continue processing other nodes instead of failing completely
                    continue
            
            logger.debug(f"AST walk complete for {file_path}: {len(functions)} functions, {len(classes)} classes, {len(imports)} imports")
            
            # Detect error patterns
            try:
                logger.debug(f"Detecting error patterns for {file_path}")
                error_patterns = self._detect_python_error_patterns(tree, content)
                logger.debug(f"Found {len(error_patterns)} error patterns in {file_path}")
            except Exception as e:
                logger.error(f"Error detecting patterns in {file_path}: {e}")
                error_patterns = []
            
            result = {
                'functions': [self._function_to_dict(f) for f in functions],
                'classes': [self._class_to_dict(c) for c in classes],
                'imports': imports,
                'error_patterns': [self._error_pattern_to_dict(e) for e in error_patterns]
            }
            
            logger.debug(f"Python analysis complete for {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"AST parsing failed for {file_path}: {e}")
            raise
            
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
    
"""
    Performs _analyze_javascript_file operation. Function has side effects. Takes self, content and file_path as input. Returns a dict[(str, any)] value.
    :param self: The self object.
    :param content: The content string.
    :param file_path: The file_path value of type Path.
    :return: Value of type Dict[(str, Any)]
"""
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
    
"""
    Performs _analyze_java_file operation. Function has side effects. Takes self, content and file_path as input. Returns a dict[(str, any)] value.
    :param self: The self object.
    :param content: The content string.
    :param file_path: The file_path value of type Path.
    :return: Value of type Dict[(str, Any)]
"""
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
    
"""
    Performs _extract_function_info operation. Function iterates over data, conditionally processes input, has side effects. Takes self, node and content as input. Returns a functioninfo value.
    :param self: The self object.
    :param node: The node value of type ast.FunctionDef.
    :param content: The content string.
    :return: Value of type FunctionInfo
"""
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
    
"""
    Performs _extract_class_info operation. Function iterates over data, conditionally processes input, has side effects. Takes self, node and content as input. Returns a classinfo value.
    :param self: The self object.
    :param node: The node value of type ast.ClassDef.
    :param content: The content string.
    :return: Value of type ClassInfo
"""
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
    
"""
    Performs _extract_import_info operation. Function conditionally processes input, may return early, has side effects. Takes self and node as input. Returns a dict[(str, any)] value.
    :param self: The self object.
    :param node: The node value of type Union[(ast.Import, ast.ImportFrom)].
    :return: Value of type Dict[(str, Any)]
"""
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
    
"""
    Performs _detect_python_error_patterns operation. Function iterates over data, conditionally processes input, has side effects, performs arithmetic operations. Takes self, tree and content as input. Returns a list[errorpattern] value.
    :param self: The self object.
    :param tree: The tree value of type ast.AST.
    :param content: The content string.
    :return: Value of type List[ErrorPattern]
"""
    def _detect_python_error_patterns(self, tree: ast.AST, content: str) -> List[ErrorPattern]:
        """Detect common error patterns in Python code."""
        patterns = []
        lines = content.splitlines()
        
        try:
            for node in ast.walk(tree):
                try:
                    # Undefined variables
                    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                        if hasattr(node, 'id') and hasattr(node, 'lineno'):
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
                                if hasattr(node, 'lineno'):
                                    patterns.append(ErrorPattern(
                                        type='type_mismatch',
                                        severity='warning',
                                        line=node.lineno,
                                        message="Potential type mismatch in addition",
                                        suggestion="Convert types explicitly or use proper types",
                                        code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else ''
                                    ))
                except Exception as e:
                    logger.debug(f"Error processing AST node in error pattern detection: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error in error pattern detection: {e}")
        
        return patterns
    
"""
    Performs _is_variable_defined operation. Function iterates over data, conditionally processes input, may return early, has side effects. Takes self, var_name, node and tree as input. Returns true or false.
    :param self: The self object.
    :param var_name: The var_name string.
    :param node: The node value of type ast.AST.
    :param tree: The tree value of type ast.AST.
    :return: True or false
"""
    def _is_variable_defined(self, var_name: str, node: ast.AST, tree: ast.AST) -> bool:
        """Check if a variable is defined before use."""
        # Simplified check - in a real implementation, this would be more sophisticated
        try:
            for ancestor in self._get_ancestors(node, tree):
                if isinstance(ancestor, ast.FunctionDef):
                    # Check function parameters
                    if var_name in [arg.arg for arg in ancestor.args.args]:
                        return True
                elif isinstance(ancestor, ast.ClassDef):
                    # Check class attributes - safely access .id attribute
                    for attr in ancestor.body:
                        if isinstance(attr, ast.Assign) and attr.targets:
                            target = attr.targets[0]
                            if isinstance(target, ast.Name) and hasattr(target, 'id'):
                                if target.id == var_name:
                                    return True
        except Exception as e:
            logger.debug(f"Error checking variable definition for {var_name}: {e}")
        
        return False
    
"""
    Performs _get_ancestors operation. Function iterates over data, conditionally processes input, has side effects. Takes self, node and tree as input. Returns a list[ast.ast] value.
    :param self: The self object.
    :param node: The node value of type ast.AST.
    :param tree: The tree value of type ast.AST.
    :return: Value of type List[ast.AST]
"""
    def _get_ancestors(self, node: ast.AST, tree: ast.AST) -> List[ast.AST]:
        """Get ancestor nodes of a given node."""
        # Simplified implementation
        ancestors = []
        for n in ast.walk(tree):
            if hasattr(n, 'body') and node in ast.walk(n):
                ancestors.append(n)
        return ancestors
    
"""
    Performs _get_return_type_annotation operation. Function conditionally processes input, may return early, has side effects. Takes self and node as input. Returns a optional[str] value.
    :param self: The self object.
    :param node: The node value of type ast.FunctionDef.
    :return: Value of type Optional[str]
"""
    def _get_return_type_annotation(self, node: ast.FunctionDef) -> Optional[str]:
        """Get return type annotation from function."""
        try:
            if node.returns:
                if isinstance(node.returns, ast.Name) and hasattr(node.returns, 'id'):
                    return node.returns.id
                elif isinstance(node.returns, ast.Constant) and hasattr(node.returns, 'value'):
                    return str(node.returns.value)
        except Exception as e:
            logger.debug(f"Error getting return type annotation: {e}")
        return None
    
"""
    Performs _extract_js_functions operation. Function iterates over data, has side effects, performs arithmetic operations. Takes self and content as input. Returns a list[dict[(str, any)]] value.
    :param self: The self object.
    :param content: The content string.
    :return: Value of type List[Dict[(str, Any)]]
"""
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
    
"""
    Performs _extract_js_classes operation. Function iterates over data, conditionally processes input, has side effects, performs arithmetic operations. Takes self and content as input. Returns a list[dict[(str, any)]] value.
    :param self: The self object.
    :param content: The content string.
    :return: Value of type List[Dict[(str, Any)]]
"""
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
    
"""
    Performs _extract_js_imports operation. Function iterates over data, has side effects, performs arithmetic operations. Takes self and content as input. Returns a list[dict[(str, any)]] value.
    :param self: The self object.
    :param content: The content string.
    :return: Value of type List[Dict[(str, Any)]]
"""
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
    
"""
    Performs _detect_js_error_patterns operation. Function iterates over data, conditionally processes input, has side effects, performs arithmetic operations. Takes self and content as input. Returns a list[dict[(str, any)]] value.
    :param self: The self object.
    :param content: The content string.
    :return: Value of type List[Dict[(str, Any)]]
"""
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
    
"""
    Performs _is_js_variable_defined operation. Function iterates over data, conditionally processes input, may return early, has side effects. Takes self, var_name, content and position as input. Returns true or false.
    :param self: The self object.
    :param var_name: The var_name string.
    :param content: The content string.
    :param position: The position integer.
    :return: True or false
"""
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
    
"""
    Performs _extract_java_methods operation. Function iterates over data, has side effects, performs arithmetic operations. Takes self and content as input. Returns a list[dict[(str, any)]] value.
    :param self: The self object.
    :param content: The content string.
    :return: Value of type List[Dict[(str, Any)]]
"""
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
    
"""
    Performs _extract_java_classes operation. Function iterates over data, conditionally processes input, has side effects, performs arithmetic operations. Takes self and content as input. Returns a list[dict[(str, any)]] value.
    :param self: The self object.
    :param content: The content string.
    :return: Value of type List[Dict[(str, Any)]]
"""
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
    
"""
    Performs _extract_java_imports operation. Function iterates over data, has side effects, performs arithmetic operations. Takes self and content as input. Returns a list[dict[(str, any)]] value.
    :param self: The self object.
    :param content: The content string.
    :return: Value of type List[Dict[(str, Any)]]
"""
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
    
"""
    Performs _detect_java_error_patterns operation. Function iterates over data, conditionally processes input, has side effects, performs arithmetic operations. Takes self and content as input. Returns a list[dict[(str, any)]] value.
    :param self: The self object.
    :param content: The content string.
    :return: Value of type List[Dict[(str, Any)]]
"""
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
    
"""
    Performs _is_java_variable_defined operation. Function iterates over data, conditionally processes input, may return early, has side effects. Takes self, var_name, content and position as input. Returns true or false.
    :param self: The self object.
    :param var_name: The var_name string.
    :param content: The content string.
    :param position: The position integer.
    :return: True or false
"""
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
    
"""
    Performs _detect_language operation. Function conditionally processes input, may return early, has side effects. Takes self and file_path as input. Returns a languagetype value.
    :param self: The self object.
    :param file_path: The file_path value of type Path.
    :return: Value of type LanguageType
"""
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
    
"""
    Performs _get_code_files operation. Function iterates over data, conditionally processes input, has side effects, performs arithmetic operations. Takes self as input. Returns a list[path] value.
    :param self: The self object.
    :return: Value of type List[Path]
"""
    def _get_code_files(self) -> List[Path]:
        """Get all code files in the project."""
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java'}
        code_files = []
        
        # Directories to skip
        skip_dirs = {'.git', '.vscode', '.idea', '__pycache__', 'node_modules', '.pytest_cache', '.mypy_cache'}
        
        logger.info(f"Scanning for code files in {self.project_path}")
        logger.info(f"Looking for extensions: {code_extensions}")
        logger.info(f"Skipping directories: {skip_dirs}")
        
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in code_extensions:
                # Skip files in directories we want to ignore
                if not any(part in skip_dirs for part in file_path.parts):
                    code_files.append(file_path)
                    logger.debug(f"Found code file: {file_path}")
                else:
                    logger.debug(f"Skipping file in ignored directory: {file_path}")
        
        logger.info(f"Found {len(code_files)} code files in {self.project_path}")
        
        # Log all found files
        for i, file_path in enumerate(code_files):
            logger.info(f"  {i+1}. {file_path}")
        
        return code_files
    
"""
    Performs _get_project_info operation. Function has side effects. Takes self as input. Returns a dict[(str, any)] value.
    :param self: The self object.
    :return: Value of type Dict[(str, Any)]
"""
    def _get_project_info(self) -> Dict[str, Any]:
        """Get basic project information."""
        return {
            'name': self.project_path.name,
            'path': str(self.project_path),
            'total_files': len(self._get_code_files()),
            'languages': self._get_language_distribution()
        }
    
"""
    Performs _get_language_distribution operation. Function iterates over data, has side effects, performs arithmetic operations. Takes self as input. Returns a dict[(str, int)] value.
    :param self: The self object.
    :return: Value of type Dict[(str, int)]
"""
    def _get_language_distribution(self) -> Dict[str, int]:
        """Get distribution of programming languages in the project."""
        distribution = {}
        
        for file_path in self._get_code_files():
            language = self._detect_language(file_path)
            distribution[language.value] = distribution.get(language.value, 0) + 1
        
        return distribution
    
"""
    Performs _analyze_dependencies operation. Function conditionally processes input, may return early, has side effects. Takes self as input. Returns a dict[(str, any)] value.
    :param self: The self object.
    :return: Value of type Dict[(str, Any)]
"""
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
    
"""
    Performs _generate_call_graph operation. Function conditionally processes input, may return early, has side effects. Takes self as input. Returns a dict[(str, any)] value.
    :param self: The self object.
    :return: Value of type Dict[(str, Any)]
"""
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
    
"""
    Performs _calculate_project_metrics operation. Function iterates over data, has side effects. Takes self and analysis as input. Returns a dict[(str, any)] value.
    :param self: The self object.
    :param analysis: The analysis value of type Dict[(str, Any)].
    :return: Value of type Dict[(str, Any)]
"""
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
    
"""
    Performs _function_to_dict operation. Takes self and func as input. Returns a dict[(str, any)] value.
    :param self: The self object.
    :param func: The func value of type FunctionInfo.
    :return: Value of type Dict[(str, Any)]
"""
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
    
"""
    Performs _class_to_dict operation. Function has side effects. Takes self and cls as input. Returns a dict[(str, any)] value.
    :param self: The self object.
    :param cls: The cls value of type ClassInfo.
    :return: Value of type Dict[(str, Any)]
"""
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
    
"""
    Performs _error_pattern_to_dict operation. Takes self and error as input. Returns a dict[(str, any)] value.
    :param self: The self object.
    :param error: The error value of type ErrorPattern.
    :return: Value of type Dict[(str, Any)]
"""
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