"""
Tutorial Generator - Create comprehensive "How to Build X" guides

Generates educational .md files that teach others how to implement similar systems
based on extracted knowledge from real codebases.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ..extractors.code_analyzer import CodePattern
from ..extractors.doc_processor import DocumentationInsight
from ..extractors.multimodal_processor import MultimodalInsight

logger = logging.getLogger(__name__)

class TutorialGuide:
    """Represents a generated tutorial guide"""
    def __init__(self, title: str, filename: str, content: str, tutorial_type: str):
        self.title = title
        self.filename = filename
        self.content = content
        self.tutorial_type = tutorial_type

class TutorialGenerator:
    """Generate comprehensive tutorial guides from extracted knowledge"""
    
    def __init__(self, output_dir: str = "./knowledge_library"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.how_to_build_dir = self.output_dir / "how_to_build"
        self.patterns_dir = self.output_dir / "patterns"
        self.architecture_dir = self.output_dir / "architecture"
        self.gotchas_dir = self.output_dir / "gotchas"
        
        for dir_path in [self.how_to_build_dir, self.patterns_dir, self.architecture_dir, self.gotchas_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    async def generate_all_tutorials(self, 
                                   code_patterns: Dict[str, List[CodePattern]],
                                   doc_insights: Dict[str, List[DocumentationInsight]],
                                   multimodal_insights: Dict[str, List[MultimodalInsight]]) -> List[TutorialGuide]:
        """
        Generate all tutorial guides from extracted knowledge
        
        Args:
            code_patterns: Patterns extracted from code analysis
            doc_insights: Insights from documentation processing
            multimodal_insights: Insights from images, PDFs, logs
            
        Returns:
            List of generated tutorial guides
        """
        logger.info("Generating comprehensive tutorial guides")
        
        generated_guides = []
        
        # Generate "How to Build" guides for each major feature/system
        for feature_name, patterns in code_patterns.items():
            guide = await self._generate_how_to_build_guide(feature_name, patterns, doc_insights, multimodal_insights)
            if guide:
                generated_guides.append(guide)
                await self._write_guide_to_file(guide, self.how_to_build_dir)
        
        # Generate pattern documentation
        for feature_name, patterns in code_patterns.items():
            for pattern in patterns:
                guide = await self._generate_pattern_guide(pattern, feature_name)
                if guide:
                    generated_guides.append(guide)
                    await self._write_guide_to_file(guide, self.patterns_dir)
        
        # Generate architecture guides from documentation
        for doc_type, insights in doc_insights.items():
            if doc_type in ['architecture', 'readme']:
                guide = await self._generate_architecture_guide(doc_type, insights)
                if guide:
                    generated_guides.append(guide)
                    await self._write_guide_to_file(guide, self.architecture_dir)
        
        # Generate gotcha guides from all sources
        gotcha_guide = await self._generate_gotcha_guide(code_patterns, doc_insights, multimodal_insights)
        if gotcha_guide:
            generated_guides.append(gotcha_guide)
            await self._write_guide_to_file(gotcha_guide, self.gotchas_dir)
        
        logger.info(f"Generated {len(generated_guides)} tutorial guides")
        return generated_guides
    
    async def _generate_how_to_build_guide(self, 
                                         feature_name: str, 
                                         patterns: List[CodePattern],
                                         doc_insights: Dict[str, List[DocumentationInsight]],
                                         multimodal_insights: Dict[str, List[MultimodalInsight]]) -> Optional[TutorialGuide]:
        """Generate a comprehensive 'How to Build X' guide"""
        
        if not patterns:
            return None
        
        # Collect related insights from other sources
        related_docs = self._find_related_documentation(feature_name, doc_insights)
        related_multimodal = self._find_related_multimodal(feature_name, multimodal_insights)
        
        # Generate comprehensive guide content
        content = self._create_how_to_build_content(feature_name, patterns, related_docs, related_multimodal)
        
        # Create safe filename
        safe_name = feature_name.lower().replace(' ', '_').replace('-', '_')
        filename = f"how_to_build_{safe_name}.md"
        
        return TutorialGuide(
            title=f"How to Build {feature_name.replace('_', ' ').title()}",
            filename=filename,
            content=content,
            tutorial_type="how_to_build"
        )
    
    def _create_how_to_build_content(self, 
                                   feature_name: str, 
                                   patterns: List[CodePattern],
                                   related_docs: List[DocumentationInsight],
                                   related_multimodal: List[MultimodalInsight]) -> str:
        """Create comprehensive how-to-build content"""
        
        title = f"How to Build {feature_name.replace('_', ' ').title()}"
        
        content = f"""# {title}

