"""
Documentation Processor - Extract architectural knowledge from documentation

Processes README files, API docs, architecture documents to understand
system design decisions and implementation approaches.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from .llm_router import LLMRouter, ContentType

logger = logging.getLogger(__name__)

class DocumentationInsight:
    """Represents insights extracted from documentation"""
    def __init__(self, doc_type: str, title: str, content: str, 
                 architectural_insights: List[str], implementation_guidance: List[str],
                 source_file: str):
        self.doc_type = doc_type
        self.title = title
        self.content = content
        self.architectural_insights = architectural_insights
        self.implementation_guidance = implementation_guidance
        self.source_file = source_file

class DocProcessor:
    """Process documentation to extract implementation knowledge"""
    
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        
        # Documentation file patterns
        self.doc_patterns = {
            'readme': ['README.md', 'readme.md', 'README.rst', 'README.txt'],
            'api': ['api.md', 'API.md', 'openapi.yaml', 'swagger.json', 'swagger.yaml'],
            'architecture': ['ARCHITECTURE.md', 'architecture.md', 'DESIGN.md', 'design.md'],
            'setup': ['INSTALL.md', 'SETUP.md', 'setup.md', 'installation.md'],
            'deployment': ['DEPLOY.md', 'deployment.md', 'docker-compose.yml', 'Dockerfile'],
            'contributing': ['CONTRIBUTING.md', 'DEVELOPMENT.md', 'developer.md']
        }
    
    async def extract_documentation_knowledge(self, doc_paths: List[str]) -> Dict[str, List[DocumentationInsight]]:
        """
        Extract knowledge from documentation sources
        
        Args:
            doc_paths: List of documentation directories or files
            
        Returns:
            Dictionary mapping doc types to insights
        """
        logger.info(f"Processing {len(doc_paths)} documentation paths")
        
        # Find all documentation files
        all_docs = []
        for path in doc_paths:
            all_docs.extend(self._find_documentation_files(path))
        
        logger.info(f"Found {len(all_docs)} documentation files")
        
        # Group by document type
        doc_groups = self._group_docs_by_type(all_docs)
        
        # Extract insights from each group
        results = {}
        for doc_type, files in doc_groups.items():
            logger.info(f"Processing {doc_type} documentation")
            insights = await self._extract_doc_type_insights(doc_type, files)
            if insights:
                results[doc_type] = insights
        
        return results
    
    def _find_documentation_files(self, path: str) -> List[str]:
        """Find documentation files in a path"""
        path_obj = Path(path)
        files = []
        
        if path_obj.is_file():
            if self._is_documentation_file(path_obj):
                files.append(str(path_obj))
        elif path_obj.is_dir():
            # Look for common documentation files
            for patterns in self.doc_patterns.values():
                for pattern in patterns:
                    if '*' in pattern:
                        files.extend([str(f) for f in path_obj.rglob(pattern)])
                    else:
                        file_path = path_obj / pattern
                        if file_path.exists():
                            files.append(str(file_path))
            
            # Also look for .md files in docs directories
            if 'doc' in str(path_obj).lower():
                files.extend([str(f) for f in path_obj.rglob('*.md')])
        
        return files
    
    def _is_documentation_file(self, file_path: Path) -> bool:
        """Check if a file is documentation"""
        filename = file_path.name.lower()
        
        # Check against known patterns
        for patterns in self.doc_patterns.values():
            for pattern in patterns:
                if pattern.lower() == filename:
                    return True
        
        # Check extensions
        doc_extensions = ['.md', '.rst', '.txt', '.yaml', '.yml', '.json']
        return file_path.suffix.lower() in doc_extensions
    
    def _group_docs_by_type(self, files: List[str]) -> Dict[str, List[str]]:
        """Group documentation files by type"""
        groups = {}
        
        for file_path in files:
            doc_type = self._identify_doc_type(file_path)
            
            if doc_type not in groups:
                groups[doc_type] = []
            groups[doc_type].append(file_path)
        
        return groups
    
    def _identify_doc_type(self, file_path: str) -> str:
        """Identify the type of documentation"""
        filename = Path(file_path).name.lower()
        
        # Check against known patterns
        for doc_type, patterns in self.doc_patterns.items():
            for pattern in patterns:
                if pattern.lower() == filename or pattern.lower() in filename:
                    return doc_type
        
        # Check path for clues
        path_lower = str(file_path).lower()
        if 'api' in path_lower:
            return 'api'
        elif 'setup' in path_lower or 'install' in path_lower:
            return 'setup'
        elif 'deploy' in path_lower:
            return 'deployment'
        elif 'arch' in path_lower or 'design' in path_lower:
            return 'architecture'
        
        return 'general'
    
    async def _extract_doc_type_insights(self, doc_type: str, files: List[str]) -> List[DocumentationInsight]:
        """Extract insights from a specific type of documentation"""
        insights = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if len(content.strip()) < 50:  # Skip very small files
                    continue
                
                # Extract insights from this document
                insight = await self._analyze_document(file_path, content, doc_type)
                if insight:
                    insights.append(insight)
                    
            except Exception as e:
                logger.warning(f"Could not analyze document {file_path}: {e}")
        
        return insights
    
    async def _analyze_document(self, file_path: str, content: str, doc_type: str) -> Optional[DocumentationInsight]:
        """Analyze a single document for implementation insights"""
        
        prompt = self._get_analysis_prompt(doc_type)
        
        try:
            result = await self.llm_router.analyze_content(
                content, ContentType.DOCUMENTATION, prompt
            )
            
            # Parse the analysis
            return self._parse_document_analysis(result, file_path, doc_type)
            
        except Exception as e:
            logger.error(f"Error analyzing document {file_path}: {e}")
            return None
    
    def _get_analysis_prompt(self, doc_type: str) -> str:
        """Get analysis prompt based on document type"""
        
        base_prompt = """Analyze this documentation and extract insights that would help someone build a similar system. Focus on:

