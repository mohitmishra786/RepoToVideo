"""
Step Generator Module

This module handles the generation of step-by-step analysis and execution plans
for creating video walkthroughs of GitHub repositories.
"""

import ast
import subprocess
import tempfile
import os
import sys
from typing import Dict, List, Optional, Tuple
import re


class StepGenerator:
    """Generates step-by-step analysis and execution plans for repositories."""
    
    def __init__(self):
        """Initialize the StepGenerator."""
        self.max_steps = 10
        self.step_duration = 30  # seconds per step
    
    def generate_steps(self, repo_analysis: Dict) -> List[Dict]:
        """
        Generate step-by-step analysis for the repository.
        
        Args:
            repo_analysis: Repository analysis from RepoFetcher
            
        Returns:
            List of step dictionaries
        """
        steps = []
        
        # Step 1: Introduction
        steps.append(self._create_intro_step(repo_analysis))
        
        # Step 2: Repository Overview
        if repo_analysis.get('readme'):
            steps.append(self._create_overview_step(repo_analysis))
        
        # Step 3: Structure Analysis
        steps.append(self._create_structure_step(repo_analysis))
        
        # Step 4-8: Code Analysis Steps
        code_steps = self._create_code_steps(repo_analysis)
        steps.extend(code_steps)
        
        # Step 9: Error Simulation
        if repo_analysis['main_files']:
            steps.append(self._create_error_simulation_step(repo_analysis))
        
        # Step 10: Summary
        steps.append(self._create_summary_step(repo_analysis))
        
        return steps[:self.max_steps]
    
    def _create_intro_step(self, repo_analysis: Dict) -> Dict:
        """Create the introduction step."""
        return {
            'id': 1,
            'title': f"Introduction to {repo_analysis['name']}",
            'type': 'intro',
            'duration': 20,
            'content': {
                'repo_name': repo_analysis['name'],
                'owner': repo_analysis['owner'],
                'description': repo_analysis['description'],
                'language': repo_analysis['language'],
                'stars': repo_analysis['stars'],
                'forks': repo_analysis['forks']
            },
            'voice_script': f"Welcome to this walkthrough of {repo_analysis['name']}, "
                          f"a {repo_analysis['language']} project by {repo_analysis['owner']}. "
                          f"This repository has {repo_analysis['stars']} stars and {repo_analysis['forks']} forks. "
                          f"Let's explore what makes this project interesting.",
            'visuals': ['repo_info', 'stats_display']
        }
    
    def _create_overview_step(self, repo_analysis: Dict) -> Dict:
        """Create the repository overview step."""
        readme = repo_analysis['readme']
        readme_sections = self._parse_readme_sections(readme['content'])
        
        return {
            'id': 2,
            'title': "Repository Overview",
            'type': 'overview',
            'duration': 25,
            'content': {
                'readme_title': readme_sections.get('title', ''),
                'description': readme_sections.get('description', ''),
                'code_blocks': readme_sections.get('code_blocks', [])[:3]
            },
            'voice_script': f"Let's start by looking at the README file. "
                          f"{readme_sections.get('title', 'This project')} "
                          f"provides a comprehensive overview of the codebase. "
                          f"The documentation includes several code examples that demonstrate key functionality.",
            'visuals': ['readme_display', 'code_highlight']
        }
    
    def _create_structure_step(self, repo_analysis: Dict) -> Dict:
        """Create the repository structure step."""
        structure = repo_analysis['structure']
        
        return {
            'id': 3,
            'title': "Repository Structure",
            'type': 'structure',
            'duration': 30,
            'content': {
                'total_files': structure['total_files'],
                'code_files': structure['code_files'],
                'doc_files': structure['doc_files'],
                'languages': structure['languages'],
                'directories': structure['directories'][:5]
            },
            'voice_script': f"The repository contains {structure['total_files']} files, "
                          f"including {structure['code_files']} code files and {structure['doc_files']} documentation files. "
                          f"The main programming language is {repo_analysis['language']}, "
                          f"and the code is organized into several directories for better structure.",
            'visuals': ['file_tree', 'language_stats']
        }
    
    def _create_code_steps(self, repo_analysis: Dict) -> List[Dict]:
        """Create steps for analyzing main code files."""
        steps = []
        main_files = repo_analysis['main_files']
        
        for i, file_info in enumerate(main_files[:5]):  # Limit to 5 main files
            if file_info['content'] and file_info['name'].endswith('.py'):
                step = self._create_python_code_step(file_info, i + 4)
                steps.append(step)
            else:
                step = self._create_generic_code_step(file_info, i + 4)
                steps.append(step)
        
        return steps
    
    def _create_python_code_step(self, file_info: Dict, step_id: int) -> Dict:
        """Create a step for analyzing Python code."""
        code_analysis = self._analyze_python_code(file_info['content'])
        
        # Generate execution plan
        execution_plan = self._generate_execution_plan(file_info['content'])
        
        return {
            'id': step_id,
            'title': f"Analyzing {file_info['name']}",
            'type': 'code_analysis',
            'duration': 35,
            'content': {
                'filename': file_info['name'],
                'filepath': file_info['path'],
                'code_content': file_info['content'],
                'analysis': code_analysis,
                'execution_plan': execution_plan
            },
            'voice_script': f"Now let's examine {file_info['name']}. "
                          f"This file contains {len(code_analysis['functions'])} functions "
                          f"and {len(code_analysis['classes'])} classes. "
                          f"The code imports {len(code_analysis['imports'])} modules "
                          f"and defines several key variables. Let's see how it executes.",
            'visuals': ['code_highlight', 'ast_diagram', 'execution_flow']
        }
    
    def _create_generic_code_step(self, file_info: Dict, step_id: int) -> Dict:
        """Create a step for analyzing non-Python code."""
        return {
            'id': step_id,
            'title': f"Examining {file_info['name']}",
            'type': 'code_review',
            'duration': 25,
            'content': {
                'filename': file_info['name'],
                'filepath': file_info['path'],
                'code_content': file_info['content'],
                'language': self._detect_language(file_info['name'])
            },
            'voice_script': f"This is a {self._detect_language(file_info['name'])} file. "
                          f"While we can't execute it directly, we can analyze its structure "
                          f"and understand its role in the project.",
            'visuals': ['code_highlight', 'syntax_tree']
        }
    
    def _create_error_simulation_step(self, repo_analysis: Dict) -> Dict:
        """Create a step for simulating common errors."""
        # Find a Python file to simulate errors in
        python_files = [f for f in repo_analysis['main_files'] 
                       if f['content'] and f['name'].endswith('.py')]
        
        if not python_files:
            return self._create_generic_error_step()
        
        file_info = python_files[0]
        error_simulations = self._generate_error_simulations(file_info['content'])
        
        return {
            'id': len(repo_analysis['main_files']) + 4,
            'title': "Error Handling and Debugging",
            'type': 'error_simulation',
            'duration': 40,
            'content': {
                'filename': file_info['name'],
                'original_code': file_info['content'],
                'error_simulations': error_simulations
            },
            'voice_script': f"Let's explore some common errors that might occur when working with this code. "
                          f"We'll simulate a few scenarios and show how to debug and fix them. "
                          f"This helps us understand the robustness of the codebase.",
            'visuals': ['error_display', 'fix_animation', 'before_after']
        }
    
    def _create_summary_step(self, repo_analysis: Dict) -> Dict:
        """Create the summary step."""
        structure = repo_analysis['structure']
        
        return {
            'id': len(repo_analysis['main_files']) + 5,
            'title': "Summary and Key Takeaways",
            'type': 'summary',
            'duration': 30,
            'content': {
                'total_files': structure['total_files'],
                'main_language': repo_analysis['language'],
                'key_features': self._extract_key_features(repo_analysis),
                'best_practices': self._generate_best_practices(repo_analysis)
            },
            'voice_script': f"We've successfully explored {repo_analysis['name']}, "
                          f"a {repo_analysis['language']} project with {structure['total_files']} files. "
                          f"The code demonstrates good practices in organization and documentation. "
                          f"Remember to always read the README and understand the project structure before diving into the code.",
            'visuals': ['summary_slide', 'key_points', 'best_practices']
        }
    
    def _parse_readme_sections(self, readme_content: str) -> Dict:
        """Parse README content into sections."""
        sections = {
            'title': '',
            'description': '',
            'code_blocks': []
        }
        
        # Extract title
        title_match = re.search(r'^#\s+(.+)$', readme_content, re.MULTILINE)
        if title_match:
            sections['title'] = title_match.group(1)
        
        # Extract code blocks
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', readme_content, re.DOTALL)
        sections['code_blocks'] = code_blocks
        
        # Extract description (first paragraph after title)
        lines = readme_content.split('\n')
        description_lines = []
        found_title = False
        
        for line in lines:
            if line.startswith('#') and not found_title:
                found_title = True
                continue
            elif line.startswith('#') and found_title:
                break
            elif found_title and line.strip():
                description_lines.append(line)
                if len(description_lines) >= 3:  # Limit to first 3 lines
                    break
        
        sections['description'] = ' '.join(description_lines)
        return sections
    
    def _analyze_python_code(self, code_content: str) -> Dict:
        """Analyze Python code using AST."""
        try:
            tree = ast.parse(code_content)
            analysis = {
                'imports': [],
                'functions': [],
                'classes': [],
                'variables': [],
                'lines': len(code_content.split('\n'))
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        analysis['imports'].append(f"{module}.{alias.name}")
                elif isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'lineno': node.lineno
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'lineno': node.lineno
                    })
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            analysis['variables'].append(target.id)
            
            return analysis
        except SyntaxError:
            return {
                'imports': [],
                'functions': [],
                'classes': [],
                'variables': [],
                'lines': len(code_content.split('\n')),
                'error': 'Syntax error in code'
            }
    
    def _generate_execution_plan(self, code_content: str) -> List[Dict]:
        """Generate an execution plan for the code."""
        plan = []
        lines = code_content.split('\n')
        
        # Simple execution plan based on code structure
        current_block = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                plan.append({
                    'type': 'import',
                    'line': i + 1,
                    'content': line,
                    'description': f"Importing {line.split()[-1]}"
                })
            elif line.startswith('def '):
                if current_block:
                    plan.append({
                        'type': 'code_block',
                        'lines': [l + 1 for l in current_block],
                        'content': '\n'.join(lines[current_block[0]:current_block[-1] + 1]),
                        'description': "Executing code block"
                    })
                    current_block = []
                
                func_name = line.split('(')[0].split()[-1]
                plan.append({
                    'type': 'function_def',
                    'line': i + 1,
                    'content': line,
                    'description': f"Defining function {func_name}"
                })
            elif line.startswith('class '):
                if current_block:
                    plan.append({
                        'type': 'code_block',
                        'lines': [l + 1 for l in current_block],
                        'content': '\n'.join(lines[current_block[0]:current_block[-1] + 1]),
                        'description': "Executing code block"
                    })
                    current_block = []
                
                class_name = line.split('(')[0].split()[-1]
                plan.append({
                    'type': 'class_def',
                    'line': i + 1,
                    'content': line,
                    'description': f"Defining class {class_name}"
                })
            elif line and not line.startswith('#'):
                current_block.append(i)
        
        # Add remaining code block
        if current_block:
            plan.append({
                'type': 'code_block',
                'lines': [l + 1 for l in current_block],
                'content': '\n'.join(lines[current_block[0]:current_block[-1] + 1]),
                'description': "Executing main code"
            })
        
        return plan
    
    def _generate_error_simulations(self, code_content: str) -> List[Dict]:
        """Generate error simulations for the code."""
        simulations = []
        
        # Common error types to simulate
        error_types = [
            {
                'type': 'syntax_error',
                'description': 'Missing colon after function definition',
                'original': 'def my_function()',
                'error': 'def my_function()',
                'fix': 'def my_function():'
            },
            {
                'type': 'name_error',
                'description': 'Undefined variable',
                'original': 'print(undefined_variable)',
                'error': 'print(undefined_variable)',
                'fix': 'undefined_variable = "some_value"\nprint(undefined_variable)'
            },
            {
                'type': 'indentation_error',
                'description': 'Incorrect indentation',
                'original': 'def test():\nprint("test")',
                'error': 'def test():\nprint("test")',
                'fix': 'def test():\n    print("test")'
            }
        ]
        
        for error in error_types:
            simulations.append({
                'error_type': error['type'],
                'description': error['description'],
                'original_code': error['original'],
                'error_code': error['error'],
                'fixed_code': error['fix'],
                'error_message': self._get_error_message(error['type'])
            })
        
        return simulations
    
    def _get_error_message(self, error_type: str) -> str:
        """Get a realistic error message for the error type."""
        messages = {
            'syntax_error': "SyntaxError: invalid syntax",
            'name_error': "NameError: name 'undefined_variable' is not defined",
            'indentation_error': "IndentationError: expected an indented block"
        }
        return messages.get(error_type, "Error occurred")
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename."""
        extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.m': 'Objective-C',
            '.sh': 'Shell'
        }
        
        for ext, lang in extensions.items():
            if filename.endswith(ext):
                return lang
        return 'Unknown'
    
    def _create_generic_error_step(self) -> Dict:
        """Create a generic error simulation step."""
        return {
            'id': 9,
            'title': "Common Programming Errors",
            'type': 'error_simulation',
            'duration': 30,
            'content': {
                'error_simulations': [
                    {
                        'error_type': 'general',
                        'description': 'Common programming mistakes',
                        'examples': [
                            'Forgetting to import modules',
                            'Using undefined variables',
                            'Incorrect function calls'
                        ]
                    }
                ]
            },
            'voice_script': "Let's discuss some common programming errors that developers might encounter "
                          "when working with this type of code, and how to avoid them.",
            'visuals': ['error_examples', 'best_practices']
        }
    
    def _extract_key_features(self, repo_analysis: Dict) -> List[str]:
        """Extract key features from the repository analysis."""
        features = []
        
        if repo_analysis['language']:
            features.append(f"Written in {repo_analysis['language']}")
        
        if repo_analysis['structure']['code_files'] > 0:
            features.append(f"{repo_analysis['structure']['code_files']} code files")
        
        if repo_analysis['readme']:
            features.append("Comprehensive documentation")
        
        if repo_analysis['stars'] > 100:
            features.append("Popular project with many stars")
        
        if len(repo_analysis['structure']['directories']) > 2:
            features.append("Well-organized directory structure")
        
        return features
    
    def _generate_best_practices(self, repo_analysis: Dict) -> List[str]:
        """Generate best practices based on repository analysis."""
        practices = [
            "Always read the README file first",
            "Understand the project structure",
            "Check for documentation and examples",
            "Look at the main entry points",
            "Test the code before making changes"
        ]
        
        if repo_analysis['language'] == 'Python':
            practices.extend([
                "Use virtual environments",
                "Follow PEP 8 style guidelines",
                "Write docstrings for functions"
            ])
        
        return practices 