*Generated from real implementation analysis*

## Overview

This guide shows you how to build a {feature_name.replace('_', ' ')} system based on analysis of a real, working implementation. It includes architectural decisions, step-by-step implementation, common pitfalls, and best practices.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Implementation](#step-by-step-implementation)
4. [Key Implementation Patterns](#key-implementation-patterns)
5. [Common Pitfalls to Avoid](#common-pitfalls-to-avoid)
6. [Testing Strategy](#testing-strategy)
7. [Deployment Considerations](#deployment-considerations)
8. [Further Reading](#further-reading)

## System Architecture

"""
        
        # Add architectural insights from documentation
        if related_docs:
            content += "### Design Decisions\n\n"
            for doc in related_docs:
                if doc.architectural_insights:
                    content += f"**From {doc.title}:**\n"
                    for insight in doc.architectural_insights[:3]:  # Top 3 insights
                        content += f"- {insight}\n"
                    content += "\n"
        
        # Add visual architecture if available
        for multimodal in related_multimodal:
            if multimodal.content_type == 'image' and multimodal.insights:
                content += f"### Visual Architecture Insights\n\n"
                content += f"*From {multimodal.title}:*\n"
                for insight in multimodal.insights[:2]:
                    content += f"- {insight}\n"
                content += "\n"
                break
        
        content += """## Prerequisites

Before implementing this system, ensure you have:

### Technical Requirements
"""
        
        # Extract technology requirements from patterns
        technologies = set()
        for pattern in patterns:
            # Try to identify technologies from code examples or file paths
            if '.py' in pattern.file_path:
                technologies.add('Python')
            elif '.js' in pattern.file_path or '.ts' in pattern.file_path:
                technologies.add('JavaScript/TypeScript')
            elif '.java' in pattern.file_path:
                technologies.add('Java')
        
        for tech in sorted(technologies):
            content += f"- {tech} development environment\n"
        
        content += """
### Knowledge Prerequisites
- Understanding of web application architecture
- Basic knowledge of databases and APIs
- Familiarity with the chosen technology stack

## Step-by-Step Implementation

"""
        
        # Generate implementation steps from patterns
        for i, pattern in enumerate(patterns[:5], 1):  # Top 5 patterns
            content += f"### Step {i}: {pattern.name}\n\n"
            content += f"{pattern.description}\n\n"
            
            if pattern.implementation_guide:
                content += "**Implementation Approach:**\n"
                # Extract implementation guidance from the pattern
                guide_lines = pattern.implementation_guide.split('\n')
                for line in guide_lines[:10]:  # First 10 lines
                    if line.strip() and not line.strip().startswith('#'):
                        content += f"- {line.strip()}\n"
                content += "\n"
            
            if pattern.code_example and len(pattern.code_example.strip()) > 20:
                content += "**Code Example:**\n\n"
                content += f"```python\n{pattern.code_example}\n```\n\n"
        
        content += """## Key Implementation Patterns

The following patterns were identified in the analyzed system:

"""
        
        # Document key patterns
        for pattern in patterns:
            content += f"### {pattern.name}\n\n"
            content += f"**Purpose:** {pattern.description}\n\n"
            content += f"**Implementation Location:** `{Path(pattern.file_path).name}`\n\n"
            
            if pattern.implementation_guide:
                # Extract key guidance points
                guide_lines = [line.strip() for line in pattern.implementation_guide.split('\n') 
                              if line.strip() and not line.startswith('#')]
                if guide_lines:
                    content += "**Key Points:**\n"
                    for line in guide_lines[:3]:  # Top 3 points
                        content += f"- {line}\n"
                    content += "\n"
        
        content += """## Common Pitfalls to Avoid

Based on analysis of the real implementation, here are common issues to watch out for:

"""
        
        # Add gotchas from multimodal sources (especially logs)
        for multimodal in related_multimodal:
            if multimodal.gotchas:
                content += f"### Issues from {multimodal.content_type.title()} Analysis\n\n"
                for gotcha in multimodal.gotchas[:3]:  # Top 3 gotchas
                    content += f"- **{gotcha}**\n"
                content += "\n"
        
        # Add implementation guidance from docs
        for doc in related_docs:
            if doc.implementation_guidance:
                content += f"### Guidance from {doc.title}\n\n"
                for guidance in doc.implementation_guidance[:3]:
                    content += f"- {guidance}\n"
                content += "\n"
        
        content += """## Testing Strategy

Implement comprehensive testing to ensure system reliability:

### Unit Testing
- Test individual components and functions
- Mock external dependencies
- Aim for 80%+ code coverage

### Integration Testing
- Test component interactions
- Verify database operations
- Test API endpoints end-to-end

### Performance Testing
- Load test critical paths
- Monitor memory usage
- Benchmark response times

## Deployment Considerations

### Infrastructure Requirements
"""
        
        # Add deployment insights from documentation
        deployment_docs = [doc for doc in related_docs if doc.doc_type in ['deployment', 'setup']]
        if deployment_docs:
            for doc in deployment_docs:
                if doc.implementation_guidance:
                    for guidance in doc.implementation_guidance:
                        content += f"- {guidance}\n"
        else:
            content += """- Consider containerization (Docker)
- Set up proper logging and monitoring
- Configure environment-specific settings
- Plan for scalability and load balancing
"""
        
        content += """
### Security Considerations
- Implement proper authentication and authorization
- Validate and sanitize all inputs
- Use HTTPS for all communications
- Regular security audits and updates

## Further Reading

### Related Patterns
"""
        
        # Link to related pattern files
        for pattern in patterns:
            safe_pattern_name = pattern.name.lower().replace(' ', '_').replace('-', '_')
            content += f"- [{pattern.name}](../patterns/{safe_pattern_name}.md)\n"
        
        content += f"""
### Architecture Documentation
- [System Architecture Overview](../architecture/system_overview.md)
- [Common Gotchas](../gotchas/common_pitfalls.md)

---

*This guide was generated from analysis of a real {feature_name.replace('_', ' ')} implementation. The patterns and approaches described here have been proven to work in production environments.*

**Generated on:** {datetime.now().strftime('%Y-%m-%d')}
"""
        
        return content
    
    async def _generate_pattern_guide(self, pattern: CodePattern, feature_name: str) -> Optional[TutorialGuide]:
        """Generate a detailed pattern guide"""
        
        safe_name = pattern.name.lower().replace(' ', '_').replace('-', '_')
        filename = f"{safe_name}.md"
        
        content = f"""# {pattern.name}

*Implementation pattern from {feature_name.replace('_', ' ')} system*

## Overview

{pattern.description}

## When to Use This Pattern

This pattern is useful when you need to:
- Implement similar functionality to {feature_name.replace('_', ' ')}
- Follow established architectural patterns
- Ensure consistent implementation approaches

## Implementation Guide

{pattern.implementation_guide}

## Code Example

```python
{pattern.code_example}
```

## Key Benefits

- **Reusability**: This pattern can be adapted for similar use cases  
- **Maintainability**: Follows established conventions
- **Reliability**: Based on proven, working implementation

## Variations

Consider these variations based on your specific needs:
- Adapt the pattern for different programming languages
- Modify for different scale requirements
- Integrate with different frameworks or libraries

## Testing This Pattern

When implementing this pattern, ensure you test:
- Core functionality works as expected
- Error cases are handled properly
- Performance meets requirements
- Integration with other components is seamless

## Related Patterns

This pattern works well with other patterns from the {feature_name.replace('_', ' ')} system.

---

*Extracted from: `{Path(pattern.file_path).name}`*
*Generated on: {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        return TutorialGuide(
            title=pattern.name,
            filename=filename,
            content=content,
            tutorial_type="pattern"
        )
    
    async def _generate_architecture_guide(self, doc_type: str, insights: List[DocumentationInsight]) -> Optional[TutorialGuide]:
        """Generate architecture guide from documentation insights"""
        
        if not insights:
            return None
        
        filename = f"{doc_type}_architecture.md"
        title = f"{doc_type.replace('_', ' ').title()} Architecture Guide"
        
        content = f"""# {title}

*Architectural insights extracted from documentation analysis*

## Overview

This guide documents the architectural decisions and design patterns identified in the system documentation.

"""
        
        for insight in insights:
            content += f"## {insight.title}\n\n"
            
            if insight.architectural_insights:
                content += "### Architectural Decisions\n\n"
                for arch_insight in insight.architectural_insights:
                    content += f"- {arch_insight}\n"
                content += "\n"
            
            if insight.implementation_guidance:
                content += "### Implementation Guidance\n\n"
                for guidance in insight.implementation_guidance:
                    content += f"- {guidance}\n"
                content += "\n"
        
        content += f"""
---

*Generated from {len(insights)} documentation sources*
*Generated on: {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        return TutorialGuide(
            title=title,
            filename=filename,
            content=content,
            tutorial_type="architecture"
        )
    
    async def _generate_gotcha_guide(self, 
                                   code_patterns: Dict[str, List[CodePattern]],
                                   doc_insights: Dict[str, List[DocumentationInsight]],
                                   multimodal_insights: Dict[str, List[MultimodalInsight]]) -> Optional[TutorialGuide]:
        """Generate comprehensive gotcha guide from all sources"""
        
        filename = "common_pitfalls.md"
        title = "Common Pitfalls and Gotchas"
        
        content = f"""# {title}

*Pitfalls and gotchas identified from real system analysis*

## Overview

This guide documents common pitfalls, gotchas, and issues identified through analysis of real implementations. Use this to avoid common mistakes when building similar systems.

"""
        
        # Add gotchas from multimodal sources (especially logs)
        log_gotchas = []
        for content_type, insights in multimodal_insights.items():
            if content_type == 'logs':
                for insight in insights:
                    log_gotchas.extend(insight.gotchas)
        
        if log_gotchas:
            content += "## Production Issues (From Log Analysis)\n\n"
            for i, gotcha in enumerate(log_gotchas[:10], 1):
                content += f"### {i}. {gotcha}\n\n"
                content += "**How to avoid:** Implement proper error handling and monitoring for this scenario.\n\n"
        
        # Add gotchas from other multimodal sources
        other_gotchas = []
        for content_type, insights in multimodal_insights.items():
            if content_type != 'logs':
                for insight in insights:
                    other_gotchas.extend(insight.gotchas)
        
        if other_gotchas:
            content += "## Implementation Gotchas\n\n"
            for gotcha in other_gotchas[:5]:
                content += f"- **{gotcha}**\n"
            content += "\n"
        
        content += """## General Best Practices

Based on the analysis, follow these best practices to avoid common issues:

### Error Handling
- Always implement comprehensive error handling
- Log errors with sufficient context for debugging
- Provide meaningful error messages to users

### Performance
- Monitor system performance in production
- Implement proper caching strategies
- Optimize database queries and API calls

### Security
- Validate all user inputs
- Implement proper authentication and authorization
- Keep dependencies updated and secure

### Testing
- Write comprehensive tests for all functionality
- Test error scenarios and edge cases
- Implement automated testing in CI/CD pipeline

### Monitoring
- Set up proper logging and monitoring
- Implement health checks and alerts
- Monitor key business metrics

---

*Generated from analysis of logs, documentation, and code patterns*
*Generated on: {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        return TutorialGuide(
            title=title,
            filename=filename,
            content=content,
            tutorial_type="gotchas"
        )
    
    def _find_related_documentation(self, feature_name: str, doc_insights: Dict[str, List[DocumentationInsight]]) -> List[DocumentationInsight]:
        """Find documentation insights related to a feature"""
        related = []
        feature_keywords = feature_name.lower().split('_')
        
        for doc_type, insights in doc_insights.items():
            for insight in insights:
                # Check if insight is related to the feature
                insight_text = (insight.title + ' ' + insight.content).lower()
                if any(keyword in insight_text for keyword in feature_keywords):
                    related.append(insight)
        
        return related
    
    def _find_related_multimodal(self, feature_name: str, multimodal_insights: Dict[str, List[MultimodalInsight]]) -> List[MultimodalInsight]:
        """Find multimodal insights related to a feature"""
        related = []
        feature_keywords = feature_name.lower().split('_')
        
        for content_type, insights in multimodal_insights.items():
            for insight in insights:
                # Check if insight is related to the feature
                all_insights_text = ' '.join(insight.insights + insight.implementation_notes).lower()
                if any(keyword in all_insights_text for keyword in feature_keywords):
                    related.append(insight)
        
        return related
    
    async def _write_guide_to_file(self, guide: TutorialGuide, output_dir: Path):
        """Write a tutorial guide to file"""
        try:
            output_path = output_dir / guide.filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(guide.content)
            
            logger.info(f"Generated tutorial: {output_path}")
            
        except Exception as e:
            logger.error(f"Error writing guide {guide.filename}: {e}")
            raise