1. **Architectural Insights**: What architectural decisions were made and why?
2. **Implementation Guidance**: How should someone approach building similar functionality?
3. **Key Concepts**: What are the important concepts and patterns?
4. **Dependencies and Integrations**: What external systems or libraries are used?
5. **Configuration and Setup**: How is the system configured and deployed?

Provide practical insights that would guide implementation decisions."""
        
        specific_prompts = {
            'readme': """
This is a README file. Extract:
- Project architecture and structure
- Key features and how they work
- Technology stack and dependencies
- Setup and running instructions
- Usage patterns and examples
""",
            'api': """
This is API documentation. Extract:
- API design patterns and conventions
- Authentication and authorization approaches
- Request/response structures
- Error handling strategies
- Rate limiting and security measures
""",
            'architecture': """
This is architecture documentation. Extract:
- System design decisions and rationale
- Component interactions and data flow
- Scalability and performance considerations
- Security architecture patterns
- Integration points and external dependencies
""",
            'setup': """
This is setup/installation documentation. Extract:
- Infrastructure requirements
- Configuration management approaches
- Deployment strategies and patterns
- Environment setup procedures
- Common setup issues and solutions
""",
            'deployment': """
This is deployment documentation. Extract:
- Deployment architecture and strategies
- Infrastructure as code patterns
- Container and orchestration setup
- CI/CD pipeline approaches
- Monitoring and logging setup
"""
        }
        
        specific = specific_prompts.get(doc_type, "")
        return base_prompt + specific
    
    def _parse_document_analysis(self, analysis: str, file_path: str, doc_type: str) -> DocumentationInsight:
        """Parse LLM analysis into DocumentationInsight"""
        
        # Extract title from file or analysis
        title = Path(file_path).stem
        if '# ' in analysis:
            title_line = [line for line in analysis.split('\n') if line.strip().startswith('# ')]
            if title_line:
                title = title_line[0].replace('# ', '').strip()
        
        # Extract architectural insights
        architectural_insights = []
        implementation_guidance = []
        
        lines = analysis.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify sections
            if 'architectural insights' in line.lower():
                current_section = 'architectural'
            elif 'implementation guidance' in line.lower():
                current_section = 'implementation'
            elif line.startswith('- ') or line.startswith('* '):
                # This is a bullet point
                point = line[2:].strip()
                if current_section == 'architectural':
                    architectural_insights.append(point)
                elif current_section == 'implementation':
                    implementation_guidance.append(point)
        
        # If no structured sections found, try to extract general insights
        if not architectural_insights and not implementation_guidance:
            # Look for any bullet points as general insights
            for line in lines:
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    point = line[2:].strip()
                    if 'architecture' in point.lower() or 'design' in point.lower():
                        architectural_insights.append(point)
                    else:
                        implementation_guidance.append(point)
        
        return DocumentationInsight(
            doc_type=doc_type,
            title=title,
            content=analysis,
            architectural_insights=architectural_insights,
            implementation_guidance=implementation_guidance,
            source_file=file_path
        )