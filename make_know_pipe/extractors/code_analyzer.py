"""
Code Analyzer - Extract implementation patterns and knowledge from source code

Focuses on extracting "how to build" knowledge rather than just documenting what exists.
"""

import os
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from .llm_router import LLMRouter, ContentType

logger = logging.getLogger(__name__)

class CodePattern:
    """Represents an extracted code pattern"""
    def __init__(self, name: str, description: str, code_example: str, 
                 implementation_guide: str, file_path: str):
        self.name = name
        self.description = description
        self.code_example = code_example
        self.implementation_guide = implementation_guide
        self.file_path = file_path

class CodeAnalyzer:
    """Extract implementation knowledge from source code"""
    
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        self.supported_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP'
        }
    
    async def extract_implementation_patterns(self, source_paths: List[str]) -> Dict[str, List[CodePattern]]:
        """
        Extract implementation patterns organized by feature/system
        
        Args:
            source_paths: List of source directories or files
            
        Returns:
            Dictionary mapping feature names to implementation patterns
        """
        logger.info(f"Analyzing {len(source_paths)} source paths")
        
        # Collect all source files
        all_files = []
        for path in source_paths:
            all_files.extend(self._find_source_files(path))
        
        logger.info(f"Found {len(all_files)} source files")
        
        # Group files by likely feature/system
        feature_groups = self._group_files_by_feature(all_files)
        
        # Extract patterns for each feature group
        results = {}
        for feature_name, files in feature_groups.items():
            logger.info(f"Extracting patterns for {feature_name}")
            patterns = await self._extract_feature_patterns(feature_name, files)
            if patterns:
                results[feature_name] = patterns
        
        return results
    
    def _find_source_files(self, path: str) -> List[str]:
        """Find all source files in a path"""
        path_obj = Path(path)
        files = []
        
        if path_obj.is_file():
            if path_obj.suffix.lower() in self.supported_extensions:
                files.append(str(path_obj))
        elif path_obj.is_dir():
            for ext in self.supported_extensions.keys():
                files.extend([str(f) for f in path_obj.rglob(f'*{ext}')])
        
        return files
    
    def _group_files_by_feature(self, files: List[str]) -> Dict[str, List[str]]:
        """Group files by likely feature or system"""
        groups = {}
        
        for file_path in files:
            path_obj = Path(file_path)
            parts = path_obj.parts
            
            # Try to identify feature from path structure
            feature = self._identify_feature_from_path(parts)
            
            if feature not in groups:
                groups[feature] = []
            groups[feature].append(file_path)
        
        return groups
    
    def _identify_feature_from_path(self, path_parts: tuple) -> str:
        """Identify feature/system from file path parts"""
        # Common feature indicators
        feature_keywords = {
            'auth': 'authentication',
            'login': 'authentication', 
            'user': 'user_management',
            'api': 'api_endpoints',
            'model': 'data_models',
            'database': 'database_integration',
            'db': 'database_integration',
            'payment': 'payment_processing',
            'email': 'email_system',
            'notification': 'notification_system',
            'upload': 'file_handling',
            'file': 'file_handling',
            'config': 'configuration',
            'middleware': 'middleware_patterns',
            'util': 'utility_functions',
            'helper': 'utility_functions',
            'test': 'testing_patterns',
            'admin': 'admin_interface'
        }
        
        # Check each part of the path
        for part in path_parts:
            part_lower = part.lower()
            for keyword, feature in feature_keywords.items():
                if keyword in part_lower:
                    return feature
        
        # Default grouping
        if len(path_parts) >= 2:
            return path_parts[-2]  # Use parent directory name
        else:
            return 'general'
    
    async def _extract_feature_patterns(self, feature_name: str, files: List[str]) -> List[CodePattern]:
        """Extract implementation patterns for a specific feature"""
        patterns = []
        
        # Analyze key files for this feature (limit to avoid overwhelming LLM)
        key_files = self._select_key_files(files)
        
        for file_path in key_files[:5]:  # Limit to 5 files per feature
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if len(content.strip()) < 50:  # Skip very small files
                    continue
                
                # Extract patterns from this file
                file_patterns = await self._analyze_file_for_patterns(file_path, content, feature_name)
                patterns.extend(file_patterns)
                
            except Exception as e:
                logger.warning(f"Could not analyze file {file_path}: {e}")
        
        return patterns
    
    def _select_key_files(self, files: List[str]) -> List[str]:
        """Select the most important files for analysis"""
        # Sort by file size (larger files likely more important) and take top files
        file_sizes = []
        for file_path in files:
            try:
                size = Path(file_path).stat().st_size
                file_sizes.append((file_path, size))
            except Exception:
                continue
        
        # Sort by size, but not too large (skip generated files)
        file_sizes = [(f, s) for f, s in file_sizes if 100 < s < 50000]
        file_sizes.sort(key=lambda x: x[1], reverse=True)
        
        return [f[0] for f in file_sizes]
    
    async def _analyze_file_for_patterns(self, file_path: str, content: str, feature_name: str) -> List[CodePattern]:
        """Analyze a single file for implementation patterns"""
        
        prompt = f"""Analyze this {feature_name} code and extract implementation patterns that would help someone build a similar system.

For each significant pattern you find, provide:

1. **Pattern Name**: A clear, descriptive name
2. **What it does**: Brief explanation of the pattern's purpose  
3. **How to implement**: Step-by-step guide to implement this pattern
4. **Code example**: The key code that demonstrates the pattern
5. **Why this approach**: Reasoning behind the design decisions

Focus on patterns that are:
- Reusable in similar projects
- Demonstrate good architectural decisions
- Show how to solve common problems
- Include error handling or edge cases

File: {Path(file_path).name}
Feature: {feature_name}

Make your response educational - someone should be able to follow your guidance to implement similar functionality."""

        try:
            result = await self.llm_router.analyze_content(
                content, ContentType.CODE, prompt
            )
            
            # Parse the result into CodePattern objects
            patterns = self._parse_pattern_analysis(result, file_path)
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return []
    
    def _parse_pattern_analysis(self, analysis: str, file_path: str) -> List[CodePattern]:
        """Parse LLM analysis into CodePattern objects"""
        patterns = []
        
        # Simple parsing - look for pattern sections
        sections = analysis.split('\n\n')
        current_pattern = {}
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Look for pattern indicators
            if 'Pattern Name:' in section or '1. **Pattern Name**' in section:
                # Save previous pattern if exists
                if current_pattern.get('name'):
                    pattern = self._create_pattern_from_dict(current_pattern, file_path)
                    if pattern:
                        patterns.append(pattern)
                
                # Start new pattern
                current_pattern = {'raw_section': section}
                
                # Try to extract name
                if 'Pattern Name:' in section:
                    name_line = [line for line in section.split('\n') if 'Pattern Name:' in line]
                    if name_line:
                        current_pattern['name'] = name_line[0].split('Pattern Name:')[1].strip()
            
            elif current_pattern and any(key in section.lower() for key in ['what it does', 'how to implement', 'code example']):
                current_pattern['raw_section'] = current_pattern.get('raw_section', '') + '\n\n' + section
        
        # Don't forget the last pattern
        if current_pattern.get('name'):
            pattern = self._create_pattern_from_dict(current_pattern, file_path)
            if pattern:
                patterns.append(pattern)
        
        # If no structured patterns found, create a general one
        if not patterns and len(analysis) > 100:
            patterns.append(CodePattern(
                name=f"Implementation Pattern from {Path(file_path).name}",
                description="General implementation pattern extracted from code analysis",
                code_example="See full analysis for code examples",
                implementation_guide=analysis,
                file_path=file_path
            ))
        
        return patterns
    
    def _create_pattern_from_dict(self, pattern_dict: Dict, file_path: str) -> Optional[CodePattern]:
        """Create CodePattern from parsed dictionary"""
        try:
            raw_section = pattern_dict.get('raw_section', '')
            name = pattern_dict.get('name', f"Pattern from {Path(file_path).name}")
            
            # Extract basic info from raw section
            description = "Implementation pattern"
            code_example = "See implementation guide for details"
            implementation_guide = raw_section
            
            # Try to extract description and code example from raw section
            lines = raw_section.split('\n')
            for i, line in enumerate(lines):
                if 'what it does' in line.lower() and i + 1 < len(lines):
                    description = lines[i + 1].strip()
                elif 'code example' in line.lower():
                    # Try to find code block
                    remaining_lines = lines[i + 1:]
                    code_lines = []
                    in_code = False
                    for remaining_line in remaining_lines:
                        if '```' in remaining_line:
                            in_code = not in_code
                        elif in_code:
                            code_lines.append(remaining_line)
                        elif code_lines:
                            break
                    if code_lines:
                        code_example = '\n'.join(code_lines)
            
            return CodePattern(
                name=name,
                description=description,
                code_example=code_example,
                implementation_guide=implementation_guide,
                file_path=file_path
            )
            
        except Exception as e:
            logger.warning(f"Could not create pattern from dict: {e}")
            return None