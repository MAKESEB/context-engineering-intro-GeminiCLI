"""
Source Analysis Generator - Auto-generate contextual SOURCE_ANALYSIS.md

Creates custom SOURCE_ANALYSIS.md files based on discovered data patterns,
making the system adaptive to different use cases and data types.
"""

import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging

from ..extractors.data_discovery import DataPattern
from ..extractors.llm_router import LLMRouter, ContentType

logger = logging.getLogger(__name__)

class SourceAnalysisGenerator:
    """Generate contextual SOURCE_ANALYSIS.md based on discovered data patterns"""
    
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
    
    async def generate_source_analysis(self, 
                                     data_patterns: Dict[str, List[DataPattern]], 
                                     data_dir: str,
                                     use_case_description: str = "") -> str:
        """
        Generate a contextual SOURCE_ANALYSIS.md based on discovered patterns
        
        Args:
            data_patterns: Patterns discovered from data analysis
            data_dir: Directory containing the data
            use_case_description: User's description of their use case
            
        Returns:
            Generated SOURCE_ANALYSIS.md content
        """
        logger.info("🎯 Generating contextual SOURCE_ANALYSIS.md")
        
        # Create context for LLM generation
        pattern_summary = self._create_pattern_summary(data_patterns)
        
        # Generate contextual analysis
        source_analysis_content = await self._generate_contextual_analysis(
            pattern_summary, data_dir, use_case_description
        )
        
        return source_analysis_content
    
    def _create_pattern_summary(self, data_patterns: Dict[str, List[DataPattern]]) -> str:
        """Create a summary of discovered patterns for LLM context"""
        summary = "DISCOVERED DATA PATTERNS:\\n\\n"
        
        for file_type, patterns in data_patterns.items():
            summary += f"**{file_type.upper()}:**\\n"
            for pattern in patterns:
                summary += f"- Pattern: {pattern.pattern_type}\\n"
                summary += f"  Description: {pattern.description[:100]}...\\n"
                if pattern.examples:
                    summary += f"  Examples: {len(pattern.examples)} found\\n"
                summary += f"  Confidence: {pattern.confidence}\\n\\n"
        
        return summary
    
    async def _generate_contextual_analysis(self, 
                                          pattern_summary: str, 
                                          data_dir: str, 
                                          use_case_description: str) -> str:
        """Generate contextual SOURCE_ANALYSIS.md using LLM"""
        
        prompt = f"""Create a comprehensive SOURCE_ANALYSIS.md template based on the discovered data patterns and use case.

USE CASE CONTEXT:
{use_case_description}

DATA DIRECTORY: {data_dir}

{pattern_summary}

Generate a SOURCE_ANALYSIS.md that:

1. **REFLECTS THE ACTUAL DATA STRUCTURE** - Use real paths and discovered patterns
2. **MATCHES THE USE CASE** - Tailor goals to the specific application context
3. **IS ACTIONABLE** - Provide concrete extraction goals based on what's actually in the data
4. **FOLLOWS THE TEMPLATE FORMAT** - Use the established structure but customize content

Focus on:
- **Realistic paths** based on the data directory structure
- **Specific extraction goals** that match the discovered patterns  
- **Use case relevance** - what knowledge would be valuable for this application
- **Practical outcomes** - what tutorials/guides would be most useful

Generate a complete SOURCE_ANALYSIS.md that someone could immediately use to extract knowledge from this specific dataset.

Format as a complete markdown file ready to use."""
        
        try:
            result = await self.llm_router.analyze_content(
                pattern_summary, ContentType.TEXT, prompt
            )
            
            # Add metadata header
            header = f"""<!--
Auto-generated SOURCE_ANALYSIS.md
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Data directory: {data_dir}
Use case: {use_case_description[:100]}...
-->

"""
            
            return header + result
            
        except Exception as e:
            logger.error(f"Error generating contextual analysis: {e}")
            return self._create_fallback_analysis(data_dir, data_patterns)
    
    def _create_fallback_analysis(self, data_dir: str, data_patterns: Dict[str, List[DataPattern]]) -> str:
        """Create a fallback SOURCE_ANALYSIS.md if LLM generation fails"""
        
        content = f"""# Auto-Generated Source Analysis

*Generated from data pattern discovery*

## CODEBASE TO ANALYZE:

**Primary Data Sources:**
- Main data directory: `{data_dir}`
"""
        
        # Add discovered file types
        for file_type, patterns in data_patterns.items():
            content += f"- {file_type.replace('_', ' ').title()}: `{data_dir}/**/*.{self._get_extension_for_type(file_type)}`\\n"
        
        content += """
## KNOWLEDGE EXTRACTION GOALS:

**Pattern Analysis:**
"""
        
        # Add pattern-based goals
        for file_type, patterns in data_patterns.items():
            content += f"- Extract patterns from {file_type.replace('_', ' ')}\\n"
            for pattern in patterns[:2]:  # Top 2 patterns
                content += f"  - {pattern.description[:80]}...\\n"
        
        content += f"""

## OUTPUT FOCUS:

**Tutorial Style:** How to work with {data_dir} data
**Educational Depth:** Understand data structures and usage patterns
**Practical Examples:** Real data examples and integration patterns

## EXAMPLES TO EXTRACT:

- Data structure understanding
- Integration pattern examples
- Usage workflow guides
- Common data manipulation patterns

## OTHER CONSIDERATIONS:

**Data Type:** Mixed (JSON, documentation, configuration)
**Use Case:** Data analysis and integration
**Complexity Level:** Moderate

---

*Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return content
    
    def _get_extension_for_type(self, file_type: str) -> str:
        """Get file extension for a file type"""
        extension_map = {
            'json_api_docs': 'json',
            'markdown_docs': 'md', 
            'text_docs': 'txt',
            'config_files': 'yaml',
            'other': '*'
        }
        return extension_map.get(file_type, '*')
    
    async def save_generated_analysis(self, content: str, output_path: str = "./intake/auto_generated_analysis.md"):
        """Save the generated SOURCE_ANALYSIS.md to file"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Generated SOURCE_ANALYSIS.md saved to: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error saving generated analysis: {e}")
            raise